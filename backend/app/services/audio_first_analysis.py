from __future__ import annotations

import re
import subprocess
import wave
from pathlib import Path
from typing import Literal

import webrtcvad

SILENCE_START_RE = re.compile(r"silence_start:\s*([0-9.]+)")
SILENCE_END_RE = re.compile(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)")


def analyze_audio_timeline(
    input_path: str,
    duration_seconds: float,
    mode: Literal["cut", "smart"],
    protect_dialogue: bool = True,
) -> list[dict]:
    silence_candidates = _detect_silence_candidates(input_path)
    if not silence_candidates:
        return []

    wav_path = _extract_analysis_wav(input_path)
    try:
        with wave.open(str(wav_path), "rb") as wf:
            sample_rate = wf.getframerate()
            if sample_rate != 16000:
                raise ValueError("Expected 16kHz mono wav")
            audio_bytes = wf.readframes(wf.getnframes())
    finally:
        try:
            wav_path.unlink(missing_ok=True)
        except Exception:
            pass

    segments: list[dict] = []
    for start, end in silence_candidates:
        start = max(0.0, start)
        end = min(float(duration_seconds), end)
        segment_duration = end - start
        if segment_duration < 0.35:
            continue

        speech_ratio = _speech_ratio_for_window(audio_bytes, sample_rate, start, end)
        if protect_dialogue and speech_ratio > 0.12:
            continue

        if mode == "cut":
            action = "cut"
            confidence = _clamp(0.86 + min(segment_duration / 20.0, 0.11) - min(speech_ratio, 0.08), 0.55, 0.99)
            reasons = ["silence_detected", "aggressive_cut_mode"]
        else:
            if segment_duration >= 1.4:
                action = "cut"
                reasons = ["long_silence", "smart_mode_cut"]
                confidence = _clamp(0.84 + min(segment_duration / 18.0, 0.12) - min(speech_ratio, 0.08), 0.55, 0.99)
            else:
                action = "speedup"
                reasons = ["short_pause", "smart_mode_speedup"]
                confidence = _clamp(0.74 + min(segment_duration / 10.0, 0.10) - min(speech_ratio, 0.08), 0.50, 0.95)

        if speech_ratio > 0.02:
            reasons.append("low_speech")

        segments.append(
            {
                "start": round(start, 3),
                "end": round(end, 3),
                "action": action,
                "confidence": round(confidence, 3),
                "reasons": reasons,
            }
        )

    return _merge_adjacent_segments(segments)


def _detect_silence_candidates(input_path: str) -> list[tuple[float, float]]:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        input_path,
        "-af",
        "silencedetect=noise=-38dB:d=0.45",
        "-f",
        "null",
        "-",
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    stderr = completed.stderr or ""

    start_buffer: list[float] = []
    intervals: list[tuple[float, float]] = []

    for line in stderr.splitlines():
        m1 = SILENCE_START_RE.search(line)
        if m1:
            start_buffer.append(float(m1.group(1)))
            continue
        m2 = SILENCE_END_RE.search(line)
        if m2 and start_buffer:
            end = float(m2.group(1))
            start = start_buffer.pop(0)
            if end > start:
                intervals.append((start, end))

    return _merge_intervals(intervals, max_gap=0.18, min_duration=0.40)


def _extract_analysis_wav(input_path: str) -> Path:
    wav_path = Path(input_path).with_suffix(".analysis.wav")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(wav_path),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0 or not wav_path.exists():
        raise RuntimeError(f"wav extract failed: {completed.stderr[-1200:]}")
    return wav_path


def _speech_ratio_for_window(audio_bytes: bytes, sample_rate: int, start: float, end: float) -> float:
    vad = webrtcvad.Vad(2)
    bytes_per_second = sample_rate * 2
    start_byte = max(0, int(start * bytes_per_second))
    end_byte = min(len(audio_bytes), int(end * bytes_per_second))
    chunk = audio_bytes[start_byte:end_byte]

    frame_ms = 30
    bytes_per_frame = int(sample_rate * (frame_ms / 1000.0) * 2)
    voiced = 0
    total = 0
    for i in range(0, len(chunk) - bytes_per_frame + 1, bytes_per_frame):
        frame = chunk[i : i + bytes_per_frame]
        try:
            if vad.is_speech(frame, sample_rate):
                voiced += 1
            total += 1
        except Exception:
            continue
    return (voiced / total) if total else 0.0


def _merge_intervals(intervals: list[tuple[float, float]], max_gap: float, min_duration: float) -> list[tuple[float, float]]:
    if not intervals:
        return []
    intervals = sorted(intervals)
    merged = [list(intervals[0])]
    for start, end in intervals[1:]:
        prev = merged[-1]
        if start - prev[1] <= max_gap:
            prev[1] = max(prev[1], end)
        else:
            merged.append([start, end])
    return [(round(s, 3), round(e, 3)) for s, e in merged if (e - s) >= min_duration]


def _merge_adjacent_segments(segments: list[dict]) -> list[dict]:
    if not segments:
        return []
    segments = sorted(segments, key=lambda x: x["start"])
    merged = [segments[0].copy()]
    for seg in segments[1:]:
        prev = merged[-1]
        same_action = prev["action"] == seg["action"]
        close_gap = seg["start"] - prev["end"] <= 0.15
        if same_action and close_gap:
            prev["end"] = seg["end"]
            prev["confidence"] = round(max(prev["confidence"], seg["confidence"]), 3)
            prev["reasons"] = sorted(set(prev["reasons"] + seg["reasons"]))
        else:
            merged.append(seg.copy())
    return merged


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
