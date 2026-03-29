from __future__ import annotations


def build_chunk_plan(duration_seconds: int) -> list[dict]:
    """
    Adaptive chunking with smaller overlap:
    - < 45 min: 1 chunk
    - 45-90 min: 2 chunks
    - 90-150 min: 3 chunks
    - 150+ min: 4 chunks
    """
    duration = max(1, int(duration_seconds))
    if duration < 2700:
        return [{"index": 0, "start": 0.0, "end": float(duration), "offset": 0.0}]

    overlap = 60.0  # reduced overlap for speed

    if duration < 5400:
        mid = duration / 2
        return [
            {"index": 0, "start": 0.0, "end": min(duration, mid + overlap), "offset": 0.0},
            {"index": 1, "start": max(0.0, mid - overlap), "end": float(duration), "offset": max(0.0, mid - overlap)},
        ]

    if duration < 9000:
        third = duration / 3
        return [
            {"index": 0, "start": 0.0, "end": min(duration, third + overlap), "offset": 0.0},
            {"index": 1, "start": max(0.0, third - overlap), "end": min(duration, 2 * third + overlap), "offset": max(0.0, third - overlap)},
            {"index": 2, "start": max(0.0, 2 * third - overlap), "end": float(duration), "offset": max(0.0, 2 * third - overlap)},
        ]

    quarter = duration / 4
    return [
        {"index": 0, "start": 0.0, "end": min(duration, quarter + overlap), "offset": 0.0},
        {"index": 1, "start": max(0.0, quarter - overlap), "end": min(duration, 2 * quarter + overlap), "offset": max(0.0, quarter - overlap)},
        {"index": 2, "start": max(0.0, 2 * quarter - overlap), "end": min(duration, 3 * quarter + overlap), "offset": max(0.0, 2 * quarter - overlap)},
        {"index": 3, "start": max(0.0, 3 * quarter - overlap), "end": float(duration), "offset": max(0.0, 3 * quarter - overlap)},
    ]


def shift_segments_to_global(segments: list[dict], offset: float) -> list[dict]:
    shifted = []
    for seg in segments:
        new_seg = dict(seg)
        new_seg["start"] = round(float(seg["start"]) + offset, 3)
        new_seg["end"] = round(float(seg["end"]) + offset, 3)
        shifted.append(new_seg)
    return shifted


def merge_overlapping_segments(segments: list[dict], tolerance: float = 0.75) -> list[dict]:
    if not segments:
        return []

    segments = sorted(segments, key=lambda s: (s["start"], s["end"]))
    merged = [dict(segments[0])]

    for seg in segments[1:]:
        last = merged[-1]
        overlaps = seg["start"] <= last["end"] + tolerance
        same_action = seg["action"] == last["action"]

        if overlaps and same_action:
            last["end"] = max(last["end"], seg["end"])
            last["confidence"] = max(last.get("confidence", 0.0), seg.get("confidence", 0.0))
            last["reasons"] = sorted(set(last.get("reasons", [])) | set(seg.get("reasons", [])))
        else:
            merged.append(dict(seg))

    return merged
