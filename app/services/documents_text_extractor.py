from pathlib import Path

from pypdf import PdfReader

from app.exceptions.documents import DocumentTextExtractionError


class DocumentTextExtractor:
    def extract(self, file_path: str, extension: str) -> str:
        extension = extension.lower()

        if extension == "pdf":
            return self._extract_pdf(file_path)

        if extension in {"txt", "md"}:
            return self._extract_plain_text(file_path)

        raise DocumentTextExtractionError(
            f"Unsupported file extension for extraction: {extension}"
        )

    def _extract_pdf(self, file_path: str) -> str:
        try:
            reader = PdfReader(file_path)

            pages: list[str] = []

            for page in reader.pages:
                text = page.extract_text() or ""
                pages.append(text)

            return "\n\n".join(pages).strip()

        except Exception as exc:
            raise DocumentTextExtractionError(
                "Failed to extract text from PDF"
            ) from exc

    def _extract_plain_text(self, file_path: str) -> str:
        try:
            return Path(file_path).read_text(encoding="utf-8").strip()

        except UnicodeDecodeError:
            return Path(file_path).read_text(encoding="latin-1").strip()

        except Exception as exc:
            raise DocumentTextExtractionError(
                "Failed to extract text from document"
            ) from exc