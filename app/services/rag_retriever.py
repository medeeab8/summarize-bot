from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService


class RagRetrieverService:
    def __init__(self) -> None:
        # Retrieval always pairs an embedding generator with the vector store
        # that persists and searches those embeddings.
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()

    async def index_chunk(
        self,
        chunk_id: str,
        content: str,
        document_id: str,
        document_name: str,
        chunk_index: int,
    ) -> None:
        # Turn the raw chunk text into a vector before sending it to Qdrant.
        vector = await self.embedding_service.embed_text(content)

        await self.vector_store.upsert_chunk(
            chunk_id=chunk_id,
            vector=vector,
            content=content,
            document_id=document_id,
            document_name=document_name,
            chunk_index=chunk_index,
        )

    async def index_chunks(
        self,
        chunks: list[dict],
    ) -> None:
        # Embed all chunk texts first so the vector store receives one payload per
        # chunk with both metadata and vector values.
        texts = [chunk["content"] for chunk in chunks]
        vectors = await self.embedding_service.embed_texts(texts)

        qdrant_chunks = []

        for chunk, vector in zip(chunks, vectors):
            qdrant_chunks.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "document_id": chunk["document_id"],
                    "document_name": chunk["document_name"],
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                    "vector": vector,
                }
            )

        await self.vector_store.upsert_chunks(qdrant_chunks)

    async def search(
        self,
        query: str,
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[dict]:
        # Search starts by embedding the user query into the same vector space as
        # the indexed chunks.
        query_vector = await self.embedding_service.embed_text(query)

        return await self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
            document_ids=document_ids,
        )