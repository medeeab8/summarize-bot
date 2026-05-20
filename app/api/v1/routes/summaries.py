from fastapi import Depends
from fastapi import APIRouter
from fastapi import HTTPException

from app.api.v1.schemas.summaries import SummarizeRequest
from app.api.v1.schemas.summaries import SummarizeResponse
from app.core.settings import get_settings
from app.services.summarizer import count_characters
from app.services.summarizer import LENGTH_TO_MAX_LENGTH
from app.services.summarizer import SummaryService
from app.services.summarizer import get_summary_service

router = APIRouter()

@router.post(
    "/summarize",
    response_model=SummarizeResponse,
    tags=["Summarization"],
    summary="Summarize text with the configured LLM",
)
async def summarize(
    payload: SummarizeRequest,
    summary_service: SummaryService = Depends(get_summary_service),
) -> SummarizeResponse:
    settings = get_settings()
    input_length = len(payload.text)
    original_character_count = count_characters(payload.text)

    if payload.length == "custom":
        requested_max_length = payload.max_length
    else:
        requested_max_length = payload.max_length or LENGTH_TO_MAX_LENGTH[payload.length]

    max_length = min(requested_max_length, input_length, settings.SUMMARY_MAX_LENGTH)

    try:
        result = await summary_service.summarize(
            text=payload.text,
            summary_type=payload.summary_type,
            length=payload.length,
            max_length=max_length,
            options=payload.options,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    summarized_text = result["summary"]
    
    return SummarizeResponse(
        summary=summarized_text,
        original_text=payload.text,
        summarized_text=summarized_text,
        original_character_count=original_character_count,
        max_length=max_length,
        summary_type=payload.summary_type,
        length=payload.length,
        options=payload.options,
        provider=result["provider"],
        model=result["model"],
        approach=result["approach"],
        fallback_used=result["fallback_used"],
    )