"""
Multi-style caption overlay for ClipForge.
Styles: mrbeast | netflix | minimal | tiktok | hormozi | podcast
Each style controls font, size, colors, border, and caption position.
"""
import os
import subprocess
import tempfile

_OUT_W = 1080
_OUT_H = 1920

STYLES = {
    "mrbeast": {
        "font": "Anton",
        "font_size": 62,
        "primary": "&H00FFFFFF&",
        "highlight": "&H0000FFFF&",   # yellow
        "outline": "&H00000000&",
        "shadow": "&H80000000&",
        "bold": True,
        "border": 4,
        "y_pos": 1380,
    },
    "netflix": {
        "font": "Arial",
        "font_size": 50,
        "primary": "&H00FFFFFF&",
        "highlight": "&H000040FF&",   # orange-red
        "outline": "&H96000000&",
        "shadow": "&HC8000000&",
        "bold": False,
        "border": 2,
        "y_pos": 1500,
    },
    "minimal": {
        "font": "Arial",
        "font_size": 46,
        "primary": "&H00FFFFFF&",
        "highlight": "&H00FFFFFF&",
        "outline": "&H64000000&",
        "shadow": "&H32000000&",
        "bold": False,
        "border": 1,
        "y_pos": 1520,
    },
    "tiktok": {
        "font": "Arial Black",
        "font_size": 58,
        "primary": "&H00FFFFFF&",
        "highlight": "&H0000FFFF&",   # yellow
        "outline": "&H00000000&",
        "shadow": "&H00000000&",
        "bold": True,
        "border": 3,
        "y_pos": 1450,
    },
    "hormozi": {
        "font": "Arial Black",
        "font_size": 60,
        "primary": "&H00FFFFFF&",
        "highlight": "&H000000FF&",   # red
        "outline": "&H00000000&",
        "shadow": "&H80000000&",
        "bold": True,
        "border": 3,
        "y_pos": 1400,
    },
    "podcast": {
        "font": "Georgia",
        "font_size": 44,
        "primary": "&H00FFFFFF&",
        "highlight": "&H00AAFF00&",   # green
        "outline": "&H80000000&",
        "shadow": "&H40000000&",
        "bold": False,
        "border": 2,
        "y_pos": 1480,
    },
}

DEFAULT_STYLE = "mrbeast"
MAX_WORD_S   = 0.9
CAPTION_LEAD = 0.15
BLOCK        = 4


def _remap_words(all_words, story_clips):
    offsets = []
    t = 0.0
    for clip in story_clips:
        offsets.append((clip['start_seconds'], clip['end_seconds'], t))
        t += clip['end_seconds'] - clip['start_seconds']

    result = []
    for w in all_words:
        ws, we = w['start'], w['end']
        for cs, ce, offset in offsets:
            if cs <= ws < ce:
                result.append({
                    'word':  w['word'],
                    'start': offset + (ws - cs),
                    'end':   offset + (min(we, ce) - cs),
                })
                break
    return result


def _fmt(seconds):
    h  = int(seconds // 3600)
    m  = int((seconds % 3600) // 60)
    s  = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _build_ass(mapped_words, style_name):
    s    = STYLES.get(style_name, STYLES[DEFAULT_STYLE])
    bold = -1 if s["bold"] else 0

    header = (
        f"[Script Info]\nScriptType: v4.00+\nPlayResX: {_OUT_W}\nPlayResY: {_OUT_H}\nWrapStyle: 0\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{s['font']},{s['font_size']},{s['primary']},&H000000FF&,{s['outline']},"
        f"{s['shadow']},{bold},0,0,0,100,100,0,0,1,{s['border']},1,8,30,30,{s['y_pos']},1\n"
        f"Style: Active,{s['font']},{s['font_size']},{s['highlight']},&H000000FF&,{s['outline']},"
        f"{s['shadow']},{bold},0,0,0,100,100,0,0,1,{s['border']},1,8,30,30,{s['y_pos']},1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    if not mapped_words:
        return header

    events = []
    blocks = [mapped_words[i:i + BLOCK] for i in range(0, len(mapped_words), BLOCK)]

    for b_idx, block in enumerate(blocks):
        next_start = blocks[b_idx + 1][0]['start'] if b_idx + 1 < len(blocks) else None
        block_end  = min(block[-1]['end'], block[-1]['start'] + MAX_WORD_S)
        if next_start is not None:
            block_end = min(block_end, next_start - CAPTION_LEAD)

        for active_idx, active_word in enumerate(block):
            seg_start = max(0.0, active_word['start'] - CAPTION_LEAD)
            if active_idx + 1 < len(block):
                raw_end = min(block[active_idx + 1]['start'], active_word['start'] + MAX_WORD_S)
                seg_end = max(seg_start + 0.05, raw_end - CAPTION_LEAD)
            else:
                seg_end = block_end

            if seg_end <= seg_start:
                seg_end = seg_start + 0.05

            parts = []
            for j, w in enumerate(block):
                if j == active_idx:
                    parts.append(r"{\c" + s['highlight'] + r"}" + w['word'] + r"{\c" + s['primary'] + r"}")
                else:
                    parts.append(w['word'])

            line = " ".join(parts).strip()
            events.append(
                f"Dialogue: 0,{_fmt(seg_start)},{_fmt(seg_end)},Default,,0,0,0,,{line}"
            )

    return header + "\n".join(events) + "\n"


def burn_captions(video_path, output_path, all_words, story_clips, style="mrbeast"):
    mapped = _remap_words(all_words, story_clips)
    if not mapped:
        import shutil
        shutil.copy2(video_path, output_path)
        print("  Captions: no mapped words, copied without captions")
        return

    print(f"  Captions: {len(mapped)} words, style={style}")
    ass_content = _build_ass(mapped, style)
    ass_file = tempfile.mktemp(suffix='.ass')

    try:
        with open(ass_file, 'w', encoding='utf-8') as f:
            f.write(ass_content)

        # FFmpeg on Windows needs forward slashes and escaped colons for filter paths
        ass_safe = ass_file.replace('\\', '/').replace(':', '\\:')
        enhance  = "unsharp=5:5:0.8:3:3:0,eq=contrast=1.05:saturation=1.1"

        subprocess.run([
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', f"ass='{ass_safe}',{enhance}",
            '-map', '0:v', '-map', '0:a?',
            '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
            '-c:a', 'aac', '-b:a', '128k',
            output_path,
        ], check=True, capture_output=True)
    finally:
        try:
            os.unlink(ass_file)
        except OSError:
            pass
