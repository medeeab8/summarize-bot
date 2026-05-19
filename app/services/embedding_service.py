from ollama import AsyncClient
from ollama import ResponseError

from app.core.settings import get_settings


class EmbeddingService:
    def __init__(self) -> None:
        # Load runtime configuration first so the embedding client points at the
        # same Ollama instance used by the rest of the application.
        self.settings = get_settings()
        self.client = AsyncClient(host=self.settings.OLLAMA_API_URL)
        self.model = self.settings.embedding_model

    async def _embed_with_fallback(self, text: str) -> list[float]:
        try:
            # Prefer the newer bulk-capable embedding endpoint when the server
            # supports it.
            response = await self.client.embed(
                model=self.model,
                input=text,
            )
            return response["embeddings"][0]
        except ResponseError as exc:
            if exc.status_code != 404:
                raise

            # Fall back to the legacy endpoint for older Ollama versions.
            response = await self.client.embeddings(
                model=self.model,
                prompt=text,
            )
            return response["embedding"]

    async def embed_text(self, text: str) -> list[float]:
        # Single-text embedding is the common path for query vectors.
        return await self._embed_with_fallback(text)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        # Batch embedding reuses the same compatibility path for each chunk.
        return [await self._embed_with_fallback(text) for text in texts]