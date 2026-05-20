import json
import re

from app.services.ollama_client import get_llm_client
from app.services.rag_retriever import RagRetrieverService
from app.services.rag_summary_service import RagSummaryService


class RagEvaluationService:
    def __init__(self) -> None:
        self.retriever = RagRetrieverService()
        self.summary_service = RagSummaryService()
        self.llm_client = get_llm_client()

    async def evaluate_retrieval(
        self,
        query: str,
        top_k: int = 5,
        document_ids: list[str] | None = None,
        expected_document_ids: list[str] | None = None,
        expected_chunk_ids: list[str] | None = None,
    ) -> dict:
        results = await self.retriever.search(
            query=query,
            top_k=top_k,
            document_ids=document_ids,
        )

        retrieved_chunk_ids = [result["chunk_id"] for result in results]
        retrieved_document_ids = [result["document_id"] for result in results]

        document_metrics = self._calculate_metrics(
            retrieved_ids=retrieved_document_ids,
            expected_ids=expected_document_ids,
        )

        chunk_metrics = self._calculate_metrics(
            retrieved_ids=retrieved_chunk_ids,
            expected_ids=expected_chunk_ids,
        )

        return {
            "query": query,
            "top_k": top_k,
            "retrieved_chunk_ids": retrieved_chunk_ids,
            "retrieved_document_ids": retrieved_document_ids,
            "expected_document_ids": expected_document_ids,
            "expected_chunk_ids": expected_chunk_ids,
            "document_hit_rate": document_metrics["hit_rate"],
            "document_precision_at_k": document_metrics["precision_at_k"],
            "document_recall_at_k": document_metrics["recall_at_k"],
            "document_mrr": document_metrics["mrr"],
            "chunk_hit_rate": chunk_metrics["hit_rate"],
            "chunk_precision_at_k": chunk_metrics["precision_at_k"],
            "chunk_recall_at_k": chunk_metrics["recall_at_k"],
            "chunk_mrr": chunk_metrics["mrr"],
        }

    async def evaluate_rag_summary(
        self,
        query: str,
        top_k: int = 5,
        document_ids: list[str] | None = None,
        summary_type: str = "tldr",
        length: str = "medium",
        expected_document_ids: list[str] | None = None,
        expected_chunk_ids: list[str] | None = None,
        include_llm_judge: bool = False,
    ) -> dict:
        summary_response = await self.summary_service.summarize(
            query=query,
            top_k=top_k,
            document_ids=document_ids,
            summary_type=summary_type,
            length=length,
        )

        retrieval_metrics = await self.evaluate_retrieval(
            query=query,
            top_k=top_k,
            document_ids=document_ids,
            expected_document_ids=expected_document_ids,
            expected_chunk_ids=expected_chunk_ids,
        )

        llm_judge = None

        if include_llm_judge:
            retrieved_chunks = await self.retriever.search(
                query=query,
                top_k=top_k,
                document_ids=document_ids,
            )

            llm_judge = await self._judge_summary_groundedness(
                query=query,
                summary=summary_response["summary"],
                chunks=retrieved_chunks,
            )

        return {
            "query": query,
            "summary": summary_response["summary"],
            "sources": summary_response["sources"],
            "retrieval_metrics": retrieval_metrics,
            "llm_judge": llm_judge,
        }

    def _calculate_metrics(
        self,
        retrieved_ids: list[str],
        expected_ids: list[str] | None,
    ) -> dict:
        if not expected_ids:
            return {
                "hit_rate": None,
                "precision_at_k": None,
                "recall_at_k": None,
                "mrr": None,
            }

        expected_set = set(expected_ids)

        if not retrieved_ids:
            return {
                "hit_rate": 0.0,
                "precision_at_k": 0.0,
                "recall_at_k": 0.0,
                "mrr": 0.0,
            }

        relevant_retrieved = [
            retrieved_id
            for retrieved_id in retrieved_ids
            if retrieved_id in expected_set
        ]

        hit_rate = 1.0 if relevant_retrieved else 0.0
        precision_at_k = len(relevant_retrieved) / len(retrieved_ids)
        recall_at_k = len(set(relevant_retrieved)) / len(expected_set)

        mrr = 0.0
        for index, retrieved_id in enumerate(retrieved_ids, start=1):
            if retrieved_id in expected_set:
                mrr = 1.0 / index
                break

        return {
            "hit_rate": hit_rate,
            "precision_at_k": precision_at_k,
            "recall_at_k": recall_at_k,
            "mrr": mrr,
        }

    async def _judge_summary_groundedness(
        self,
        query: str,
        summary: str,
        chunks: list[dict],
    ) -> dict:
        context = "\n\n---\n\n".join(
            f"Document: {chunk.get('document_name')}\n"
            f"Chunk ID: {chunk.get('chunk_id')}\n"
            f"Content:\n{chunk.get('content')}"
            for chunk in chunks
        )

        prompt = f"""
You are evaluating a RAG summary.

User query:
{query}

Retrieved context:
{context}

Generated summary:
{summary}

Return only valid JSON with this structure:
{{
  "groundedness_score": 0.0,
  "relevance_score": 0.0,
  "completeness_score": 0.0,
  "hallucination_risk": "low|medium|high",
  "notes": "brief explanation"
}}

Scoring:
- groundedness_score: Is the summary supported by the context?
- relevance_score: Does the summary answer the user query?
- completeness_score: Does it cover the key context?
""".strip()

        response = await self.llm_client.create_response(prompt)
        content = response["content"]

        return self._safe_parse_json(content)

    def _safe_parse_json(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", text, flags=re.DOTALL)

        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return {
            "groundedness_score": None,
            "relevance_score": None,
            "completeness_score": None,
            "hallucination_risk": "unknown",
            "notes": text,
        }