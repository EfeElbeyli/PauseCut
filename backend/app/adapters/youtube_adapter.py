from urllib.parse import urlparse, parse_qs

from app.adapters.base import VideoSourceAdapter
from app.services.metadata_service import fetch_video_metadata


class YouTubeAdapter(VideoSourceAdapter):
    def validate_url(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.netloc in ["www.youtube.com", "youtube.com"]:
            return parsed.path == "/watch" and "v" in parse_qs(parsed.query)
        if parsed.netloc == "youtu.be":
            return bool(parsed.path.strip("/"))
        return False

    def fetch_metadata(self, url: str) -> dict:
        return fetch_video_metadata(url)
