from __future__ import annotations

import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.core.settings import get_settings
from app.services.ollama_client import get_llm_client

LENGTH_TO_MAX_LENGTH = {
    "short": 150,
    "medium": 500,
    "long": 1000,
}

SUMMARY_TYPE_INSTRUCTIONS = {
    "tldr": "Write a concise TL;DR in 2 to 3 sentences.",
    "bullet": "Write a short bullet list of the most important points.",
    "executive": "Write an executive summary with the main outcome, key context, and notable risks.",
    "explain_like_12": "Explain the content in simple language for a 12-year-old.",
}

LENGTH_INSTRUCTIONS = {
    "short": "Keep it brief and dense.",
    "medium": "Keep it moderately detailed.",
    "long": "Allow more detail while staying focused on the main ideas.",
    "custom": "Follow the requested character target closely while staying coherent.",
}

SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a precise summarization assistant. Follow the requested format, stay faithful to the source, do not invent facts, and end cleanly without trailing ellipses.",
        ),
        (
            "human",
            "Task: {summary_instruction}\n"
            "Length guidance: {length_instruction}\n"
            "Hard limit: keep the response within about {max_length} characters.\n"
            "Return only the summary. End with a complete, concise final sentence or bullet, never with '...' or '…'.\n\n"
            "Source text:\n{text}",
        ),
    ]
)

OUTPUT_PARSER = StrOutputParser()
CHUNK_TARGET_CHARS = 6000
CHUNK_SUMMARY_MAX_LENGTH = 600
MAX_REDUCTION_PASSES = 4


def count_characters(text: str) -> int:
    return len(text)


def _split_sentences(text: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    ]


def _split_text_chunks(text: str, target_chars: int) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text.strip()) if paragraph.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current_parts: list[str] = []
    current_length = 0

    def flush_current() -> None:
        nonlocal current_parts, current_length
        if current_parts:
            chunks.append("\n\n".join(current_parts))
            current_parts = []
            current_length = 0

    for paragraph in paragraphs:
        if len(paragraph) > target_chars:
            flush_current()
            sentences = _split_sentences(paragraph)
            if not sentences:
                chunks.append(paragraph[:target_chars])
                continue

            sentence_parts: list[str] = []
            sentence_length = 0
            for sentence in sentences:
                addition = len(sentence) + (1 if sentence_parts else 0)
                if sentence_parts and sentence_length + addition > target_chars:
                    chunks.append(" ".join(sentence_parts))
                    sentence_parts = [sentence]
                    sentence_length = len(sentence)
                elif len(sentence) > target_chars:
                    words = sentence.split()
                    word_parts: list[str] = []
                    word_length = 0
                    for word in words:
                        word_addition = len(word) + (1 if word_parts else 0)
                        if word_parts and word_length + word_addition > target_chars:
                            chunks.append(" ".join(word_parts))
                            word_parts = [word]
                            word_length = len(word)
                        else:
                            word_parts.append(word)
                            word_length += word_addition
                    if word_parts:
                        chunks.append(" ".join(word_parts))
                    sentence_parts = []
                    sentence_length = 0
                else:
                    sentence_parts.append(sentence)
                    sentence_length += addition
            if sentence_parts:
                chunks.append(" ".join(sentence_parts))
            continue

        addition = len(paragraph) + (2 if current_parts else 0)
        if current_parts and current_length + addition > target_chars:
            flush_current()
        current_parts.append(paragraph)
        current_length += len(paragraph) + (2 if len(current_parts) > 1 else 0)

    flush_current()
    return chunks


def _clip_text(text: str, max_length: int) -> str:
    text = text.strip() # removes whitespace from the beginning and end
    # the two re.sub(...) calls remove unwanted trailing endings: the first strips off ellipses like ... or …, and the second removes leftover trailing separators such as spaces, commas, colons, semicolons, and dash characters.
    text = re.sub(r"(?:\s*(?:\.{3,}|…))+\s*$", "", text)
    text = re.sub(r"[\s,:;\-–—]+$", "", text)

    if len(text) > max_length:
        clipped = text[:max_length].rstrip()

        sentence_boundary = max(clipped.rfind(". "), clipped.rfind("! "), clipped.rfind("? "))
        if sentence_boundary >= max_length // 2:
            clipped = clipped[: sentence_boundary + 1].rstrip()
        else:
            newline_boundary = clipped.rfind("\n")
            word_boundary = clipped.rfind(" ")
            boundary = max(newline_boundary, word_boundary)
            if boundary > 0:
                clipped = clipped[:boundary].rstrip()

        text = re.sub(r"(?:\s*(?:\.{3,}|…))+\s*$", "", clipped)
        text = re.sub(r"[\s,:;\-–—]+$", "", text)

    if not text:
        return ""

    is_bullet_list = any(
        line.lstrip().startswith(("- ", "* ", "• "))
        for line in text.splitlines()
        if line.strip()
    )
    if is_bullet_list:
        return text

    if text[-1] not in ".!?)]}\"'”’":
        text += "."

    return text


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
            async def run_langchain_summary(source_text: str, limit: int) -> str:
                chain = (
                    SUMMARY_PROMPT
                    | self._llm_client.get_chat_model(**self._generation_kwargs(limit))
                    | OUTPUT_PARSER
                )
                generated_summary = await chain.ainvoke(
                    {
                        "summary_instruction": SUMMARY_TYPE_INSTRUCTIONS.get(
                            summary_type,
                            SUMMARY_TYPE_INSTRUCTIONS["tldr"],
                        ),
                        "length_instruction": LENGTH_INSTRUCTIONS.get(
                            length,
                            LENGTH_INSTRUCTIONS["short"],
                        ),
                        "max_length": limit,
                        "text": source_text.strip(),
                    }
                )
                generated_summary = _clip_text(str(generated_summary).strip(), limit)
                if not generated_summary:
                    raise ValueError("Empty summary returned by LLM")
                return generated_summary

            current_text = text.strip()
            for _ in range(MAX_REDUCTION_PASSES):
                if len(current_text) <= CHUNK_TARGET_CHARS:
                    summary = await run_langchain_summary(current_text, max_length)
                    break

                chunks = _split_text_chunks(current_text, CHUNK_TARGET_CHARS)
                if len(chunks) <= 1:
                    summary = await run_langchain_summary(current_text[:CHUNK_TARGET_CHARS], max_length)
                    break

                chunk_max_length = min(CHUNK_SUMMARY_MAX_LENGTH, max(200, max_length * 2))
                chunk_summaries = []
                for chunk in chunks:
                    chunk_summaries.append(await run_langchain_summary(chunk, chunk_max_length))
                current_text = "\n\n".join(chunk_summaries)
            else:
                summary = await run_langchain_summary(current_text[:CHUNK_TARGET_CHARS], max_length)

            return {
                "summary": summary,
                "provider": provider,
                "model": model,
                "approach": "langchain",
                "fallback_used": False,
            }
        except Exception:
            del options
            if summary_type == "bullet":
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