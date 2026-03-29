from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services.audio_analysis import analyze_audio
from app.services.chunk_probe_service import create_chunk_probe
from app.services.chunking_service import shift_segments_to_global, merge_overlapping_segments
from app.services.decision_engine import build_candidates, decide_segments
from app.services.frame_sampler import sample_frames
from app.services.motion_analysis import analyze_motion
from app.services.repetition_detector import detect_repetition
from app.services.scene_detection import detect_scenes


def analyze_chunks_parallel(
    job_id: str,
    input_source: str,
    chunks: list[dict],
    mode: str,
    protect_dialogue: bool,
    max_workers: int = 2,
    on_status=None,
) -> tuple[list[dict], int]:
    all_segments = []
    total = len(chunks)
    completed = 0
    processed_frames = 0

    if on_status:
        on_status({"type": "start", "completed": 0, "total": total, "frames": 0})

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(
                _analyze_single_chunk,
                job_id,
                input_source,
                chunk,
                mode,
                protect_dialogue,
            )
            for chunk in chunks
        ]

        for future in as_completed(futures):
            result = future.result()
            all_segments.extend(result["segments"])
            completed += 1
            processed_frames += result["processed_frames"]

            if on_status:
                on_status({
                    "type": "chunk_done",
                    "completed": completed,
                    "total": total,
                    "frames": processed_frames,
                })

    return merge_overlapping_segments(all_segments), processed_frames


def _analyze_single_chunk(
    job_id: str,
    input_source: str,
    chunk: dict,
    mode: str,
    protect_dialogue: bool,
) -> dict:
    probe = create_chunk_probe(input_source, job_id, chunk)

    if not probe["probe_path"]:
        return {"segments": [], "processed_frames": 0}

    scenes = detect_scenes(probe)
    frame_samples = sample_frames(probe, scenes)
    processed_frames = sum(sample.get("frame_count", 0) for sample in frame_samples)

    motion_results = analyze_motion(frame_samples)
    repetition_results = detect_repetition(frame_samples)
    audio_results = analyze_audio(probe, scenes, protect_dialogue)

    candidates = build_candidates(
        scenes=scenes,
        motion_results=motion_results,
        audio_results=audio_results,
        repetition_results=repetition_results,
    )

    local_segments = decide_segments(
        candidates=candidates,
        mode=mode,
        protect_dialogue=protect_dialogue,
    )

    return {
        "segments": shift_segments_to_global(local_segments, chunk["offset"]),
        "processed_frames": processed_frames,
    }
