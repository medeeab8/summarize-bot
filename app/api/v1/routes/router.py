from fastapi import APIRouter
from . import health
from . import summaries

router = APIRouter()
router.include_router(health.router, prefix="", tags=["Health"])
router.include_router(summaries.router, prefix="", tags=["Summarization"])