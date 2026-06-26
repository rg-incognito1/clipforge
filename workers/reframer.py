"""
Speaker-aware 9:16 reframing — adapted from shortGen_HIMYM.

Pipeline:
  1. pyannote.audio  — who speaks when (optional, needs HF_TOKEN)
  2. MediaPipe FaceMesh — face positions + lip openness per sampled frame
  3. Smooth exponential crop — pans to the speaking face
  4. ffmpeg pipe — renders blurred-bg + sharp fg at 1080x1920
"""
import os
import subprocess
import tempfile
import numpy as np
import cv2
import mediapipe as mp

_mp_face_mesh = mp.solutions.face_mesh

_OUT_W, _OUT_H = 1080, 1920
_SAMPLE_FPS   = 3
_SMOOTH_ALPHA = 0.03

_NOSE_TIP = 1
_LIP_TOP  = 13
_LIP_BOT  = 14
_FACE_TOP = 10
_FACE_BOT = 152


def load_diarization_pipeline(hf_token: str):
    from pyannote.audio import Pipeline
    print('  Loading pyannote diarization model...')
    pipe = Pipeline.from_pretrained('pyannote/speaker-diarization-3.1')
    return pipe


def _extract_wav(video_path, start_sec, end_sec, wav_path):
    subprocess.run([
        'ffmpeg', '-y',
        '-ss', str(start_sec), '-to', str(end_sec),
        '-i', video_path,
        '-vn', '-ar', '16000', '-ac', '1', wav_path,
    ], check=True, capture_output=True)


def _speech_frames(pipeline, wav_path, src_fps) -> set:
    result = pipeline(wav_path)
    frames = set()
    for seg, _, _ in result.itertracks(yield_label=True):
        for fi in range(int(seg.start * src_fps), int(seg.end * src_fps) + 1):
            frames.add(fi)
    return frames


def _sample_faces(video_path, start_sec, end_sec, src_fps) -> dict:
    step = max(1, round(src_fps / _SAMPLE_FPS))
    start_f = int(start_sec * src_fps)
    end_f   = int(end_sec   * src_fps)

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_f)

    face_mesh = _mp_face_mesh.FaceMesh(
        max_num_faces=6,
        refine_landmarks=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    data = {}
    for fi in range(end_f - start_f):
        ret, frame = cap.read()
        if not ret:
            break
        if fi % step != 0:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = face_mesh.process(rgb)
        faces = []
        if res.multi_face_landmarks:
            for lm in res.multi_face_landmarks:
                pts = lm.landmark
                cx       = pts[_NOSE_TIP].x
                lip_open = abs(pts[_LIP_BOT].y - pts[_LIP_TOP].y)
                face_h   = abs(pts[_FACE_BOT].y - pts[_FACE_TOP].y) or 0.1
                faces.append((cx, lip_open / face_h))
        data[fi] = faces

    cap.release()
    face_mesh.close()
    return data


def _build_cx_timeline(frame_data, speech_frames, total_frames, src_w) -> list:
    sampled = sorted(frame_data.keys())
    cx_at   = {}
    last_cx = src_w / 2.0

    for fi in sampled:
        faces = frame_data[fi]
        if not faces:
            cx_at[fi] = last_cx
            continue
        best = max(faces, key=lambda f: f[1]) if fi in speech_frames else faces[0]
        last_cx   = best[0] * src_w
        cx_at[fi] = last_cx

    result = []
    for i in range(total_frames):
        if not sampled or i <= sampled[0]:
            result.append(cx_at.get(sampled[0] if sampled else 0, src_w / 2))
        elif i >= sampled[-1]:
            result.append(cx_at[sampled[-1]])
        else:
            lo = max(f for f in sampled if f <= i)
            hi = min(f for f in sampled if f >= i)
            t  = (i - lo) / (hi - lo) if hi != lo else 0
            result.append(cx_at[lo] * (1 - t) + cx_at[hi] * t)
    return result


def _smooth(values, alpha):
    out = list(values)
    for i in range(1, len(out)):
        out[i] = alpha * out[i] + (1 - alpha) * out[i - 1]
    return out


def reframe_clip(video_path: str, start_sec: float, end_sec: float,
                 output_path: str, pipeline=None) -> None:
    cap = cv2.VideoCapture(video_path)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    src_w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    start_f      = int(start_sec * src_fps)
    total_frames = int((end_sec - start_sec) * src_fps)
    crop_w       = min(int(src_h * 9 / 16), src_w)

    speech_frames: set = set()
    if pipeline is not None:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            wav_tmp = f.name
        try:
            _extract_wav(video_path, start_sec, end_sec, wav_tmp)
            speech_frames = _speech_frames(pipeline, wav_tmp, src_fps)
        except Exception as exc:
            print(f'    Diarization skipped: {exc}')
        finally:
            os.unlink(wav_tmp)

    print('    Detecting faces + lip movement...')
    frame_data = _sample_faces(video_path, start_sec, end_sec, src_fps)

    crop_cx = _build_cx_timeline(frame_data, speech_frames, total_frames, src_w)
    crop_cx = _smooth(crop_cx, _SMOOTH_ALPHA)
    half    = crop_w / 2
    crop_cx = [max(half, min(src_w - half, cx)) for cx in crop_cx]

    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{_OUT_W}x{_OUT_H}', '-pix_fmt', 'bgr24',
        '-r', str(src_fps),
        '-i', 'pipe:0',
        '-ss', str(start_sec), '-to', str(end_sec), '-i', video_path,
        '-map', '0:v', '-map', '1:a?',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
        '-c:a', 'aac', '-b:a', '128k',
        '-shortest', output_path,
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_f)

    for fi in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break

        cx = int(crop_cx[fi])
        x1 = max(0, min(cx - crop_w // 2, src_w - crop_w))

        bg = cv2.GaussianBlur(frame, (45, 45), 0)
        bg = cv2.resize(bg, (_OUT_W, _OUT_H), interpolation=cv2.INTER_LINEAR)
        fg = cv2.resize(frame[:, x1:x1 + crop_w], (_OUT_W, _OUT_H),
                        interpolation=cv2.INTER_LANCZOS4)

        proc.stdin.write(fg.tobytes())

    cap.release()
    try:
        proc.stdin.close()
    except BrokenPipeError:
        pass
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f'reframe_clip ffmpeg failed for {output_path}')
