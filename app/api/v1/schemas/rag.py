# app/schemas/rag.py

from pydantic import BaseModel, Field


class RagSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: list[str] | None = None


class RagSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str | None = None
    chunk_index: int
    content: str
    score: float


class RagSearchResponse(BaseModel):
    query: str
    top_k: int
    results: list[RagSearchResult]