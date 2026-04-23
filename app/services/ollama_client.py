import httpx
from app.core.settings import get_settings
from app.services.openai_client import get_openai_client


class OllamaClient:
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip("/")

    async def ping(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/api/tags",
                timeout=5,
            )
            response.raise_for_status()
            payload = response.json()
            return {
                "status": "ok",
                "detail": "Connected to Ollama",
                "models": len(payload.get("models", [])),
            }

    async def create_response(self, model: str, prompt: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()

def get_llm_client():
    settings = get_settings()
    if settings.LLM_PROVIDER.lower() == "ollama":
        return OllamaClient(settings.OLLAMA_API_URL)
    if settings.LLM_PROVIDER.lower() == "openai":
        return get_openai_client()
    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
