from __future__ import annotations

import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.core.settings import get_settings
from app.services.ollama_client import get_llm_client

LENGTH_TO_MAX_LENGTH = {
    "short": 120,
    "medium": 240,
    "long": 400,
}

SUMMARY_TYPE_INSTRUCTIONS = {
    "tldr": "Write a concise TL;DR in 2 to 3 sentences.",
    "bullet": "Write a short bullet list of the most important points.",
    "executive": "Write an executive summary with the main outcome, key context, and notable risks.",
    "action_items": "Extract concrete action items or next steps as bullet points.",
    "explain_like_12": "Explain the content in simple language for a 12-year-old.",
}

LENGTH_INSTRUCTIONS = {
    "short": "Keep it brief and dense.",
    "medium": "Keep it moderately detailed.",
    "long": "Allow more detail while staying focused on the main ideas.",
}

SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a precise summarization assistant. Follow the requested format, stay faithful to the source, and do not invent facts.",
        ),
        (
            "human",
            "Task: {summary_instruction}\n"
            "Length guidance: {length_instruction}\n"
            "Hard limit: keep the response within about {max_length} characters.\n"
            "Return only the summary.\n\n"
            "Source text:\n{text}",
        ),
    ]
)

OUTPUT_PARSER = StrOutputParser()


def _split_sentences(text: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    ]


def _clip_text(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."


class SummaryService:
    def __init__(self, llm_client=None):
        self._llm_client = llm_client or get_llm_client()
        self._settings = get_settings()

    def _provider_name(self) -> str:
        return self._llm_client.__class__.__name__.removesuffix("Client").lower()

    def _model_name(self) -> str | None:
        return getattr(self._llm_client, "model", None)

    def _generation_kwargs(self, max_length: int) -> dict[str, int]:
        approx_tokens = max(32, min(self._settings.SUMMARY_MAX_TOKENS, max_length // 4))
        provider = self._provider_name()
        if provider == "ollama":
            return {"num_predict": approx_tokens}
        if provider == "openai":
            return {"max_tokens": approx_tokens}
        return {}

    async def summarize(
        self,
        *,
        text: str,
        summary_type: str,
        length: str,
        max_length: int,
        options: dict | None = None,
    ) -> dict[str, object]:
        provider = self._provider_name()
        model = self._model_name()
        sentences = _split_sentences(text)
        if not sentences:
            return {
                "summary": "",
                "provider": provider,
                "model": model,
                "approach": "langchain",
                "fallback_used": False,
            }

        try:
            chain = (
                SUMMARY_PROMPT
                | self._llm_client.get_chat_model(**self._generation_kwargs(max_length))
                | OUTPUT_PARSER
            )
            summary = await chain.ainvoke(
                {
                    "summary_instruction": SUMMARY_TYPE_INSTRUCTIONS.get(
                        summary_type,
                        SUMMARY_TYPE_INSTRUCTIONS["tldr"],
                    ),
                    "length_instruction": LENGTH_INSTRUCTIONS.get(
                        length,
                        LENGTH_INSTRUCTIONS["short"],
                    ),
                    "max_length": max_length,
                    "text": text.strip(),
                }
            )
            summary = _clip_text(str(summary).strip(), max_length)
            if not summary:
                raise ValueError("Empty summary returned by LLM")
            return {
                "summary": summary,
                "provider": provider,
                "model": model,
                "approach": "langchain",
                "fallback_used": False,
            }
        except Exception:
            del options
            if summary_type in {"bullet", "action_items"}:
                summary = _clip_text(
                    "\n".join(f"- {sentence}" for sentence in sentences[:3]),
                    max_length,
                )
            else:
                summary = _clip_text(" ".join(sentences[:3]), max_length)

        return {
            "summary": summary,
            "provider": provider,
            "model": model,
            "approach": "extractive",
            "fallback_used": True,
        }


def get_summary_service() -> SummaryService:
    return SummaryService()