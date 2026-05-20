import logging

from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas.evaluation import (
    RagSummaryEvaluationRequest,
    RagSummaryEvaluationResponse,
    RetrievalEvaluationRequest,
    RetrievalEvaluationResponse,
)
from app.services.rag_evaluation_service import RagEvaluationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post(
    "/retrieval",
    response_model=RetrievalEvaluationResponse,
    status_code=status.HTTP_200_OK,
)
async def evaluate_retrieval(payload: RetrievalEvaluationRequest):
    service = RagEvaluationService()

    try:
        return await service.evaluate_retrieval(
            query=payload.query,
            top_k=payload.top_k,
            document_ids=payload.document_ids,
            expected_document_ids=payload.expected_document_ids,
            expected_chunk_ids=payload.expected_chunk_ids,
        )

    except Exception as exc:
        logger.exception("Retrieval evaluation failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate retrieval",
        ) from exc


@router.post(
    "/rag-summary",
    response_model=RagSummaryEvaluationResponse,
    status_code=status.HTTP_200_OK,
)
async def evaluate_rag_summary(payload: RagSummaryEvaluationRequest):
    service = RagEvaluationService()

    try:
        return await service.evaluate_rag_summary(
            query=payload.query,
            top_k=payload.top_k,
            document_ids=payload.document_ids,
            summary_type=payload.summary_type,
            length=payload.length,
            expected_document_ids=payload.expected_document_ids,
            expected_chunk_ids=payload.expected_chunk_ids,
            include_llm_judge=payload.include_llm_judge,
        )

    except Exception as exc:
        logger.exception("RAG summary evaluation failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate RAG summary",
        ) from exc