from pydantic import BaseModel, Field, HttpUrl
from typing import Literal, Optional

AnalysisMode = Literal["cut", "smart", "conservative", "balanced", "aggressive"]


class AnalyzeLinkRequest(BaseModel):
    url: HttpUrl
    mode: AnalysisMode = "smart"
    protect_dialogue: bool = True
    preview_only: bool = True


class SegmentSuggestion(BaseModel):
    start: float = Field(...)
    end: float = Field(...)
    action: Literal["cut", "speedup"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasons: list[str]


class JobSummary(BaseModel):
    job_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    source_url: str
    mode: str
    protect_dialogue: bool
    preview_only: bool
    platform: Optional[str] = None
    title: Optional[str] = None
    duration_seconds: Optional[int] = None
    estimated_time_saved_seconds: Optional[int] = None
    created_at: str
    updated_at: str
