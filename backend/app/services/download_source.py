from __future__ import annotations

import os
from pathlib import Path

from yt_dlp import YoutubeDL


DOWNLOAD_DIR = Path("app/db/downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def ensure_local_source(job_id: str, url: str) -> str:
    """
    Download the source video locally and return a stable MP4 path.
    Uses a persistent cache per job_id.
    """
    out_base = DOWNLOAD_DIR / f"{job_id}"
    final_mp4 = str(out_base.with_suffix(".mp4"))

    if os.path.exists(final_mp4):
        return final_mp4

    ydl_opts = {
        "format": "mp4/bestvideo+bestaudio/best",
        "outtmpl": str(out_base) + ".%(ext)s",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if os.path.exists(final_mp4):
        return final_mp4

    # Fallback: find any downloaded file for this job base
    for candidate in DOWNLOAD_DIR.glob(f"{job_id}.*"):
        if candidate.is_file():
            return str(candidate)

    raise FileNotFoundError("Local video download failed.")
