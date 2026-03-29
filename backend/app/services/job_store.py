import json
import sqlite3
from pathlib import Path

DB_DIR = Path("app/db")
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "pausecut.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            source_url TEXT NOT NULL,
            mode TEXT NOT NULL,
            protect_dialogue INTEGER NOT NULL,
            preview_only INTEGER NOT NULL,
            platform TEXT,
            title TEXT,
            duration_seconds INTEGER,
            estimated_time_saved_seconds INTEGER,
            progress INTEGER NOT NULL DEFAULT 0,
            activity_text TEXT,
            analysis_stage TEXT,
            error_message TEXT,
            preview_status TEXT,
            preview_path TEXT,
            preview_error TEXT,
            final_status TEXT,
            final_path TEXT,
            final_error TEXT,
            segments_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()

    for column_def in [
        "activity_text TEXT",
        "analysis_stage TEXT",
        "preview_status TEXT",
        "preview_path TEXT",
        "preview_error TEXT",
        "final_status TEXT",
        "final_path TEXT",
        "final_error TEXT",
    ]:
        try:
            cur.execute(f"ALTER TABLE jobs ADD COLUMN {column_def}")
        except Exception:
            pass

    conn.commit()
    conn.close()


def create_job(job: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO jobs (
            job_id, status, source_url, mode, protect_dialogue, preview_only,
            platform, title, duration_seconds, estimated_time_saved_seconds,
            progress, activity_text, analysis_stage, error_message,
            preview_status, preview_path, preview_error,
            final_status, final_path, final_error,
            segments_json, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job["job_id"],
            job["status"],
            job["source_url"],
            job["mode"],
            int(job["protect_dialogue"]),
            int(job["preview_only"]),
            job.get("platform"),
            job.get("title"),
            job.get("duration_seconds"),
            job.get("estimated_time_saved_seconds"),
            job.get("progress", 0),
            job.get("activity_text"),
            job.get("analysis_stage"),
            job.get("error_message"),
            job.get("preview_status"),
            job.get("preview_path"),
            job.get("preview_error"),
            job.get("final_status"),
            job.get("final_path"),
            job.get("final_error"),
            json.dumps(job.get("segments", [])),
            job["created_at"],
            job["updated_at"],
        ),
    )
    conn.commit()
    conn.close()


def get_job(job_id: str) -> dict | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "job_id": row["job_id"],
        "status": row["status"],
        "source_url": row["source_url"],
        "mode": row["mode"],
        "protect_dialogue": bool(row["protect_dialogue"]),
        "preview_only": bool(row["preview_only"]),
        "platform": row["platform"],
        "title": row["title"],
        "duration_seconds": row["duration_seconds"],
        "estimated_time_saved_seconds": row["estimated_time_saved_seconds"],
        "progress": row["progress"],
        "activity_text": row["activity_text"],
        "analysis_stage": row["analysis_stage"],
        "error_message": row["error_message"],
        "preview_status": row["preview_status"],
        "preview_path": row["preview_path"],
        "preview_error": row["preview_error"],
        "final_status": row["final_status"],
        "final_path": row["final_path"],
        "final_error": row["final_error"],
        "segments": json.loads(row["segments_json"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def update_job(job_id: str, updates: dict) -> bool:
    current = get_job(job_id)
    if not current:
        return False

    merged = {**current, **updates}
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE jobs
        SET status = ?, source_url = ?, mode = ?, protect_dialogue = ?,
            preview_only = ?, platform = ?, title = ?, duration_seconds = ?,
            estimated_time_saved_seconds = ?, progress = ?, activity_text = ?, analysis_stage = ?, error_message = ?,
            preview_status = ?, preview_path = ?, preview_error = ?,
            final_status = ?, final_path = ?, final_error = ?,
            segments_json = ?, created_at = ?, updated_at = ?
        WHERE job_id = ?
        """,
        (
            merged["status"],
            merged["source_url"],
            merged["mode"],
            int(merged["protect_dialogue"]),
            int(merged["preview_only"]),
            merged.get("platform"),
            merged.get("title"),
            merged.get("duration_seconds"),
            merged.get("estimated_time_saved_seconds"),
            merged.get("progress", 0),
            merged.get("activity_text"),
            merged.get("analysis_stage"),
            merged.get("error_message"),
            merged.get("preview_status"),
            merged.get("preview_path"),
            merged.get("preview_error"),
            merged.get("final_status"),
            merged.get("final_path"),
            merged.get("final_error"),
            json.dumps(merged.get("segments", [])),
            merged["created_at"],
            merged["updated_at"],
            job_id,
        ),
    )
    conn.commit()
    conn.close()
    return True
