from __future__ import annotations

from app.services.audio_probe import create_audio_probe
from app.services.probe_service import create_lowres_probe, probe_exists
from app.services.stream_resolver import resolve_analysis_stream


def build_probe_artifact(job_id: str, url: str, metadata: dict) -> dict:
    """
    Build both video and audio analysis probes with adaptive quality.
    """
    stream_info = resolve_analysis_stream(url)

    video_probe = {"status": "fallback", "probe_path": None, "stderr": "", "profile": {}}
    audio_probe = {"status": "fallback", "audio_path": None, "stderr": ""}

    if stream_info["has_direct_url"]:
        direct_url = stream_info["direct_url"]
        video_probe = create_lowres_probe(
            direct_url,
            job_id,
            duration_seconds=metadata.get("duration_seconds"),
        )
        audio_probe = create_audio_probe(direct_url, job_id)

    return {
        "source_url": url,
        "platform": metadata.get("platform"),
        "duration_seconds": metadata.get("duration_seconds"),
        "analysis_target": "local_probe" if probe_exists(video_probe.get("probe_path")) else "remote_stream",
        "probe_path": video_probe.get("probe_path"),
        "probe_status": video_probe.get("status"),
        "probe_stderr": video_probe.get("stderr"),
        "analysis_profile": video_probe.get("profile"),
        "audio_path": audio_probe.get("audio_path"),
        "audio_status": audio_probe.get("status"),
        "audio_stderr": audio_probe.get("stderr"),
        "stream_info": stream_info,
    }
