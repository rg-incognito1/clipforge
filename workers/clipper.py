"""
Clip extraction, 9:16 reframing, concat, and caption burn — adapted from shortGen_HIMYM.
Added: recipe parameter to select caption style.
"""
import os
import subprocess
import tempfile


def create_story_short(video_path, story, output_dir, clip_name,
                        pipeline=None, all_words=None, recipe="mrbeast"):
    from reframer import reframe_clip
    from captioner import burn_captions

    clips = story['clips']
    title = story['storyline_title']
    score = story['score']

    parts_dir = os.path.join(output_dir, f'_parts_{clip_name}')
    os.makedirs(parts_dir, exist_ok=True)

    part_paths = []
    try:
        for i, clip in enumerate(clips, 1):
            part_path = os.path.join(parts_dir, f"part_{i:02d}.mp4")
            print(f"  Part {i}/{len(clips)}: {clip['start_seconds']:.1f}s – {clip['end_seconds']:.1f}s")
            reframe_clip(video_path, clip['start_seconds'], clip['end_seconds'],
                         part_path, pipeline=pipeline)
            part_paths.append(part_path)

        merged_path = os.path.join(output_dir, f'_merged_{clip_name}.mp4')
        print(f"  Merging {len(part_paths)} parts...")
        _merge_clips(part_paths, merged_path)

        safe_title = "".join(c if c.isalnum() or c == '_' else '_' for c in title)[:40]
        out_path   = os.path.join(output_dir, f"{safe_title}_s{score}.mp4")

        if all_words:
            print(f"  Burning captions (style: {recipe})...")
            burn_captions(merged_path, out_path, all_words, clips, style=recipe)
            try:
                os.unlink(merged_path)
            except OSError:
                pass
        else:
            os.rename(merged_path, out_path)

        return out_path

    finally:
        for p in part_paths:
            try:
                os.unlink(p)
            except OSError:
                pass
        try:
            os.rmdir(parts_dir)
        except OSError:
            pass


def _merge_clips(clip_paths, output_path):
    list_file = tempfile.mktemp(suffix='.txt')
    try:
        with open(list_file, 'w') as f:
            for p in clip_paths:
                safe = p.replace('\\', '/').replace("'", "'\\''")
                f.write(f"file '{safe}'\n")
        subprocess.run([
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0',
            '-i', list_file,
            '-c', 'copy',
            output_path,
        ], check=True, capture_output=True)
    finally:
        try:
            os.unlink(list_file)
        except OSError:
            pass
