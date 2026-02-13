import httpx
from app.core.settings import get_settings
from app.services.openai_client import get_openai_client

class OllamaClient:
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip("/")

    async def create_response(self, model: str, prompt: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/api/generate",
                json={"model": model, "prompt": prompt},
                timeout=10,
            )
            response.raise_for_status()
            # If we get here, we are connected to Ollama and the request succeeded
            return {"status": "ok", "detail": "Connected to Ollama"}
            return results[-1] if results else {}

def get_llm_client():
    settings = get_settings()
    print(settings)
    if settings.LLM_PROVIDER.lower() == "ollama":
        return OllamaClient(settings.OLLAMA_API_URL)
    if settings.LLM_PROVIDER.lower() == "openai":
        return get_openai_client()
