from __future__ import annotations

import re

LENGTH_TO_MAX_LENGTH = {
    "short": 120,
    "medium": 240,
    "long": 400,
}


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
    async def summarize(
        self,
        *,
        text: str,
        summary_type: str,
        length: str,
        max_length: int,
        options: dict | None = None,
    ) -> dict[str, object]:
        del length, options

        sentences = _split_sentences(text)
        if not sentences:
            summary = ""
        elif summary_type == "bullet":
            summary = _clip_text(
                "\n".join(f"- {sentence}" for sentence in sentences[:3]),
                max_length,
            )
        elif summary_type == "action_items":
            summary = _clip_text(
                "\n".join(f"- {sentence}" for sentence in sentences[:3]),
                max_length,
            )
        else:
            summary = _clip_text(" ".join(sentences[:3]), max_length)

        return {
            "summary": summary,
            "approach": "simple",
            "fallback_used": False,
        }


def get_summary_service() -> SummaryService:
    return SummaryService()