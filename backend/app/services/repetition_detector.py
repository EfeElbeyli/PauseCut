from __future__ import annotations


def detect_repetition(frame_samples: list[dict]) -> list[dict]:
    """
    Compare adjacent scene descriptors and estimate repetition / visual redundancy.
    """
    results = []

    for idx, sample in enumerate(frame_samples):
        if idx == 0:
            repetition_score = 0.0
        else:
            repetition_score = _similarity_between(
                frame_samples[idx - 1].get("avg_descriptor"),
                sample.get("avg_descriptor"),
                fallback=sample.get("similarity_hint", 0.0),
            )

        results.append(
            {
                "scene_index": sample["scene_index"],
                "repetition_score": repetition_score,
                "high_repetition": repetition_score > 0.72,
            }
        )

    return results


def _similarity_between(prev_desc, curr_desc, fallback: float = 0.0) -> float:
    if prev_desc is None or curr_desc is None:
        return float(fallback)

    try:
        import numpy as np
    except Exception:
        return float(fallback)

    a = np.array(prev_desc, dtype=float)
    b = np.array(curr_desc, dtype=float)

    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0
    sim = float(np.dot(a, b) / denom)
    return max(0.0, min(1.0, sim))
