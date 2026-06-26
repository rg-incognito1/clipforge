# ClipForge MVP

AI-powered video editor SDK + SaaS. Upload any long-form video → AI finds viral moments → auto-crops to 9:16 → burns styled captions → delivers ready-to-post shorts.

## Stack

| Layer | Tech |
|---|---|
| Backend API | Spring Boot 3.3 + PostgreSQL + Redis |
| AI Workers | Python 3.11 · Whisper · Gemini 2.5 Flash · MediaPipe · FFmpeg |
| Frontend | Next.js 15 · TypeScript · Tailwind |
| Infrastructure | Docker Compose |

## Quick Start

### 1. Copy env file
```bash
cp .env.example .env
# Fill in GEMINI_API_KEY (required) — free at https://aistudio.google.com/app/apikey
# HF_TOKEN is optional — enables speaker diarization (better multi-speaker crop)
```

### 2. Run everything
```bash
docker compose up --build
```

Frontend: http://localhost:3000  
Backend API: http://localhost:8080

### 3. First run takes a while
The worker Docker image downloads PyTorch CPU + Whisper + MediaPipe.  
After the first `docker compose build`, subsequent starts are fast.

---

## Architecture

```
Browser  →  Next.js (3000)  →  Spring Boot (8080)  →  Redis queue
                                     ↓
                              PostgreSQL (jobs/clips)
                                     ↑
                           Python Worker ←── Redis queue
                                     │
                              FFmpeg + Whisper + Claude + MediaPipe
                                     │
                              /storage/clips/{jobId}/
```

**Flow:**
1. User uploads video → Spring Boot saves to `/storage/uploads/{jobId}/`
2. Job ID pushed to Redis list `clipforge:job_queue`
3. Python worker pops job → transcribes (Whisper) → analyzes (Claude) → reframes (MediaPipe+FFmpeg) → burns captions
4. Worker reports clip paths back to Spring Boot via `/internal/jobs/{id}/clips`
5. Frontend polls `/api/jobs/{id}` every 3s until `COMPLETE`

---

## Caption Styles

| ID | Style | Description |
|---|---|---|
| `mrbeast` | MrBeast | Yellow highlights, Anton font, bold |
| `netflix` | Netflix | Orange-red highlights, clean Arial |
| `minimal` | Minimal | White only, subtle shadow |
| `tiktok` | TikTok | Yellow + thick black border |
| `hormozi` | Hormozi | Red highlights, heavy font |
| `podcast` | Podcast | Green speaker highlights, Georgia |

---

## REST API

```bash
# Upload video and start job
curl -X POST http://localhost:8080/api/jobs \
  -F "file=@myvideo.mp4" \
  -F "recipe=mrbeast" \
  -F "formats=9:16"

# Check status
curl http://localhost:8080/api/jobs/{jobId}

# Download clip
curl -O http://localhost:8080/api/jobs/{jobId}/clips/{clipId}/download
```

---

## Development (without Docker)

**Prerequisites:** Java 21, Maven, Python 3.11, FFmpeg, PostgreSQL, Redis

```bash
# Backend
cd backend
mvn spring-boot:run

# Workers
cd workers
pip install -r requirements.txt
ANTHROPIC_API_KEY=sk-ant-... python worker.py

# Frontend
cd frontend
npm install
npm run dev
```

---

## Roadmap

- [ ] Edit Recipe system (describe style in English → structured pipeline)
- [ ] Multi-speaker colored captions (pyannote diarization)
- [ ] AI Thumbnail generator
- [ ] Viral score breakdown (hook / emotion / pacing / CTA)
- [ ] Retention heatmap
- [ ] Batch processing (50+ videos)
- [ ] Multi-language captions
- [ ] Plugin marketplace SDK
- [ ] Analytics feedback loop (connect YouTube → AI adapts per creator)

See `AI_VIDEO_EDITOR_SDK.md` for the full product vision.
