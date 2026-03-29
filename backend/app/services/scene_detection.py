from __future__ import annotations

from typing import Optional
from app.services.analysis_profile import get_analysis_profile


def detect_scenes(probe: dict) -> list[dict]:
    """
    Adaptive scene detection:
    - very long videos skip expensive scene detection and use chunking
    - shorter videos try PySceneDetect first
    """
    duration = probe.get("duration_seconds") or 1800
    profile = probe.get("analysis_profile") or get_analysis_profile(duration)
    probe_path = probe.get("probe_path")

    if profile.get("force_chunking"):
        return _fallback_chunking(duration, profile.get("chunk_target", 150))

    if probe_path:
        scenes = _detect_with_pyscenedetect(probe_path)
        if scenes:
            return scenes

    return _fallback_chunking(duration, profile.get("chunk_target", 120))


def _detect_with_pyscenedetect(video_path: str) -> Optional[list[dict]]:
    try:
        from scenedetect import detect
        from scenedetect.detectors import ContentDetector
    except Exception:
        return None

    try:
        scene_list = detect(video_path, ContentDetector(threshold=30.0))
    except Exception:
        return None

    if not scene_list:
        return None

    scenes = []
    for start, end in scene_list:
        scenes.append(
            {
                "start": start.get_seconds(),
                "end": end.get_seconds(),
            }
        )
    return scenes or None


def _fallback_chunking(duration: int, chunk_target: int) -> list[dict]:
    chunk = max(45, int(chunk_target))
    scenes = []
    start = 0
    while start < duration:
        end = min(start + chunk, duration)
        scenes.append({"start": float(start), "end": float(end)})
        start = end
    return scenes
