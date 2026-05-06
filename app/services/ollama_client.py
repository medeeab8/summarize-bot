from langchain_ollama import ChatOllama

from app.core.settings import get_settings
from app.services.openai_client import get_openai_client


class OllamaClient:
    def __init__(self, api_url: str, model: str, temperature: float):
        self.api_url = api_url.rstrip("/")
        self.model = model
        self._client = ChatOllama(
            base_url=self.api_url,
            model=model,
            temperature=temperature,
        )

    @staticmethod
    def _response_to_text(response) -> str:
        content = response.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    parts.append(item.get("text", ""))
                else:
                    parts.append(str(item))
            return "".join(parts).strip()
        return str(content)

    async def ping(self):
        response = await self._client.ainvoke("ping")
        return {
            "status": "ok",
            "detail": "Connected to Ollama via LangChain",
            "model": self.model,
            "response": self._response_to_text(response),
        }

    async def create_response(self, prompt: str, model: str | None = None):
        llm = self._client if model is None or model == self.model else self._client.bind(model=model)
        response = await llm.ainvoke(prompt)
        return {
            "content": self._response_to_text(response),
            "model": model or self.model,
        }

    def get_chat_model(self, model: str | None = None, **kwargs):
        llm = self._client if model is None or model == self.model else self._client.bind(model=model)
        return llm.bind(**kwargs) if kwargs else llm


def get_llm_client():
    settings = get_settings()
    if settings.LLM_PROVIDER.lower() == "ollama":
        return OllamaClient(
            settings.OLLAMA_API_URL,
            settings.OLLAMA_MODEL,
            settings.LLM_TEMPERATURE,
        )
    if settings.LLM_PROVIDER.lower() == "openai":
        return get_openai_client()
    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
