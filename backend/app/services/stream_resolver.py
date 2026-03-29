from __future__ import annotations

from yt_dlp import YoutubeDL


def resolve_analysis_stream(url: str) -> dict:
    """
    Resolve a stream URL suitable for analysis.

    For now, this returns the original page URL as a safe fallback, plus any direct format URL
    yt-dlp provides in the metadata. This keeps the skeleton ready for real low-res probe creation.
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "noplaylist": True,
        "format": "mp4/best",
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    direct_url = info.get("url")
    formats = info.get("formats") or []

    best_mp4_url = None
    for fmt in formats:
        fmt_url = fmt.get("url")
        ext = fmt.get("ext")
        if fmt_url and ext == "mp4":
            best_mp4_url = fmt_url
            break

    return {
        "page_url": url,
        "direct_url": best_mp4_url or direct_url,
        "has_direct_url": bool(best_mp4_url or direct_url),
    }
