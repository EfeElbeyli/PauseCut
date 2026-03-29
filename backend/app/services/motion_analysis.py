from __future__ import annotations


def analyze_motion(frame_samples: list[dict]) -> list[dict]:
    """
    Placeholder motion analysis upgraded to use descriptor deltas when available.
    """
    results = []
    for sample in frame_samples:
        motion_score = _estimate_motion_from_descriptors(sample)
        results.append(
            {
                "scene_index": sample["scene_index"],
                "motion_score": motion_score,
                "low_motion": motion_score < 0.25,
            }
        )
    return results


def _estimate_motion_from_descriptors(sample: dict) -> float:
    descriptors = sample.get("descriptors") or []
    if len(descriptors) < 2:
        return 0.15 if sample.get("similarity_hint", 0.0) > 0.7 else 0.55

    try:
        import numpy as np
    except Exception:
        return 0.5

    deltas = []
    for i in range(len(descriptors) - 1):
        a = np.array(descriptors[i], dtype=float)
        b = np.array(descriptors[i + 1], dtype=float)
        deltas.append(float(np.mean(np.abs(a - b))))

    score = float(sum(deltas) / len(deltas))
    return max(0.0, min(1.0, score * 8.0))
