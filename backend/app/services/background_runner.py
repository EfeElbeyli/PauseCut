import threading

from app.workers.pipeline import run_analysis_pipeline


def dispatch_analysis_job(job_id: str) -> None:
    """
    Lightweight threaded background execution for MVP.
    Later this can be replaced with Celery, RQ, Dramatiq, etc.
    """
    thread = threading.Thread(target=run_analysis_pipeline, args=(job_id,), daemon=True)
    thread.start()
