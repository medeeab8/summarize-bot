from fastapi import APIRouter, HTTPException
import httpx
from openai import OpenAIError, RateLimitError
from app.core.settings import get_settings
from app.services.ollama_client import get_llm_client
from app.core.logging import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/ping", tags=["LLM"], summary="Ping LLM API")
async def ping_llm():
    client = get_llm_client()
    settings = get_settings()
    logger.info("Pinging LLM API...")
    try:
        if hasattr(client, "ping"):
            logger.info("Sending ping via configured LLM client...")
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
        detail = "Could not connect to Ollama."
        if settings.LLM_PROVIDER.lower() == "ollama":
            detail = f"Could not connect to Ollama at {settings.OLLAMA_API_URL}."
            if settings.OLLAMA_API_URL == "http://ollama:11434":
                detail += " Make sure the Compose ollama service is running and the model has been pulled into that container."
            elif "host.docker.internal" in settings.OLLAMA_API_URL:
                detail += " If the API is running in Docker on Linux, either expose the host Ollama listener on 0.0.0.0:11434 or switch OLLAMA_API_URL to http://ollama:11434 and use the Compose ollama service."
        raise HTTPException(
            status_code=502,
            detail=detail,
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected LLM ping error")
        raise HTTPException(
            status_code=502,
            detail=f"LLM request failed: {exc}",
        ) from exc