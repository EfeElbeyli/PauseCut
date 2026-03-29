from app.adapters.youtube_adapter import YouTubeAdapter
from app.services.audio_first_analysis import analyze_audio_timeline
from app.services.decision_engine import estimate_time_saved
from app.services.download_source import ensure_local_source
from app.services.job_store import get_job, update_job
from app.services.metadata_service import fetch_video_metadata
from app.services.render_service import render_preview
from app.services.time_utils import now_iso


def _set_state(job_id: str, progress: int, stage: str, activity: str, **extra):
    payload = {
        "progress": progress,
        "analysis_stage": stage,
        "activity_text": activity,
        "updated_at": now_iso(),
    }
    payload.update(extra)
    update_job(job_id, payload)


def run_analysis_pipeline(job_id: str) -> None:
    job = get_job(job_id)
    if not job:
        raise ValueError(f"Job not found: {job_id}")

    try:
        _set_state(
            job_id,
            5,
            "Preparing",
            "Starting audio-first analysis",
            status="processing",
            preview_status="not_started",
            preview_error=None,
        )

        adapter = YouTubeAdapter()
        if not adapter.validate_url(job["source_url"]):
            raise ValueError("Invalid or unsupported YouTube URL")

        metadata = fetch_video_metadata(job["source_url"])
        duration = metadata.get("duration_seconds") or 0

        update_job(
            job_id,
            {
                "platform": metadata.get("platform"),
                "title": metadata.get("title"),
                "duration_seconds": duration,
                "progress": 15,
                "analysis_stage": "Metadata ready",
                "activity_text": "Metadata fetched",
                "updated_at": now_iso(),
            },
        )

        _set_state(job_id, 28, "Downloading source", "Preparing local analysis file")
        local_input = ensure_local_source(job_id, job["source_url"])

        _set_state(job_id, 52, "Audio scan", "Detecting silent intervals")
        segments = analyze_audio_timeline(
            input_path=local_input,
            duration_seconds=float(duration),
            mode=job["mode"],
            protect_dialogue=job["protect_dialogue"],
        )

        saved = estimate_time_saved(segments)
        update_job(
            job_id,
            {
                "estimated_time_saved_seconds": saved,
                "segments": segments,
                "progress": 76,
                "analysis_stage": "Edited video build queued",
                "activity_text": f"Built {len(segments)} edit segments",
                "preview_status": "processing",
                "updated_at": now_iso(),
            },
        )

        current_job = get_job(job_id)
        _set_state(job_id, 86, "Building edited video", "Rendering watchable result", preview_status="processing")
        result = render_preview(current_job, force=True)

        update_job(
            job_id,
            {
                "status": "completed",
                "preview_status": "ready",
                "preview_path": result["preview_path"],
                "preview_error": None,
                "estimated_time_saved_seconds": saved,
                "segments": segments,
                "progress": 100,
                "analysis_stage": "Completed",
                "activity_text": "Edited video ready to watch",
                "updated_at": now_iso(),
            },
        )

    except Exception as exc:
        update_job(
            job_id,
            {
                "status": "failed",
                "preview_status": "failed",
                "preview_error": str(exc),
                "error_message": str(exc),
                "analysis_stage": "Failed",
                "activity_text": "Analysis failed",
                "updated_at": now_iso(),
            },
        )
        raise
