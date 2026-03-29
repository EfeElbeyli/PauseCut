from __future__ import annotations

import subprocess
from pathlib import Path


CHUNK_DIR = Path("app/db/chunks")
CHUNK_DIR.mkdir(parents=True, exist_ok=True)


def create_chunk_probe(input_source: str, job_id: str, chunk: dict) -> dict:
    """
    Faster chunk probe:
    - lower resolution
    - lower fps
    - faster preset
    """
    idx = chunk["index"]
    start = float(chunk["start"])
    end = float(chunk["end"])
    duration = max(0.1, end - start)

    video_probe = CHUNK_DIR / f"{job_id}_chunk_{idx}.mp4"
    audio_probe = CHUNK_DIR / f"{job_id}_chunk_{idx}.wav"

    video_cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start:.3f}",
        "-t", f"{duration:.3f}",
        "-i", input_source,
        "-vf", "scale='min(224,iw)':-2,fps=0.10",
        "-an",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "35",
        str(video_probe),
    ]

    audio_cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start:.3f}",
        "-t", f"{duration:.3f}",
        "-i", input_source,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        str(audio_probe),
    ]

    v = subprocess.run(video_cmd, capture_output=True, text=True)
    a = subprocess.run(audio_cmd, capture_output=True, text=True)

    return {
        "probe_path": str(video_probe) if video_probe.exists() else None,
        "audio_path": str(audio_probe) if audio_probe.exists() else None,
        "duration_seconds": duration,
        "video_ok": v.returncode == 0,
        "audio_ok": a.returncode == 0,
        "chunk": chunk,
    }
