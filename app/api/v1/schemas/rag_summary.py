from typing import Literal

from pydantic import BaseModel, Field


class RagSummaryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: list[str] | None = None
    summary_type: Literal["tldr", "technical", "bullet_points", "executive"] = "tldr"
    length: Literal["short", "medium", "long"] = "medium"


class RagSummarySource(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str | None = None
    chunk_index: int
    score: float


class RagSummaryResponse(BaseModel):
    query: str
    summary: str
    sources: list[RagSummarySource]