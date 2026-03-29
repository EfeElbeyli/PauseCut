def get_analysis_profile(duration_seconds: int | None) -> dict:
    duration = duration_seconds or 0

    if duration >= 7200:  # 120+ min
        return {
            "profile": "ultra_long",
            "probe_fps": 0.2,
            "probe_width": 256,
            "force_chunking": True,
            "chunk_target": 180,
        }

    if duration >= 5400:  # 90+ min
        return {
            "profile": "very_long",
            "probe_fps": 0.25,
            "probe_width": 320,
            "force_chunking": True,
            "chunk_target": 150,
        }

    if duration >= 2700:  # 45+ min
        return {
            "profile": "long",
            "probe_fps": 0.5,
            "probe_width": 426,
            "force_chunking": False,
            "chunk_target": 120,
        }

    return {
        "profile": "standard",
        "probe_fps": 2.0,
        "probe_width": 640,
        "force_chunking": False,
        "chunk_target": 90,
    }
