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
from .documents_text_extractor import DocumentTextExtractor


class DocumentIngestionService:
    def __init__(self) -> None:
        self.extractor = DocumentTextExtractor()
        self.settings = get_settings()

    async def upload_document(
        self,
        file: UploadFile,
        db: AsyncSession,
    ) -> Document:
        original_filename = file.filename or "unknown"
        extension = self._get_extension(original_filename)

        self._validate_extension(extension)

        document_id = str(uuid.uuid4())

        stored_filename = f"{document_id}.{extension}"

        upload_dir = Path(self.settings.UPLOAD_DIR)
        extracted_text_dir = Path(self.settings.EXTRACTED_TEXT_DIR)

        upload_dir.mkdir(parents=True, exist_ok=True)
        extracted_text_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / stored_filename
        extracted_text_path = extracted_text_dir / f"{document_id}.txt"

        file_size = await self._save_file(file, file_path)

        self._validate_file_size(file_size)

        extracted_text = self.extractor.extract(
            file_path=str(file_path),
            extension=extension,
        )

        if not extracted_text:
            raise EmptyDocumentError("Uploaded document has no extractable text")

        extracted_text_path.write_text(extracted_text, encoding="utf-8")

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

        db.add(document)
        await db.commit()
        await db.refresh(document)

        return document

    def _get_extension(self, filename: str) -> str:
        if "." not in filename:
            raise UnsupportedDocumentTypeError("File must have an extension")

        return filename.rsplit(".", 1)[-1].lower()

    def _validate_extension(self, extension: str) -> None:
        if extension not in self.settings.ALLOWED_DOCUMENT_EXTENSTIONS:
            raise UnsupportedDocumentTypeError(
                f"Unsupported file type: {extension}"
            )

    def _validate_file_size(self, file_size: int) -> None:
        max_size_bytes = self.settings.MAX_UPLOAD_SIZE_MS * 1024 * 1024

        if file_size > max_size_bytes:
            raise DocumentTooLargeError(
                f"File is too large. Max size is {self.settings.MAX_UPLOAD_SIZE_MS} MB"
            )

    async def _save_file(self, file: UploadFile, destination: Path) -> int:
        size = 0

        async with aiofiles.open(destination, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                await out_file.write(chunk)

        return size