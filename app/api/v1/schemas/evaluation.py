from pydantic import BaseModel, Field


class RetrievalEvaluationRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: list[str] | None = None

    expected_document_ids: list[str] | None = None
    expected_chunk_ids: list[str] | None = None


class RetrievalEvaluationResponse(BaseModel):
    query: str
    top_k: int
    retrieved_chunk_ids: list[str]
    retrieved_document_ids: list[str]

    expected_document_ids: list[str] | None
    expected_chunk_ids: list[str] | None

    document_hit_rate: float | None
    document_precision_at_k: float | None
    document_recall_at_k: float | None
    document_mrr: float | None

    chunk_hit_rate: float | None
    chunk_precision_at_k: float | None
    chunk_recall_at_k: float | None
    chunk_mrr: float | None


class RagSummaryEvaluationRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: list[str] | None = None

    summary_type: str = "tldr"
    length: str = "medium"

    expected_document_ids: list[str] | None = None
    expected_chunk_ids: list[str] | None = None
    include_llm_judge: bool = False


class RagSummaryEvaluationResponse(BaseModel):
    query: str
    summary: str
    sources: list[dict]
    retrieval_metrics: RetrievalEvaluationResponse
    llm_judge: dict | None = None