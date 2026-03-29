def estimate_time_saved(segments: list[dict]) -> int:
    total = 0.0
    for segment in segments:
        duration = segment["end"] - segment["start"]
        if segment["action"] == "cut":
            total += duration
        else:
            total += duration * 0.75
    return int(total)
