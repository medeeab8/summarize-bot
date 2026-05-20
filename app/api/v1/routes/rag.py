# app/api/v1/routes/rag.py

import logging

from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas.rag import RagSearchRequest, RagSearchResponse
from app.services.rag_retriever import RagRetrieverService

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.api.v1.schemas.rag import RagReindexRequest, RagReindexResponse
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
    
@router.post(
    "/reindex",
    response_model=RagReindexResponse,
    status_code=status.HTTP_200_OK,
)
async def reindex_documents(
    payload: RagReindexRequest,
    db: AsyncSession = Depends(get_db),
):
    retriever = RagRetrieverService()

    document_ids = payload.document_ids

    stmt = (
        select(DocumentChunk, Document)
        .join(Document, DocumentChunk.document_id == Document.id)
        .order_by(DocumentChunk.document_id, DocumentChunk.chunk_index)
    )

    if document_ids:
        stmt = stmt.where(Document.id.in_(document_ids))

    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return {
            "message": "No document chunks found to reindex",
            "indexed_chunks": 0,
            "indexed_documents": 0,
            "missing_document_ids": document_ids or [],
        }

    found_document_ids = {document.id for _, document in rows}
    missing_document_ids = []

    if document_ids:
        missing_document_ids = [
            document_id
            for document_id in document_ids
            if document_id not in found_document_ids
        ]

    chunks = [
        {
            "chunk_id": chunk.id,
            "document_id": document.id,
            "document_name": document.original_filename,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
        }
        for chunk, document in rows
    ]

    await retriever.index_chunks(chunks)

    await db.execute(
        update(Document)
        .where(Document.id.in_(found_document_ids))
        .values(status="indexed")
    )
    await db.commit()

    return {
        "message": "Documents reindexed successfully",
        "indexed_chunks": len(chunks),
        "indexed_documents": len(found_document_ids),
        "missing_document_ids": missing_document_ids,
    }