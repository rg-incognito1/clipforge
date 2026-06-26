# ClipForge — AI Video Editor SDK + SaaS

> API-first, GUI-powered, community-extensible video editing platform.
> Think: Canva + CapCut + OpusClip + Runway — but with a REST API, plugin marketplace, and "Edit Recipe" system at its core.

---

## Vision

Most AI video tools are black boxes: upload → wait → download. ClipForge is different.

It exposes every editing decision as a programmable, inspectable, and overridable layer — giving creators a powerful GUI, agencies a REST API, and developers a plugin SDK. The editing logic is described in structured "Edit Recipes" that can be saved, shared, sold, and applied across thousands of videos automatically.

---

## Why This Exists

| Problem | Current Tools | ClipForge |
|---|---|---|
| Creators spend 4+ hours editing one podcast | CapCut (manual) | AI generates 10 shorts in 20 min |
| Agencies can't scale editing across 50 clients | Premiere (expensive human time) | Batch API + Brand Kits |
| Developers want video AI in their own product | No good embeddable SDK | REST API + Webhooks + SDKs |
| Everyone's output looks the same | Generic presets | Edit Recipe marketplace |
| AI tools don't learn your audience | Static rules | Analytics feedback loop |

---

## Product Layers

```
┌─────────────────────────────────────────────────────────┐
│                    ClipForge GUI                        │
│         (Web app — Next.js, Timeline Editor)            │
├─────────────────────────────────────────────────────────┤
│                   Edit Recipe Engine                    │
│    (Describe style in English → Structured Pipeline)    │
├────────────────┬────────────────┬───────────────────────┤
│  Scene AI      │  Caption Engine │  Audio Engine        │
│  (detection,   │  (styles, sync, │  (music, ducking,    │
│   scoring)     │   highlighting) │   enhancement)       │
├────────────────┴────────────────┴───────────────────────┤
│                  Video Processing Core                  │
│           (FFmpeg workers, GPU rendering)               │
├─────────────────────────────────────────────────────────┤
│                    REST API Layer                       │
│           (Spring Boot orchestrator + auth)             │
├─────────────────────────────────────────────────────────┤
│               Plugin / Marketplace SDK                  │
│          (Community caption styles, transitions)        │
└─────────────────────────────────────────────────────────┘
```

---

## Core Features (All 30)

### Group 1 — AI Intelligence Layer

#### 1. AI Scene Detection
Instead of splitting every 30 seconds, the AI finds semantically meaningful moments:

- **Moment types detected:** hook, climax, CTA, question, emotional peak, punchline, viral moment
- **Model:** Whisper transcription → LLM (Claude) scene tagging → ffprobe shot boundary detection
- **Output:** Ranked list of clips with confidence scores and moment type labels

```json
{
  "clip_id": "clip_007",
  "start": "00:14:22",
  "end": "00:17:45",
  "moment_type": "emotional_peak",
  "viral_score": 91,
  "hook_strength": 88,
  "reason": "Voice pitch rises 40%, keywords: 'changed my life', audience laughter detected"
}
```

**Example:** 120-minute podcast → AI → 14 best clips (not 240 random 30s chunks)

---

#### 16. Viral Score
Every generated short gets a composite score:

| Signal | Score |
|---|---|
| Hook strength | 96 |
| Emotional arc | 88 |
| Pacing | 91 |
| Retention prediction | 85 |
| CTA presence | 42 |
| **Overall** | **87 / 100** |

Powered by a fine-tuned scoring model trained on viral vs. non-viral clips.

---

#### 17. Retention Heatmap
Timeline visualization showing predicted audience drop-off:

```
00:00 ████████████████████ 98%
00:15 ████████████████░░░░ 81%   ← predicted drop-off zone
00:30 ████████████████████ 96%
00:45 ████████████░░░░░░░░ 61%   ← AI suggests: add zoom here
01:00 ████████████████████ 94%
```

AI suggests: zoom, transition, music change, or cut at each drop-off point.

---

#### 30. Analytics Feedback Loop
Connect YouTube/TikTok → AI learns per-creator preferences:

- Creator A gets higher retention with yellow captions + fast zoom + no music
- Creator B gets better CTR with minimal captions + documentary music
- Future edits auto-adapt to that creator's audience — not generic rules

---

### Group 2 — Caption Engine

#### 2. Multiple Caption Styles

| Style | Font | Animation | Shadow | Emoji | Highlight |
|---|---|---|---|---|---|
| Netflix | Helvetica Neue | Fade | Soft | No | Italic |
| Mr Beast | Anton | Bounce | Hard black | Yes | Yellow fill |
| Alex Hormozi | Bebas Neue | Pop | None | No | Red underline |
| Ali Abdaal | Inter | Slide | Soft | Yes | Blue box |
| Minimal | System UI | None | None | No | None |
| TikTok | Proxima Nova | Bounce | Outlined | Yes | White fill |
| Gaming | Impact | Flash | Neon glow | Yes | Color burst |
| Anime | Custom JP | Shake | None | Yes | Manga lines |
| Podcast | Georgia | Typewriter | None | No | Quote marks |
| Corporate | Arial | Fade | Drop | No | Underline |

---

#### 3. Caption Templates Marketplace
Exactly like VS Code themes:

1. Creator builds custom caption style in GUI
2. Publishes to marketplace (free or paid)
3. Others install with one click
4. Revenue split: 70% creator / 30% ClipForge

---

#### 4. Dynamic Caption Highlighting
Not every word — AI highlights based on:

- **Pitch analysis:** Higher pitch → emphasized word
- **Keyword importance:** LLM scores semantic weight per word
- **Emotion:** Excited words get larger/bolder treatment

```
Before:  "This changed everything for my business"
After:   "This CHANGED EVERYTHING for my business"
```

---

#### 5. Speaker Detection
Multi-speaker caption differentiation:

- Speaker A → Blue captions (left-aligned)
- Speaker B → Green captions (right-aligned)
- Podcast host vs. guest automatic detection via speaker diarization (pyannote.audio)

---

#### 23. Multi-language Captions
Transcribe → Translate → Re-sync timestamps automatically:

- Supported: English, Hindi, Spanish, Japanese, French, Portuguese, German
- All translated captions stay synchronized to original audio timing
- Separate SRT/VTT export per language

---

### Group 3 — Video Intelligence

#### 6. Smart Crop
Detect what matters in frame, then crop for any aspect ratio:

- **Detects:** face, product, whiteboard, slides, screen recording, text overlay
- **Crops:** 16:9 → 9:16 without cutting faces or key content
- **Model:** MediaPipe face detection + custom ROI model

---

#### 7. Multi-Face Tracking
Podcast / interview mode:

- Speaker A talks → virtual camera follows Speaker A
- Speaker B responds → virtual camera follows Speaker B
- Smooth pan/cut transition between speakers
- Like professional camera direction, automated

---

#### 8. Auto Zoom
Emphasis zoom on important sentences:

```
Normal sentence → 100%
"This is important" → 105% (ramp up 0.3s)
"THIS CHANGED EVERYTHING" → 120% (hold 1.2s)
Sentence ends → ramp back to 100% (0.5s)
```

Zoom frequency and intensity configurable per Edit Recipe.

---

#### 9. Emotion-Aware Editing
AI detects emotional tone → applies matching edit style:

| Emotion | Zoom | Transition | Sound Effect | Music |
|---|---|---|---|---|
| Excited | Fast zoom in | Flash cut | Whoosh | Upbeat |
| Sad | Slow pull back | Fade | None | Soft piano |
| Angry | Shake | Hard cut | Impact | Tense |
| Funny | Pop | Bounce | Boing | Comedic sting |
| Inspirational | Ken Burns | Cross dissolve | Swell | Orchestral rise |

---

### Group 4 — Audio Engine

#### 10. Background Music AI
Not one static track — AI selects music matching video mood:

- **Mood detection:** LLM analyzes transcript tone per segment
- **Music library:** 50,000+ royalty-free tracks, tagged by mood
- **Music changes:** Automatically transitions when video tone shifts
- **Moods:** Motivational, Funny, Serious, Documentary, Luxury, Travel, Coding, Sad

---

#### 11. Auto Ducking
Professional audio mix:

```
Speaker starts talking → music fades from 100% → 15% over 0.3s
Speaker pauses → music rises from 15% → 80% over 0.5s
Speaker stops (end) → music returns to 100%
```

---

#### 12. Silence Removal
Automatically detects and removes:

- Filler words: "um", "uh", "hmm", "okay so", "like"
- Dead air: pauses > configurable threshold (default: 0.8s)
- Configurable aggressiveness (light / medium / aggressive)

---

#### 13. Repeated Word Removal
```
"Basically... basically... basically... I think..."
→ "Basically... I think..."
```

Detects repeated phrases within 5-second windows, keeps best delivery take.

---

#### 24. AI Voice Enhancement
Remove background noise and normalize:

- **Remove:** echo, fan noise, keyboard clicks, AC hum, room reverb
- **Normalize:** loudness to -14 LUFS (YouTube standard)
- **Model:** DeepFilterNet or RNNoise for real-time denoising

---

#### 25. Automatic Sound Effects
AI detects moments → inserts contextually appropriate SFX:

| Detected Moment | Sound Effect |
|---|---|
| Boom / explosion mentioned | Explosion SFX |
| Laughter | Audience laugh track |
| Success / win | Achievement chime |
| Suspense buildup | Tension riser |
| Surprise | Woah SFX |
| Price reveal | Cash register |

---

### Group 5 — Editing Tools

#### 14. AI Hook Generator
Replace weak openings with high-retention hooks:

```
Original start: "Hey guys, welcome back to my channel..."
AI replaces with: "90% of people make this mistake... (cut to: actual content)"
```

User can choose from 3-5 AI-generated hook options per clip.

---

#### 15. AI Thumbnail Generator
Per short, generate:

- 10 thumbnail variants (different expressions, text overlays, colors)
- AI selects faces with peak emotional expression from clip
- A/B test-ready (multiple options for YouTube upload)

---

#### 18. AI B-roll Generator
Automatically insert relevant visuals:

```
Speaker says "Tesla" → insert Tesla stock footage or image
Speaker says "meditation" → insert nature/calm B-roll
Speaker says "revenue went up" → insert rising graph animation
```

B-roll sources: licensed stock library + AI-generated (Runway/Kling API integration)

---

#### 19. Brand Kit
Upload once, apply everywhere:

- Logo (position: top-left, bottom-right, or custom)
- Brand fonts (auto-applied to all captions)
- Brand colors (applied to highlights and CTAs)
- Intro clip (3-5s, auto-prepended)
- Outro clip (3-5s with subscribe animation, auto-appended)
- All videos automatically match brand guidelines

---

#### 20. Auto CTA
Last 5 seconds auto-generates platform-specific CTAs:

- Subscribe button animation
- Bell icon animation
- "Follow for more" text overlay
- Website URL card
- Configurable per Brand Kit

---

### Group 6 — Export & Distribution

#### 21. Export Presets

| Platform | Resolution | FPS | Bitrate | Safe Zones |
|---|---|---|---|---|
| TikTok | 1080x1920 | 30 | 8 Mbps | 150px top/bottom |
| Instagram Reels | 1080x1920 | 30 | 10 Mbps | 250px top/bottom |
| YouTube Shorts | 1080x1920 | 60 | 15 Mbps | 100px top/bottom |
| Instagram Square | 1080x1080 | 30 | 8 Mbps | None |
| LinkedIn | 1920x1080 | 30 | 12 Mbps | None |
| Facebook | 1080x1920 | 30 | 8 Mbps | 200px bottom |
| Snapchat | 1080x1920 | 30 | 6 Mbps | 300px top/bottom |

---

#### 22. Batch Processing
Upload 50 videos → receive 220 shorts by morning:

- Async job queue (Redis + BullMQ)
- Parallel Docker worker pool (auto-scales)
- Email/webhook notification on completion
- Bulk download as ZIP or per-platform folder

---

### Group 7 — GUI Editor

#### 26. Timeline Editor
Full non-destructive timeline, not just AI output:

- **Drag** captions to reposition on timeline
- **Resize** clips by dragging handles
- **Split** clip at playhead
- **Merge** adjacent clips
- **Delete** unwanted segments
- **Undo/Redo** stack (50 levels)
- **Zoom** timeline in/out for precision editing
- Keyboard shortcuts matching industry standards

---

#### 27. Prompt Editing
Type instead of clicking:

```
"Make this more energetic"
→ AI: increases zoom frequency, adds upbeat music, tightens cuts

"Add cinematic zoom at 0:23"
→ AI: inserts Ken Burns zoom at specified timestamp

"Use Mr Beast style"
→ AI: applies Mr Beast Edit Recipe to current clip

"Remove the part where he stumbles"
→ AI: identifies and cuts the disfluency
```

---

---

## The Edit Recipe System (Key Differentiator)

This is the feature nobody has built correctly.

### What is an Edit Recipe?

A structured, shareable editing pipeline described in plain English — converted to a deterministic set of parameters:

```json
{
  "recipe_name": "MrBeast Style",
  "author": "ClipForge",
  "version": "1.0",
  "caption": {
    "style": "bold_bounce",
    "font": "Anton",
    "highlight_color": "#FFD700",
    "emoji_frequency": "high",
    "animation": "bounce"
  },
  "zoom": {
    "frequency": "aggressive",
    "max_scale": 1.25,
    "trigger": "emphasis_words"
  },
  "cuts": {
    "avg_cut_length_seconds": 2.1,
    "remove_pauses": true,
    "pause_threshold_ms": 500
  },
  "audio": {
    "music_mood": "hype",
    "music_volume": 0.12,
    "ducking": true,
    "sfx": ["whoosh", "impact", "pop"]
  },
  "transitions": {
    "type": "flash_cut",
    "duration_ms": 80
  },
  "color": {
    "grade": "vibrant",
    "saturation": 1.3,
    "contrast": 1.1
  },
  "thumbnail": {
    "style": "bold_text_face",
    "background": "yellow"
  }
}
```

### How It Works

```
User types: "Edit like MrBeast"
        ↓
LLM converts to Edit Recipe JSON
        ↓
Recipe Engine applies each parameter to video pipeline
        ↓
Rendered output matches the described style
```

### Recipe Marketplace

- Creators publish their signature editing style as a Recipe
- Other creators install/purchase with one click
- Revenue split: 70% creator / 30% platform
- Over time: the marketplace becomes more valuable than the editor itself
- Think: VS Code theme store, but for video editing

---

## Architecture

### System Design

```
                         ┌─────────────────┐
                         │   Next.js GUI   │
                         │  (Web + Mobile) │
                         └────────┬────────┘
                                  │ REST / WebSocket
                         ┌────────▼────────┐
                         │  Spring Boot    │
                         │  Orchestrator   │
                         │  + Auth + Jobs  │
                         └────────┬────────┘
                    ┌─────────────┼──────────────┐
                    │             │              │
           ┌────────▼──┐  ┌───────▼────┐  ┌─────▼──────┐
           │  Scene AI │  │ Caption    │  │  Audio     │
           │  Worker   │  │ Engine     │  │  Engine    │
           │ (Python)  │  │ (Python)   │  │ (Python)   │
           └────────┬──┘  └───────┬────┘  └─────┬──────┘
                    │             │              │
                    └─────────────▼──────────────┘
                              ┌──┴──┐
                              │Redis│  (job queue)
                              └──┬──┘
                    ┌────────────┼────────────┐
                    │            │            │
           ┌────────▼──┐  ┌─────▼─────┐  ┌──▼──────────┐
           │  FFmpeg   │  │  FFmpeg   │  │  FFmpeg     │
           │  Worker 1 │  │  Worker 2 │  │  Worker N   │
           │ (Docker)  │  │ (Docker)  │  │  (Docker)   │
           └────────┬──┘  └─────┬─────┘  └──┬──────────┘
                    └───────────▼────────────┘
                           ┌────┴────┐
                           │  S3 /   │
                           │  Blob   │
                           └─────────┘
```

### Service Breakdown

| Service | Language | Responsibility |
|---|---|---|
| API Gateway / Orchestrator | Spring Boot (Java) | Auth, job dispatch, webhooks, billing |
| Scene Detection Worker | Python (PyTorch, Whisper) | Transcription, moment detection, scoring |
| Caption Engine | Python (Pillow, OpenCV) | Rendering caption styles, sync, highlighting |
| Audio Engine | Python (librosa, DeepFilterNet) | Noise removal, ducking, music selection |
| Video Renderer | FFmpeg (Docker workers) | Final compositing and encoding |
| Frontend GUI | Next.js (React) | Timeline editor, dashboard, marketplace |
| Plugin Runtime | Node.js (sandboxed) | Community plugin execution |

---

## Tech Stack

### Backend
- **Java / Spring Boot** — API orchestration, job management, auth (JWT + OAuth), billing
- **Python 3.12** — All ML/video processing workers
- **Redis + BullMQ** — Async job queue, rate limiting
- **PostgreSQL** — User data, jobs, recipes, analytics
- **Docker + Kubernetes** — Scalable worker pool

### AI / ML
- **OpenAI Whisper** — Speech-to-text transcription
- **Claude (Anthropic)** — Scene tagging, Edit Recipe generation, prompt editing, hook writing
- **pyannote.audio** — Speaker diarization (multi-speaker detection)
- **MediaPipe** — Face detection and tracking
- **DeepFilterNet** — Audio noise removal
- **CLIP / custom model** — B-roll semantic matching
- **Custom scoring model** — Viral score, retention prediction

### Video Processing
- **FFmpeg** — Core video manipulation (crop, encode, composite)
- **OpenCV** — Frame analysis, smart crop
- **MoviePy** — Python-level video editing pipeline

### Frontend
- **Next.js 15 (App Router)** — Main GUI
- **React** — Component layer
- **Tailwind CSS + shadcn/ui** — Design system
- **Fabric.js or Remotion** — Timeline editor and caption preview
- **Zustand** — Editor state management
- **React Query** — API data fetching

### Infrastructure
- **Vercel** — Frontend hosting, edge middleware
- **AWS / GCP** — Video worker compute (GPU instances for AI models)
- **S3 / Cloudflare R2** — Video storage (input + output)
- **Cloudflare** — CDN for delivered videos
- **Stripe** — Billing

---

## GUI — Key Screens

### 1. Upload & Configure
```
┌─────────────────────────────────────────────────────────┐
│  ClipForge                                    [Sign in] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│         ┌─────────────────────────────────┐            │
│         │    Drop your video here         │            │
│         │    or click to upload           │            │
│         │    (MP4, MOV, up to 4 hours)    │            │
│         └─────────────────────────────────┘            │
│                                                         │
│  Edit Recipe:  [MrBeast ▼]   or  ["Describe style..."] │
│                                                         │
│  Output formats: [✓] 9:16  [✓] 16:9  [ ] 1:1          │
│                                                         │
│  Captions: [✓]   Music: [✓]   B-roll: [ ]              │
│                                                         │
│                     [Generate Shorts →]                 │
└─────────────────────────────────────────────────────────┘
```

### 2. Results Dashboard
```
┌─────────────────────────────────────────────────────────┐
│  ← Back    "Marketing Podcast Ep 47"    [Export All]   │
├─────────────────────────────────────────────────────────┤
│  14 clips found   Sorted by: [Viral Score ▼]           │
│                                                         │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐       │
│  │ 🎬     │  │ 🎬     │  │ 🎬     │  │ 🎬     │       │
│  │  :47   │  │ 1:12   │  │  :33   │  │ 2:01   │       │
│  │ 94/100 │  │ 91/100 │  │ 88/100 │  │ 82/100 │       │
│  │ Viral  │  │ Hook   │  │ CTA    │  │ Funny  │       │
│  │ [Edit] │  │ [Edit] │  │ [Edit] │  │ [Edit] │       │
│  └────────┘  └────────┘  └────────┘  └────────┘       │
└─────────────────────────────────────────────────────────┘
```

### 3. Timeline Editor
```
┌─────────────────────────────────────────────────────────┐
│  [←] Clip 1 of 14    Viral Score: 94/100   [Export]   │
├─────────────────────┬───────────────────────────────────┤
│                     │  ┌─────────────────────────────┐ │
│   [Video Preview]   │  │ Retention Heatmap           │ │
│                     │  │ ████████████░░██████████    │ │
│   0:00 / 0:47       │  └─────────────────────────────┘ │
│                     │                                   │
│   [Prompt Edit...]  │  Caption Style: [MrBeast ▼]      │
│                     │  Music: [Hype ▼]                  │
├─────────────────────┴───────────────────────────────────┤
│  Timeline                                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │ VIDEO  [████████████████████████████████████████] │  │
│  │ AUDIO  [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓] │  │
│  │ MUSIC  [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] │  │
│  │ CAPS   [████ ██████ ████ ██████████ ███████████] │  │
│  └──────────────────────────────────────────────────┘  │
│  [Split] [Delete] [Undo] [Redo] [Zoom+] [Zoom-]        │
└─────────────────────────────────────────────────────────┘
```

---

## REST API

### Authentication
```
POST /api/v1/auth/token
Authorization: Basic {api_key}

→ { "access_token": "...", "expires_in": 3600 }
```

### Core Endpoints

```http
# Upload a video and start processing
POST /api/v1/videos
Content-Type: multipart/form-data
{
  "file": <binary>,
  "recipe": "mrbeast",           // or recipe_id from marketplace
  "formats": ["9:16", "16:9"],
  "captions": true,
  "music": true,
  "language": "en"
}

→ { "job_id": "job_abc123", "status": "queued", "webhook_url": "..." }


# Check job status
GET /api/v1/jobs/{job_id}

→ {
    "status": "processing",        // queued | processing | complete | failed
    "progress": 67,
    "clips_found": 14,
    "eta_seconds": 120
  }


# Get results
GET /api/v1/jobs/{job_id}/clips

→ {
    "clips": [
      {
        "clip_id": "clip_001",
        "viral_score": 94,
        "moment_type": "hook",
        "duration": 47,
        "download_url": "https://cdn.clipforge.io/...",
        "thumbnail_url": "https://cdn.clipforge.io/...",
        "srt_url": "https://cdn.clipforge.io/...",
        "formats": {
          "9:16": "https://cdn...",
          "16:9": "https://cdn..."
        }
      }
    ]
  }


# Generate short from specific parameters
POST /api/v1/clips/{clip_id}/regenerate
{
  "recipe": "documentary",
  "captions": { "style": "netflix", "highlight": true },
  "zoom": { "frequency": "low" },
  "music": { "mood": "serious" }
}


# Batch processing
POST /api/v1/batch
{
  "videos": ["s3://bucket/video1.mp4", "s3://bucket/video2.mp4"],
  "recipe": "alex_abdaal",
  "formats": ["9:16"],
  "webhook": "https://yourapp.com/webhooks/clipforge"
}
```

### Webhook Payload
```json
{
  "event": "job.complete",
  "job_id": "job_abc123",
  "clips": [...],
  "processing_time_seconds": 847,
  "credits_used": 15
}
```

---

## Plugin SDK

Community developers can build:

- **Caption Style Plugins** — Custom fonts, animations, effects
- **Transition Packs** — Anime-style, glitch, film burn
- **Sound Effect Packs** — Gaming, podcast, sports commentary
- **Export Plugins** — Custom platforms, proprietary formats
- **AI Model Plugins** — Replace/augment any AI step

### Plugin Interface (TypeScript)

```typescript
import { ClipForgePlugin, CaptionFrame, VideoSegment } from '@clipforge/sdk';

export default class AnimeCaptionPlugin implements ClipForgePlugin {
  metadata = {
    name: 'Anime Captions',
    version: '1.0.0',
    type: 'caption_style'
  };

  renderCaption(frame: CaptionFrame): CaptionFrame {
    return {
      ...frame,
      font: 'ShinGo-Bold',
      borderColor: '#FFFFFF',
      borderWidth: 4,
      animation: 'typewriter',
      shadowColor: '#000000',
      characterSpacing: 2
    };
  }
}
```

---

## Pricing Model

### Creator Plans (GUI)

| Plan | Price | Minutes/month | Shorts/month | Features |
|---|---|---|---|---|
| Free | $0 | 30 min | 5 shorts | Basic captions, 3 styles |
| Starter | $19/mo | 200 min | 50 shorts | All caption styles, music |
| Pro | $49/mo | 600 min | 200 shorts | B-roll, brand kit, batch |
| Agency | $149/mo | 2,000 min | Unlimited | White-label, API access |

### Developer Plans (API)

| Plan | Price | Credits | Rate Limit |
|---|---|---|---|
| Dev | $0 | 50 credits | 10 req/hr |
| Growth | $99/mo | 1,000 credits | 100 req/hr |
| Scale | $499/mo | 10,000 credits | 1,000 req/hr |
| Enterprise | Custom | Unlimited | Custom |

1 credit = 1 minute of video processed

### Marketplace Revenue
- Plugin sales: 70% creator / 30% ClipForge
- Recipe sales: 70% creator / 30% ClipForge
- Caption template sales: 70% creator / 30% ClipForge

---

## MVP Scope (Ship First)

**Phase 1 — Core Loop (8 weeks)**

Build the minimum that proves value end-to-end:

- [ ] Video upload (S3)
- [ ] Whisper transcription
- [ ] Claude scene detection (top 5 moments)
- [ ] FFmpeg clip extraction
- [ ] 3 caption styles (Mr Beast, Netflix, Minimal)
- [ ] Smart crop (9:16 from 16:9)
- [ ] Auto silence removal
- [ ] Export as MP4
- [ ] Basic dashboard GUI (upload → results)
- [ ] REST API with API key auth

**Phase 2 — Quality & Engagement (6 weeks)**

- [ ] All 10 caption styles
- [ ] Auto zoom
- [ ] Background music + auto ducking
- [ ] Viral score
- [ ] Thumbnail generator
- [ ] Timeline editor (basic)
- [ ] Brand kit
- [ ] Batch processing

**Phase 3 — Differentiation (8 weeks)**

- [ ] Edit Recipe system + marketplace
- [ ] Prompt editing
- [ ] Speaker detection + colored captions
- [ ] Retention heatmap
- [ ] AI B-roll
- [ ] Multi-language captions
- [ ] Plugin SDK
- [ ] Analytics feedback loop

---

## Competitive Positioning

| Feature | ClipForge | OpusClip | CapCut | Descript | Runway |
|---|---|---|---|---|---|
| AI scene detection | ✅ | ✅ | ❌ | ❌ | ❌ |
| Caption marketplace | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit Recipe system | ✅ | ❌ | ❌ | ❌ | ❌ |
| Prompt editing | ✅ | ❌ | ❌ | ✅ | ❌ |
| REST API | ✅ | Limited | ❌ | ❌ | ✅ |
| Plugin SDK | ✅ | ❌ | ❌ | ❌ | ❌ |
| Speaker-colored captions | ✅ | ❌ | ❌ | ✅ | ❌ |
| Analytics feedback loop | ✅ | ❌ | ❌ | ❌ | ❌ |
| Retention heatmap | ✅ | ❌ | ❌ | ❌ | ❌ |
| Viral scoring | ✅ | Basic | ❌ | ❌ | ❌ |
| GUI timeline editor | ✅ | ❌ | ✅ | ✅ | ✅ |
| White-label API | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## Why This Wins

1. **Edit Recipes create a network effect** — every creator who publishes a recipe brings their audience to ClipForge
2. **API-first means B2B revenue** — agencies and app developers pay more and churn less than individual creators
3. **Plugin marketplace creates lock-in** — creators invest in their workflow, making switching costly
4. **Analytics feedback loop** — the more a creator uses ClipForge, the better it gets for their specific audience
5. **Genuinely modular** — every AI step is replaceable via the plugin SDK, so ClipForge improves as AI models improve

---

## GitHub Stars Strategy

- Open-source the Plugin SDK (drives developer adoption)
- Open-source FFmpeg pipeline utilities
- Keep AI models and Edit Recipe engine proprietary
- Publish "build your own AI video editor" tutorial series using the open API

---

*Document version: 1.0 — June 2026*
*Author: ClipForge Product Team*
