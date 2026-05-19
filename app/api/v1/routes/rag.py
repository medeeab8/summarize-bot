# app/api/v1/routes/rag.py

import logging

from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas.rag import RagSearchRequest, RagSearchResponse
from app.services.rag_retriever import RagRetrieverService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post(
    "/search",
    response_model=RagSearchResponse,
    status_code=status.HTTP_200_OK,
)
async def search_documents(payload: RagSearchRequest):
    retriever = RagRetrieverService()

    try:
        results = await retriever.search(
            query=payload.query,
            top_k=payload.top_k,
            document_ids=payload.document_ids,
        )

        return {
            "query": payload.query,
            "top_k": payload.top_k,
            "results": results,
        }

    except Exception as exc:
        logger.exception("RAG search failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search documents",
        ) from exc