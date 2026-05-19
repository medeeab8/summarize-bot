from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    PointStruct,
    VectorParams,
)

from app.core.settings import get_settings


class VectorStoreService:
    def __init__(self) -> None:
        # Read the active vector-store configuration once per service instance.
        self.settings = get_settings()
        self.client = AsyncQdrantClient(url=self.settings.QDRANT_URL)
        self.collection_name = self.settings.QDRANT_COLLECTION_NAME

    async def ensure_collection_exists(self) -> None:
        # Every write/search path first verifies that the target collection exists
        # with the expected vector size.
        collections = await self.client.get_collections()
        collection_names = [collection.name for collection in collections.collections]

        if self.collection_name in collection_names:
            return

        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.settings.embedding_dimension,
                distance=Distance.COSINE,
            ),
        )

    async def upsert_chunk(
        self,
        chunk_id: str,
        vector: list[float],
        content: str,
        document_id: str,
        document_name: str,
        chunk_index: int,
    ) -> None:
        # Store one chunk with both its vector and searchable metadata payload.
        await self.ensure_collection_exists()

        point = PointStruct(
            id=chunk_id,
            vector=vector,
            payload={
                "chunk_id": chunk_id,
                "document_id": document_id,
                "document_name": document_name,
                "chunk_index": chunk_index,
                "content": content,
            },
        )

        await self.client.upsert(
            collection_name=self.collection_name,
            points=[point],
        )

    async def upsert_chunks(
        self,
        chunks: list[dict],
    ) -> None:
        # Bulk upsert uses the same payload shape as single-chunk indexing.
        await self.ensure_collection_exists()

        points = [
            PointStruct(
                id=chunk["chunk_id"],
                vector=chunk["vector"],
                payload={
                    "chunk_id": chunk["chunk_id"],
                    "document_id": chunk["document_id"],
                    "document_name": chunk["document_name"],
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                },
            )
            for chunk in chunks
        ]

        await self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[dict]:
        # Search the nearest vectors and then reshape the Qdrant response into a
        # compact API-friendly result structure.
        await self.ensure_collection_exists()

        # Document filtering is wired into the method signature, but the current
        # implementation returns the top matches across the whole collection.
        del document_ids

        result = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )

        if not result.points:
            return []

        return [
            {
                "chunk_id": point.payload.get("chunk_id"),
                "document_id": point.payload.get("document_id"),
                "document_name": point.payload.get("document_name"),
                "chunk_index": point.payload.get("chunk_index"),
                "content": point.payload.get("content"),
                "score": point.score,
            }
            for point in result.points
        ]