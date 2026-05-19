import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import get_settings
from app.exceptions.documents import (
    DocumentTooLargeError,
    EmptyDocumentError,
    UnsupportedDocumentTypeError,
)
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from .documents_text_extractor import DocumentTextExtractor
from app.services.rag_retriever import RagRetrieverService
from app.services.text_chunker import TextChunker


class DocumentIngestionService:
    def __init__(self) -> None:
        # Keep the ingestion pipeline components on the service so a single
        # upload request can move from raw file to indexed chunks end to end.
        self.settings = get_settings()
        self.extractor = DocumentTextExtractor()
        self.chunker = TextChunker()
        self.rag_retriever = RagRetrieverService()

    async def upload_document(
        self,
        file: UploadFile,
        db: AsyncSession,
    ) -> Document:
        # Normalize the file metadata first so validation and storage paths are
        # built from a stable extension and generated document id.
        original_filename = file.filename or "unknown"
        extension = self._get_extension(original_filename)

        self._validate_extension(extension)

        document_id = str(uuid.uuid4())
        stored_filename = f"{document_id}.{extension}"

        upload_dir = Path(self.settings.UPLOAD_DIR)
        extracted_text_dir = Path(self.settings.EXTRACTED_TEXT_DIR)

        # Ensure the on-disk storage layout exists before streaming the upload.
        upload_dir.mkdir(parents=True, exist_ok=True)
        extracted_text_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / stored_filename
        extracted_text_path = extracted_text_dir / f"{document_id}.txt"

        # Persist the raw file first, then extract text from the stored copy.
        file_size = await self._save_file(file, file_path)

        extracted_text = self.extractor.extract(
            file_path=str(file_path),
            extension=extension,
        )

        if not extracted_text:
            raise EmptyDocumentError("Uploaded document has no extractable text")

        # Save the extracted text so later processing can reuse it without
        # reopening the original upload.
        extracted_text_path.write_text(extracted_text, encoding="utf-8")

        # Create the main document row before generating per-chunk records.
        document = Document(
            id=document_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_type=file.content_type,
            file_extension=extension,
            file_size_bytes=file_size,
            file_path=str(file_path),
            extracted_text_path=str(extracted_text_path),
            status="processed",
        )

        # Split the extracted text into retrieval-sized chunks for vector
        # indexing and later search.
        chunks = self.chunker.chunk_text(extracted_text)

        if not chunks:
            raise EmptyDocumentError("No chunks could be created from this document")

        document_chunks = [
            DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=document_id,
                chunk_index=index,
                content=chunk,
                character_count=len(chunk),
            )
            for index, chunk in enumerate(chunks)
        ]

        # Commit the relational data first so document and chunk ids are durable
        # before the external vector index is updated.
        db.add(document)
        db.add_all(document_chunks)

        await db.commit()
        await db.refresh(document)

        # Mirror the chunk data into the vector store so RAG search can query it.
        await self.rag_retriever.index_chunks(
            [
                {
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "document_name": document.original_filename,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                }
                for chunk in document_chunks
            ]
        )

        # Mark the document as fully indexed only after vector storage succeeds.
        document.status = "indexed"

        await db.commit()
        await db.refresh(document)

        return document

    def _get_extension(self, filename: str) -> str:
        if "." not in filename:
            raise UnsupportedDocumentTypeError("File must have an extension")

        return filename.rsplit(".", 1)[-1].lower()

    def _validate_extension(self, extension: str) -> None:
        # Reject unsupported types early so we do not write unusable files.
        if extension not in self.settings.ALLOWED_DOCUMENT_EXTENSIONS:
            raise UnsupportedDocumentTypeError(
                f"Unsupported file type: {extension}"
            )

    async def _save_file(self, file: UploadFile, destination: Path) -> int:
        size = 0
        max_size_bytes = self.settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        async with aiofiles.open(destination, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)

                # Stop oversized uploads while the file is still streaming so we
                # do not keep partial files on disk.
                if size > max_size_bytes:
                    destination.unlink(missing_ok=True)
                    raise DocumentTooLargeError(
                        f"File is too large. Max size is {self.settings.MAX_UPLOAD_SIZE_MB} MB"
                    )

                await out_file.write(chunk)

        return size