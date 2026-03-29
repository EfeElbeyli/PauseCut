from yt_dlp import YoutubeDL


def fetch_video_metadata(url: str) -> dict:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "noplaylist": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    extractor = (info.get("extractor_key") or info.get("extractor") or "").lower()
    platform = "youtube" if "youtube" in extractor or "youtu" in url else extractor or "unknown"

    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "duration_seconds": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "uploader": info.get("uploader"),
        "webpage_url": info.get("webpage_url"),
        "description": info.get("description"),
        "platform": platform,
    }
