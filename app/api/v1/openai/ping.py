from fastapi import APIRouter, HTTPException
from openai import OpenAIError, RateLimitError
from app.services.ollama_client import get_llm_client
from app.core.logging import logging

router = APIRouter() 
logger = logging.getLogger(__name__)

@router.get("/ping", tags=["LLM"], summary="Ping LLM API")
async def ping_llm():
    client = get_llm_client()
    print(client)
    print(f"client hasattr: {hasattr(client, "responses")}")
    logger.info("Pinging LLM API...")
    try:
        # OpenAI client
        """This kind of check is useful when you are working with objects whose type or structure might vary, or when you want to write code that can handle different types of clients in a flexible way. For example, if some client objects have a responses attribute (such as a list or method) and others do not, this check allows you to conditionally execute code that depends on the presence of that attribute, avoiding potential AttributeError exceptions."""
        if hasattr(client, "responses"):
            logger.info("Detected OpenAI client, sending ping...")
            response = await client.responses.create(
                model="gpt-4o-mini",
                input="ping",
            )
            return {"status": "success", "response_id": response.id}
        # Ollama client
        else:
            logger.info("Detected Ollama client, sending ping...")
            response = await client.create_response(model="llama2", prompt="ping")
            return {"status": "success", "response": response}
    
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
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}")
        raise HTTPException(
            status_code=502,
            detail=f"LLM request failed: {exc}",
        ) from exc