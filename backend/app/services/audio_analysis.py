from __future__ import annotations

from typing import List


def analyze_audio(probe: dict, scenes: list[dict], protect_dialogue: bool) -> list[dict]:
    """
    Analyze speech density per scene.

    Strategy:
    1. Prefer WebRTC VAD on a 16k mono WAV if available.
    2. Fallback to librosa RMS-based low-energy estimate.
    3. Final fallback to synthetic values.
    """
    audio_path = probe.get("audio_path")

    if audio_path:
        try:
            return _analyze_with_webrtcvad(audio_path, scenes, protect_dialogue)
        except Exception:
            pass

        try:
            return _analyze_with_librosa(audio_path, scenes, protect_dialogue)
        except Exception:
            pass

    return _fallback_audio(scenes, protect_dialogue)


def _analyze_with_webrtcvad(audio_path: str, scenes: list[dict], protect_dialogue: bool) -> list[dict]:
    import wave
    import webrtcvad

    vad = webrtcvad.Vad(2)

    with wave.open(audio_path, "rb") as wf:
        sample_rate = wf.getframerate()
        if sample_rate != 16000:
            raise ValueError("Expected 16kHz WAV for WebRTC VAD")
        audio_bytes = wf.readframes(wf.getnframes())

    frame_ms = 30
    bytes_per_frame = int(sample_rate * (frame_ms / 1000.0) * 2)  # int16 mono
    total_duration = len(audio_bytes) / (sample_rate * 2)

    scene_results = []
    for idx, scene in enumerate(scenes):
        start_byte = int((scene["start"] / total_duration) * len(audio_bytes))
        end_byte = int((scene["end"] / total_duration) * len(audio_bytes))
        chunk = audio_bytes[start_byte:end_byte]

        voiced = 0
        total = 0
        for i in range(0, len(chunk) - bytes_per_frame + 1, bytes_per_frame):
            frame = chunk[i:i + bytes_per_frame]
            try:
                is_speech = vad.is_speech(frame, sample_rate)
            except Exception:
                continue
            voiced += int(is_speech)
            total += 1

        speech_ratio = (voiced / total) if total else 0.0
        scene_results.append(
            {
                "scene_index": idx,
                "speech_ratio": round(float(speech_ratio), 4),
                "low_speech": speech_ratio < 0.20,
                "protect_dialogue": protect_dialogue,
                "source": "webrtcvad",
            }
        )

    return scene_results


def _analyze_with_librosa(audio_path: str, scenes: list[dict], protect_dialogue: bool) -> list[dict]:
    import librosa
    import numpy as np

    y, sr = librosa.load(audio_path, sr=16000, mono=True)
    total_duration = len(y) / sr if sr else 1.0

    results = []
    for idx, scene in enumerate(scenes):
        start = int((scene["start"] / total_duration) * len(y))
        end = int((scene["end"] / total_duration) * len(y))
        segment = y[start:end]

        if len(segment) == 0:
            speech_ratio = 0.0
        else:
            frame = 512
            hop = 256
            rms = librosa.feature.rms(y=segment, frame_length=frame, hop_length=hop)[0]
            threshold = max(0.01, float(np.percentile(rms, 60)) * 0.7)
            active = float(np.mean(rms > threshold)) if len(rms) else 0.0
            speech_ratio = active

        results.append(
            {
                "scene_index": idx,
                "speech_ratio": round(float(speech_ratio), 4),
                "low_speech": speech_ratio < 0.20,
                "protect_dialogue": protect_dialogue,
                "source": "librosa_rms",
            }
        )

    return results


def _fallback_audio(scenes: list[dict], protect_dialogue: bool) -> list[dict]:
    results = []
    for idx, _scene in enumerate(scenes):
        speech_ratio = 0.1 if idx % 3 == 0 else 0.65
        results.append(
            {
                "scene_index": idx,
                "speech_ratio": speech_ratio,
                "low_speech": speech_ratio < 0.2,
                "protect_dialogue": protect_dialogue,
                "source": "fallback",
            }
        )
    return results
