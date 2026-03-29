from __future__ import annotations

import os
import subprocess
from pathlib import Path

from app.services.analysis_profile import get_analysis_profile


PROBE_DIR = Path("app/db/probes")
PROBE_DIR.mkdir(parents=True, exist_ok=True)


def _safe_name(job_id: str) -> str:
    return "".join(c for c in job_id if c.isalnum() or c in ("-", "_"))


def create_lowres_probe(url: str, job_id: str, duration_seconds: int | None = None) -> dict:
    """
    Create an adaptive low-resolution probe.
    Longer videos are processed with much lower FPS and width.
    """
    profile = get_analysis_profile(duration_seconds)
    probe_name = f"{_safe_name(job_id)}_probe.mp4"
    probe_path = PROBE_DIR / probe_name

    fps = str(profile["probe_fps"])
    width = int(profile["probe_width"])

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        url,
        "-vf",
        f"scale='min({width},iw)':-2,fps={fps}",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "32",
        str(probe_path),
    ]

    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if completed.returncode != 0:
        return {
            "status": "fallback",
            "probe_path": None,
            "stderr": completed.stderr[-1200:],
            "profile": profile,
        }

    return {
        "status": "ok",
        "probe_path": str(probe_path),
        "stderr": "",
        "profile": profile,
    }


def probe_exists(probe_path: str | None) -> bool:
    return bool(probe_path and os.path.exists(probe_path))
