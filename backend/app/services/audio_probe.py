from __future__ import annotations

import subprocess
from pathlib import Path


AUDIO_DIR = Path("app/db/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def create_audio_probe(url: str, job_id: str) -> dict:
    """
    Extract a low-bandwidth mono WAV for speech/silence analysis.
    """
    out_path = AUDIO_DIR / f"{job_id}_audio.wav"

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        url,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(out_path),
    ]

    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        return {
            "status": "fallback",
            "audio_path": None,
            "stderr": completed.stderr[-1200:],
        }

    return {
        "status": "ok",
        "audio_path": str(out_path),
        "stderr": "",
    }
