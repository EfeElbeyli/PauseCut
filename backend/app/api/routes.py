from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from uuid import uuid4

from app.adapters.youtube_adapter import YouTubeAdapter
from app.models.schemas import AnalyzeLinkRequest, JobSummary, SegmentSuggestion
from app.services.background_runner import dispatch_analysis_job
from app.services.final_render_service import render_final_video
from app.services.job_store import create_job, get_job as db_get_job, update_job
from app.services.render_service import render_preview
from app.services.time_utils import now_iso

router = APIRouter()


def _normalize_mode(mode: str) -> str:
    mapping = {
        "aggressive": "cut",
        "balanced": "smart",
        "conservative": "smart",
        "cut": "cut",
        "smart": "smart",
    }
    return mapping.get(mode, "smart")


@router.get("/")
def root() -> dict:
    return {"name": "PauseCut API", "version": "1.7.0", "status": "ok"}


@router.get("/health")
def health() -> dict:
    return {"status": "healthy"}


@router.post("/analyze-link", response_model=JobSummary)
def analyze_link(payload: AnalyzeLinkRequest) -> JobSummary:
    url = str(payload.url)
    youtube = YouTubeAdapter()

    if not youtube.validate_url(url):
        raise HTTPException(status_code=400, detail="Currently only valid YouTube links are supported.")

    job_id = str(uuid4())
    timestamp = now_iso()

    job = {
        "job_id": job_id,
        "status": "queued",
        "source_url": url,
        "mode": _normalize_mode(payload.mode),
        "protect_dialogue": payload.protect_dialogue,
        "preview_only": payload.preview_only,
        "platform": None,
        "title": None,
        "duration_seconds": None,
        "estimated_time_saved_seconds": None,
        "progress": 0,
        "activity_text": "Queued",
        "analysis_stage": "Queued",
        "error_message": None,
        "preview_status": "not_started",
        "preview_path": None,
        "preview_error": None,
        "final_status": "not_started",
        "final_path": None,
        "final_error": None,
        "segments": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    create_job(job)
    dispatch_analysis_job(job_id)

    created = db_get_job(job_id)
    return JobSummary(**{k: created[k] for k in JobSummary.model_fields.keys()})


@router.get("/job/{job_id}", response_model=JobSummary)
def get_job(job_id: str) -> JobSummary:
    job = db_get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobSummary(**{k: job[k] for k in JobSummary.model_fields.keys()})


@router.get("/job/{job_id}/detail")
def get_job_detail(job_id: str) -> dict:
    job = db_get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/job/{job_id}/segments", response_model=list[SegmentSuggestion])
def get_segments(job_id: str) -> list[SegmentSuggestion]:
    job = db_get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return [SegmentSuggestion(**segment) for segment in job["segments"]]


@router.put("/job/{job_id}/segments")
def put_segments(job_id: str, segments: list[SegmentSuggestion]) -> dict:
    job = db_get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_job(
        job_id,
        {
            "segments": [s.model_dump() for s in segments],
            "preview_status": "not_started",
            "preview_path": None,
            "preview_error": None,
            "updated_at": now_iso(),
        },
    )
    return {"status": "ok", "count": len(segments)}


@router.get("/job/{job_id}/summary")
def get_summary(job_id: str) -> dict:
    job = db_get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job["job_id"],
        "title": job["title"],
        "platform": job["platform"],
        "duration_seconds": job["duration_seconds"],
        "estimated_time_saved_seconds": job["estimated_time_saved_seconds"],
        "segments_found": len(job["segments"]),
        "mode": job["mode"],
        "protect_dialogue": job["protect_dialogue"],
        "preview_only": job["preview_only"],
        "status": job["status"],
        "progress": job["progress"],
        "activity_text": job.get("activity_text"),
        "analysis_stage": job.get("analysis_stage"),
        "error_message": job["error_message"],
        "preview_status": job.get("preview_status"),
        "preview_error": job.get("preview_error"),
        "final_status": job.get("final_status"),
        "final_error": job.get("final_error"),
    }


@router.post("/job/{job_id}/preview")
def build_preview(job_id: str, force: bool = False) -> dict:
    job = db_get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "completed":
        raise HTTPException(status_code=409, detail="Job analysis is not completed yet.")

    update_job(job_id, {"preview_status": "processing", "preview_error": None, "updated_at": now_iso()})
    try:
        result = render_preview(job, force=force)
        update_job(
            job_id,
            {
                "preview_status": "ready",
                "preview_path": result["preview_path"],
                "preview_error": None,
                "updated_at": now_iso(),
            },
        )
    except Exception as exc:
        update_job(job_id, {"preview_status": "failed", "preview_error": str(exc), "updated_at": now_iso()})
        raise HTTPException(status_code=500, detail=f"Preview render failed: {str(exc)}")

    return {
        "job_id": job_id,
        "status": "ready",
        "preview_path": result["preview_path"],
        "clip_count": result["clip_count"],
        "cached": result.get("cached", False),
        "download_url": f"/job/{job_id}/preview/download",
    }


@router.get("/job/{job_id}/preview/download")
def download_preview(job_id: str):
    job = db_get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    preview_path = job.get("preview_path")
    if not preview_path:
        raise HTTPException(status_code=404, detail="Preview not built yet.")
    return FileResponse(path=preview_path, media_type="video/mp4", filename=f"{job_id}_preview.mp4")


@router.post("/job/{job_id}/final")
def build_final(job_id: str, force: bool = False) -> dict:
    job = db_get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "completed":
        raise HTTPException(status_code=409, detail="Job analysis is not completed yet.")

    update_job(job_id, {"final_status": "processing", "final_error": None, "updated_at": now_iso()})
    try:
        result = render_final_video(job, force=force)
        update_job(
            job_id,
            {
                "final_status": "ready",
                "final_path": result["final_path"],
                "final_error": None,
                "updated_at": now_iso(),
            },
        )
    except Exception as exc:
        update_job(job_id, {"final_status": "failed", "final_error": str(exc), "updated_at": now_iso()})
        raise HTTPException(status_code=500, detail=f"Final render failed: {str(exc)}")

    return {
        "job_id": job_id,
        "status": "ready",
        "final_path": result["final_path"],
        "clip_count": result["clip_count"],
        "cached": result.get("cached", False),
        "download_url": f"/job/{job_id}/final/download",
    }


@router.get("/job/{job_id}/final/download")
def download_final(job_id: str):
    job = db_get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    final_path = job.get("final_path")
    if not final_path:
        raise HTTPException(status_code=404, detail="Final render not built yet.")
    return FileResponse(path=final_path, media_type="video/mp4", filename=f"{job_id}_final.mp4")
