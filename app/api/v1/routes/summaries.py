from fastapi import APIRouter
from fastapi import Depends

from app.api.v1.schemas.summaries import SummarizeRequest
from app.services.summarizer import LENGTH_TO_MAX_LENGTH
from app.services.summarizer import SummaryService
from app.services.summarizer import get_summary_service

router = APIRouter()

@router.post("/summarize", tags=["Summarization"], summary="Summarize Endpoint")
async def summarize(
    payload: SummarizeRequest,
    summary_service: SummaryService = Depends(get_summary_service),
):
    max_length = payload.max_length or LENGTH_TO_MAX_LENGTH[payload.length]
    result = await summary_service.summarize(
        text=payload.text,
        summary_type=payload.summary_type,
        length=payload.length,
        max_length=max_length,
        options=payload.options,
    )
    summarized_text = result["summary"]
    return {
        "summary": summarized_text,
        "original_text": payload.text,
        "summarized_text": summarized_text,
        "max_length": max_length,
        "summary_type": payload.summary_type,
        "length": payload.length,
        "options": payload.options,
        "approach": result["approach"],
        "fallback_used": result["fallback_used"],
    }