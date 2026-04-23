from fastapi import APIRouter, HTTPException
import httpx
from openai import OpenAIError, RateLimitError
from app.services.ollama_client import get_llm_client
from app.core.logging import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/ping", tags=["LLM"], summary="Ping LLM API")
async def ping_llm():
    client = get_llm_client()
    logger.info("Pinging LLM API...")
    try:
        if hasattr(client, "responses"):
            logger.info("Detected OpenAI client, sending ping...")
            response = await client.responses.create(
                model="gpt-4o-mini",
                input="ping",
            )
            return {"status": "success", "response_id": response.id}

        if hasattr(client, "ping"):
            logger.info("Detected Ollama client, sending ping...")
            response = await client.ping()
            return {"status": "success", "response": response}

        raise HTTPException(status_code=500, detail="Unsupported LLM client configuration.")
    except RateLimitError as exc:
        logger.error(f"Rate limit error: {exc}")
        raise HTTPException(
            status_code=503,
            detail="OpenAI quota exceeded or rate limited.",
        ) from exc
    except OpenAIError as exc:
        logger.error(f"OpenAI error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="OpenAI request failed.",
        ) from exc
    except httpx.TimeoutException as exc:
        logger.error(f"LLM timeout: {exc}")
        raise HTTPException(
            status_code=504,
            detail="Ollama request timed out.",
        ) from exc
    except httpx.HTTPStatusError as exc:
        logger.error(f"Ollama HTTP error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Ollama request failed.",
        ) from exc
    except httpx.RequestError as exc:
        logger.error(f"Ollama connection error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Could not connect to Ollama.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected LLM ping error")
        raise HTTPException(
            status_code=502,
            detail=f"LLM request failed: {exc}",
        ) from exc