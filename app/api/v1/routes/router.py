from fastapi import APIRouter
from . import health
from . import summaries
from . import documents
from . import rag
from . import rag_summaries
from . import evaluations
from app.api.v1.openai import ping

router = APIRouter()
router.include_router(health.router, prefix="", tags=["Health"])
router.include_router(summaries.router, prefix="", tags=["Summarization"])
router.include_router(ping.router, prefix="", tags=["Ping API"])
router.include_router(documents.router, prefix="", tags=["Documents"])
router.include_router(rag.router, prefix="", tags=["RAG"])
router.include_router(rag_summaries.router, prefix="", tags=["RAG"])
router.include_router(evaluations.router, prefix="", tags=["Evaluations"])