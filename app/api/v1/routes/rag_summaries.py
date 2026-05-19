import logging

from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas.rag_summary import RagSummaryRequest, RagSummaryResponse
from app.services.rag_summary_service import RagSummaryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.post(
    "/rag",
    response_model=RagSummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def summarize_with_rag(payload: RagSummaryRequest):
    service = RagSummaryService()

    try:
        return await service.summarize(
            query=payload.query,
            top_k=payload.top_k,
            document_ids=payload.document_ids,
            summary_type=payload.summary_type,
            length=payload.length,
        )

    except Exception as exc:
        logger.exception("RAG summary failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate RAG summary",
        ) from exc