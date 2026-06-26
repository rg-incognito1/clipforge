import os
from faster_whisper import WhisperModel


def transcribe_video(video_path, model_size="base"):
    """Returns (segments, words) with word-level timestamps."""
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    raw_segments, _ = model.transcribe(video_path, beam_size=5, word_timestamps=True)

    segments = []
    words = []
    for seg in raw_segments:
        segments.append({
            'start': round(seg.start, 2),
            'end':   round(seg.end, 2),
            'text':  seg.text.strip(),
        })
        if seg.words:
            for w in seg.words:
                words.append({
                    'word':  w.word.strip(),
                    'start': round(w.start, 3),
                    'end':   round(w.end, 3),
                })

    return segments, words
