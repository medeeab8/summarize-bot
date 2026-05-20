# app/services/rag_summary_service.py

from app.services.ollama_client import get_llm_client
from app.services.rag_retriever import RagRetrieverService


class RagSummaryService:
    def __init__(self) -> None:
        self.retriever = RagRetrieverService()
        self.llm_client = get_llm_client()

    async def summarize(
        self,
        query: str,
        top_k: int = 5,
        document_ids: list[str] | None = None,
        summary_type: str = "tldr",
        length: str = "medium",
    ) -> dict:
        retrieved_chunks = await self.retriever.search(
            query=query,
            top_k=top_k,
            document_ids=document_ids,
        )

        if not retrieved_chunks:
            return {
                "query": query,
                "summary": "I could not find relevant information in the uploaded documents.",
                "sources": [],
            }

        prompt = self._build_prompt(
            query=query,
            chunks=retrieved_chunks,
            summary_type=summary_type,
            length=length,
        )

        response = await self.llm_client.create_response(prompt)

        sources = [
            {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "document_name": chunk.get("document_name"),
                "chunk_index": chunk["chunk_index"],
                "score": chunk["score"],
            }
            for chunk in retrieved_chunks
        ]

        return {
            "query": query,
            "summary": response["content"].strip(),
            "sources": sources,
        }

    def _build_prompt(
        self,
        query: str,
        chunks: list[dict],
        summary_type: str,
        length: str,
    ) -> str:
        context_blocks = []

        for index, chunk in enumerate(chunks, start=1):
            context_blocks.append(
                f"""
[Source {index}]
Document: {chunk.get("document_name")}
Chunk ID: {chunk.get("chunk_id")}
Score: {chunk.get("score")}

Content:
{chunk.get("content")}
""".strip()
            )

        context = "\n\n---\n\n".join(context_blocks)

        return f"""
You are a source-grounded AI summarizer.

Rules:
- Use only the provided document context.
- Do not invent information.
- If the context is not enough, say that the uploaded documents do not contain enough information.
- Write a {length} summary.
- Summary style: {summary_type}.
- Be clear and concise.

User request:
{query}

Relevant document context:
{context}

Now generate the summary using only the context above. Output the summary only, without mentions of details of how the user wanted it done, and also no other irrelevent intro phrases, just the summary.
If the files uploaded are unrelated and the user ask for a summary of the link between them, state that there is no connection clearly and provide a summary of each document instead, but do not mention the file name.
""".strip()