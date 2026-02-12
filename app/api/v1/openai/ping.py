from fastapi import APIRouter, HTTPException
from openai import OpenAIError, RateLimitError
from app.services.openai_client import get_openai_client 

router = APIRouter() 

@router.get("/ping", tags=["OpenAI"], summary="Ping OpenAI API") 
async def ping_openai(): 
    client = get_openai_client()
    try:
        response = await client.responses.create(
            model="gpt-4o-mini",
            input="ping",
        )
    except RateLimitError as exc:
        raise HTTPException(
            status_code=503,
            detail="OpenAI quota exceeded or rate limited.",
        ) from exc
    except OpenAIError as exc:
        raise HTTPException(
            status_code=502,
            detail="OpenAI request failed.",
        ) from exc

    return {"status": "success", "response_id": response.id}