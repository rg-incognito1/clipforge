"""
Gemini-powered scene analysis — finds the best viral moments in any video.
Uses the same Gemini client pattern as shortGen_HIMYM, but with a
general-purpose prompt (works on any video, not just HIMYM).
"""
import json
import re
import time
import requests

_GEMINI_BASE     = 'https://generativelanguage.googleapis.com/v1/models/{}:generateContent'
_FALLBACK_MODELS = ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.0-flash']

_PROMPT = """You are an expert viral short-form video editor. Analyze this transcript and find the BEST moments to clip for engaging short-form content.

Look for moments that work standalone without requiring prior context:
- HOOK: immediately engaging, surprising, or counterintuitive
- CLIMAX: the big reveal, punchline, or "aha" moment
- EMOTIONAL_PEAK: genuine emotion, passion, or vulnerability
- FUNNY: laugh-out-loud or deeply relatable
- QUESTION: engages curiosity, makes viewers want the answer
- CTA: strong call to action that creates urgency
- VIRAL: likely to generate shares, comments, or reactions

Transcript (format: [start_sec - end_sec] text):
{transcript}

Return ONLY valid JSON (no markdown, no explanation):
{{
  "clips": [
    {{
      "start_seconds": 45.0,
      "end_seconds": 87.0,
      "label": "hook",
      "moment_type": "hook",
      "description": "Speaker makes a shocking claim that challenges the audience",
      "storyline_title": "shocking_productivity_claim",
      "storyline_summary": "Host reveals that 90% of people waste their mornings doing the wrong thing",
      "viral_score": 9
    }}
  ]
}}

Rules:
- Find 1-5 of the absolute BEST moments (quality over quantity)
- Each clip: 15-60 seconds
- Clips must NOT overlap each other
- End every clip at a natural sentence pause — NEVER cut mid-word or mid-sentence
- moment_type: one of hook | climax | emotional_peak | funny | question | cta | viral
- viral_score: 1-10 (10 = highest viral potential)
- storyline_title: snake_case, max 40 chars
- Only pick moments that work as standalone content without requiring prior context"""


def _gemini_post(payload, api_key, timeout=120):
    """POST to Gemini with automatic model fallback on 503/429."""
    for i, model in enumerate(_FALLBACK_MODELS):
        try:
            resp = requests.post(
                _GEMINI_BASE.format(model),
                params={'key': api_key},
                json=payload,
                timeout=timeout,
            )
            resp.raise_for_status()
            if i > 0:
                print(f"  Success with fallback model: {model}")
            return resp.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        except requests.HTTPError as e:
            if e.response.status_code in (503, 429) and i < len(_FALLBACK_MODELS) - 1:
                print(f"  {model} returned {e.response.status_code}, trying {_FALLBACK_MODELS[i+1]}")
                time.sleep(5)
            else:
                raise


def analyze_transcript(segments, api_key, retries=5):
    transcript_text = '\n'.join(
        f"[{s['start']} - {s['end']}] {s['text']}"
        for s in segments
    )

    if not transcript_text.strip():
        raise ValueError("Transcript is empty — cannot analyze")

    prompt = _PROMPT.format(transcript=transcript_text)
    payload = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {'temperature': 0.2},
    }

    for attempt in range(1, retries + 1):
        try:
            raw = _gemini_post(payload, api_key, timeout=120)
            raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE)
            raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)
            result = json.loads(raw)
            print(f"  Gemini found {len(result['clips'])} clips")
            return result
        except Exception as e:
            print(f"  Gemini attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(15)

    raise RuntimeError("Analysis failed after all retries")
