from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.exceptions.documents import (
    DocumentTextExtractionError,
    DocumentTooLargeError,
    EmptyDocumentError,
    UnsupportedDocumentTypeError,
)
from app.api.v1.schemas.documents import DocumentUploadResponse
from app.services.document_ingestion import DocumentIngestionService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentIngestionService()

    try:
        documents = []

        for file in files:
            document = await service.upload_document(file=file, db=db)
            documents.append(document)

        return {
            "message": f"{len(documents)} documents uploaded successfully",
            "documents": documents,
        }
    
    except UnsupportedDocumentTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc

    except DocumentTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc

    except EmptyDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except DocumentTextExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc