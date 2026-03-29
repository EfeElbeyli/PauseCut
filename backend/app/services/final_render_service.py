from __future__ import annotations

import os
import subprocess
from pathlib import Path

from app.services.download_source import ensure_local_source


FINAL_DIR = Path("app/db/final_renders")
FINAL_DIR.mkdir(parents=True, exist_ok=True)


def render_final_video(job: dict, force: bool = False) -> dict:
    existing_path = job.get("final_path")
    if existing_path and os.path.exists(existing_path) and not force:
        return {
            "final_path": existing_path,
            "clip_count": 0,
            "input_path": None,
            "cached": True,
        }

    source_url = job["source_url"]
    duration = float(job.get("duration_seconds") or 0)
    if duration <= 0:
        raise ValueError("Job does not have a valid duration for final rendering.")

    local_input = ensure_local_source(job["job_id"], source_url)
    if not os.path.exists(local_input):
        raise ValueError("Could not prepare a local video file for final rendering.")

    segments = sorted(job.get("segments", []), key=lambda x: x["start"])
    workdir = FINAL_DIR / job["job_id"]
    workdir.mkdir(parents=True, exist_ok=True)

    intervals = _build_intervals(duration, segments)
    if not intervals:
        raise ValueError("No intervals to render.")

    clip_paths = []
    for idx, interval in enumerate(intervals):
        clip_path = workdir / f"final_clip_{idx:04d}.mp4"
        _render_interval(
            input_path=local_input,
            start=interval["start"],
            end=interval["end"],
            action=interval["action"],
            output_path=str(clip_path),
        )
        if not clip_path.exists():
            raise FileNotFoundError(f"Expected final clip not created: {clip_path}")
        clip_paths.append(clip_path)

    concat_list = workdir / "final_concat.txt"
    with open(concat_list, "w", encoding="utf-8") as fh:
        for clip in clip_paths:
            fh.write(f"file '{clip.resolve().as_posix()}'\n")

    final_path = FINAL_DIR / f"{job['job_id']}_final.mp4"
    _concat_clips(str(concat_list), str(final_path))

    if not final_path.exists():
        raise FileNotFoundError("Final video was not created.")

    return {
        "final_path": str(final_path),
        "clip_count": len(clip_paths),
        "input_path": local_input,
        "cached": False,
    }


def _build_intervals(duration: float, segments: list[dict]) -> list[dict]:
    intervals = []
    cursor = 0.0

    for seg in segments:
        start = max(0.0, float(seg["start"]))
        end = min(duration, float(seg["end"]))
        action = seg["action"]

        if start > cursor:
            intervals.append({"start": cursor, "end": start, "action": "keep"})

        if action == "speedup" and end > start:
            intervals.append({"start": start, "end": end, "action": "speedup"})

        cursor = max(cursor, end)

    if cursor < duration:
        intervals.append({"start": cursor, "end": duration, "action": "keep"})

    return [x for x in intervals if x["end"] - x["start"] > 0.15]


def _render_interval(input_path: str, start: float, end: float, action: str, output_path: str) -> None:
    if action == "keep":
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", f"{start:.3f}",
            "-to", f"{end:.3f}",
            "-i", input_path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_path,
        ]
        _run_or_raise(cmd, "final keep interval render failed")
        return

    if action == "speedup":
        av_cmd = [
            "ffmpeg",
            "-y",
            "-ss", f"{start:.3f}",
            "-to", f"{end:.3f}",
            "-i", input_path,
            "-filter_complex",
            "[0:v]setpts=PTS/2[v];[0:a]atempo=2.0[a]",
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_path,
        ]
        completed = subprocess.run(av_cmd, capture_output=True, text=True)
        if completed.returncode == 0 and os.path.exists(output_path):
            return

        video_only_cmd = [
            "ffmpeg",
            "-y",
            "-ss", f"{start:.3f}",
            "-to", f"{end:.3f}",
            "-i", input_path,
            "-vf", "setpts=PTS/2",
            "-an",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-movflags", "+faststart",
            output_path,
        ]
        _run_or_raise(video_only_cmd, "final speedup interval render failed")
        return

    raise ValueError(f"Unsupported interval action: {action}")


def _concat_clips(concat_file: str, output_path: str) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output_path,
    ]
    _run_or_raise(cmd, "final concat failed")


def _run_or_raise(cmd: list[str], label: str) -> None:
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"{label}: {completed.stderr[-2400:]}")
