"""
Claude-powered scene analysis — finds the best viral moments in any video.
General-purpose replacement for the HIMYM-specific Gemini analyzer.
"""
import json
import re
import time
import anthropic

_MODEL = "claude-sonnet-4-6"

_PROMPT = """You are an expert viral short-form video editor. Analyze this transcript and find the BEST moments to clip for engaging short-form content.

Look for moments that work standalone without context:
- HOOK: immediately engaging, surprising, or counterintuitive opening
- CLIMAX: the big reveal, punchline, or "aha" moment
- EMOTIONAL_PEAK: genuine emotion, passion, or vulnerability
- FUNNY: laugh-out-loud or deeply relatable
- QUESTION: engages curiosity, makes viewers want to know the answer
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
- Each clip: 15-60 seconds total
- Clips must NOT overlap each other
- End every clip at a natural sentence pause — NEVER cut mid-word or mid-sentence
- moment_type: one of hook | climax | emotional_peak | funny | question | cta | viral
- viral_score: 1-10 (10 = highest viral potential)
- storyline_title: snake_case, max 40 chars
- Only pick moments that work as standalone content without requiring prior context"""


def analyze_transcript(segments, api_key, retries=3):
    client = anthropic.Anthropic(api_key=api_key)

    transcript_text = '\n'.join(
        f"[{s['start']} - {s['end']}] {s['text']}"
        for s in segments
    )

    if not transcript_text.strip():
        raise ValueError("Transcript is empty — cannot analyze")

    prompt = _PROMPT.format(transcript=transcript_text)

    for attempt in range(1, retries + 1):
        try:
            message = client.messages.create(
                model=_MODEL,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = message.content[0].text.strip()
            raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE)
            raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)
            result = json.loads(raw)
            print(f"  Claude found {len(result['clips'])} clips")
            return result
        except Exception as e:
            print(f"  Claude attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(10 * attempt)

    raise RuntimeError("Analysis failed after all retries")
