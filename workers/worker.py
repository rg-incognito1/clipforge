"""
ClipForge Worker — polls Redis job queue and runs the full video pipeline.

Flow: QUEUED → TRANSCRIBING → ANALYZING → PROCESSING → COMPLETE
"""
import os
import sys
import time
import logging

import redis
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

BACKEND_URL   = os.getenv("BACKEND_URL",   "http://localhost:8080")
REDIS_URL     = os.getenv("REDIS_URL",     "redis://localhost:6379")
STORAGE_PATH  = os.getenv("STORAGE_PATH",  "/storage")
GEMINI_KEY    = os.getenv("GEMINI_API_KEY", "")
HF_TOKEN      = os.getenv("HF_TOKEN",      "")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
QUEUE_KEY     = "clipforge:job_queue"


def _update_status(job_id, status, error=None):
    body = {"status": status}
    if error:
        body["errorMessage"] = str(error)[:2000]
    try:
        requests.post(f"{BACKEND_URL}/internal/jobs/{job_id}/status", json=body, timeout=15)
        log.info(f"[{job_id[:8]}] → {status}")
    except Exception as e:
        log.error(f"[{job_id[:8]}] Failed to update status: {e}")


def _report_clip(job_id, clip_data):
    try:
        r = requests.post(f"{BACKEND_URL}/internal/jobs/{job_id}/clips", json=clip_data, timeout=15)
        return r.json().get("clipId")
    except Exception as e:
        log.error(f"[{job_id[:8]}] Failed to report clip: {e}")
        return None


def _get_job(job_id):
    r = requests.get(f"{BACKEND_URL}/internal/jobs/{job_id}", timeout=15)
    r.raise_for_status()
    return r.json()


def _wait_for_backend(retries=30, delay=3):
    for i in range(retries):
        try:
            requests.get(f"{BACKEND_URL}/api/jobs", timeout=5)
            log.info("Backend is ready")
            return
        except Exception:
            log.info(f"Waiting for backend... ({i+1}/{retries})")
            time.sleep(delay)
    raise RuntimeError("Backend did not become ready in time")


def process_job(job_id):
    from transcriber import transcribe_video
    from analyzer import analyze_transcript
    from clipper import create_story_short

    log.info(f"[{job_id[:8]}] Starting job")
    job = _get_job(job_id)

    video_path = job["videoPath"]
    recipe     = job.get("recipe", "mrbeast")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    # ── Step 1: Transcribe ───────────────────────────────────────────────────
    _update_status(job_id, "TRANSCRIBING")
    log.info(f"[{job_id[:8]}] Transcribing with Whisper ({WHISPER_MODEL})...")
    segments, words = transcribe_video(video_path, WHISPER_MODEL)
    log.info(f"[{job_id[:8]}] {len(segments)} segments, {len(words)} words")

    if not segments:
        raise ValueError("No speech detected in video")

    # ── Step 2: Analyze ──────────────────────────────────────────────────────
    _update_status(job_id, "ANALYZING")
    log.info(f"[{job_id[:8]}] Analyzing with Gemini...")
    analysis = analyze_transcript(segments, GEMINI_KEY)
    clips_found = analysis.get("clips", [])
    log.info(f"[{job_id[:8]}] Found {len(clips_found)} candidate clips")

    if not clips_found:
        raise ValueError("No viral moments found in video")

    # ── Step 3: Diarization pipeline (optional) ──────────────────────────────
    diarization_pipeline = None
    if HF_TOKEN:
        try:
            from reframer import load_diarization_pipeline
            diarization_pipeline = load_diarization_pipeline(HF_TOKEN)
        except Exception as e:
            log.warning(f"[{job_id[:8]}] Diarization skipped: {e}")

    # ── Step 4: Process each clip ────────────────────────────────────────────
    _update_status(job_id, "PROCESSING")
    output_dir = os.path.join(STORAGE_PATH, "clips", job_id)
    os.makedirs(output_dir, exist_ok=True)

    processed = 0
    for i, clip_info in enumerate(clips_found):
        log.info(
            f"[{job_id[:8]}] Clip {i+1}/{len(clips_found)}: "
            f"{clip_info.get('storyline_title', 'untitled')} "
            f"(score={clip_info.get('viral_score', '?')})"
        )

        story = {
            "clips": [clip_info],
            "storyline_title": clip_info.get("storyline_title", f"clip_{i+1:02d}"),
            "storyline_summary": clip_info.get("storyline_summary", ""),
            "score": clip_info.get("viral_score", 7),
        }

        try:
            out_path = create_story_short(
                video_path, story, output_dir,
                f"{job_id[:8]}_c{i+1:02d}",
                pipeline=diarization_pipeline,
                all_words=words,
                recipe=recipe,
            )

            if out_path and os.path.exists(out_path):
                _report_clip(job_id, {
                    "startSeconds":     clip_info["start_seconds"],
                    "endSeconds":       clip_info["end_seconds"],
                    "duration":         clip_info["end_seconds"] - clip_info["start_seconds"],
                    "momentType":       clip_info.get("moment_type", "viral"),
                    "viralScore":       clip_info.get("viral_score", 7) * 10,
                    "outputPath":       out_path,
                    "storylineTitle":   clip_info.get("storyline_title", ""),
                    "storylineSummary": clip_info.get("storyline_summary", ""),
                })
                processed += 1

        except Exception as e:
            log.error(f"[{job_id[:8]}] Clip {i+1} failed: {e}")

    if processed == 0:
        raise RuntimeError("All clip renders failed")

    _update_status(job_id, "COMPLETE")
    log.info(f"[{job_id[:8]}] Done — {processed}/{len(clips_found)} clips rendered")


def main():
    log.info(f"ClipForge Worker v0.1 | Backend: {BACKEND_URL} | Model: {WHISPER_MODEL}")

    _wait_for_backend()

    rdb = redis.from_url(REDIS_URL, decode_responses=True)

    while True:
        try:
            result = rdb.brpop(QUEUE_KEY, timeout=30)
            if result is None:
                continue

            _, job_id = result
            log.info(f"Dequeued: {job_id}")

            try:
                process_job(job_id)
            except Exception as e:
                log.exception(f"Job {job_id} failed: {e}")
                _update_status(job_id, "FAILED", str(e))

        except redis.RedisError as e:
            log.error(f"Redis error: {e}")
            time.sleep(5)
        except KeyboardInterrupt:
            log.info("Worker shutting down")
            break
        except Exception as e:
            log.exception(f"Worker error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
