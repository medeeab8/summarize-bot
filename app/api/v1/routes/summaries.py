import re

from fastapi import APIRouter

from app.api.v1.schemas.summaries import SummarizeRequest

router = APIRouter()

LENGTH_TO_MAX_LENGTH = {
    "short": 120,
    "medium": 240,
    "long": 400,
}


def build_summary(text: str, summary_type: str, max_length: int) -> str:
    trimmed_text = text.strip()
    if not trimmed_text:
        return ""

    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", trimmed_text)
        if sentence.strip()
    ]

    if summary_type == "bullet":
        bullets = []
        total_chars = 0
        for sentence in sentences[:5]:
            bullet = f"- {sentence}"
            if bullets and total_chars + len(bullet) + 1 > max_length:
                break
            bullets.append(bullet)
            total_chars += len(bullet) + 1
        return "\n".join(bullets)[:max_length].rstrip()

    summary = " ".join(sentences[:3]) if sentences else trimmed_text
    if len(summary) <= max_length:
        return summary
    return summary[: max_length - 3].rstrip() + "..."

@router.post("/summarize", tags=["Summarization"], summary="Summarize Endpoint")
async def summarize(payload: SummarizeRequest):
    max_length = payload.max_length or LENGTH_TO_MAX_LENGTH[payload.length]
    summarized_text = build_summary(payload.text, payload.summary_type, max_length)

    return {
        "summary": summarized_text,
        "original_text": payload.text,
        "summarized_text": summarized_text,
        "max_length": max_length,
        "summary_type": payload.summary_type,
        "length": payload.length,
        "options": payload.options,
    }