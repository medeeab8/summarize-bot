from fastapi import APIRouter
from . import health
from . import summaries
from app.api.v1.openai import ping

router = APIRouter()
router.include_router(health.router, prefix="", tags=["Health"])
router.include_router(summaries.router, prefix="", tags=["Summarization"])
router.include_router(ping.router, prefix="", tags=["OpenAI"])