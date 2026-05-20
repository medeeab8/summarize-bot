from langchain_ollama import ChatOllama

from app.core.settings import get_settings
from app.services.openai_client import get_openai_client


class OllamaClient:
    def __init__(self, api_url: str, model: str, temperature: float):
        # Normalize the base URL once so all later calls share the same endpoint.
        self.api_url = api_url.rstrip("/")
        self.model = model
        self._client = ChatOllama(
            base_url=self.api_url,
            model=model,
            temperature=temperature,
        )

    @staticmethod
    def _response_to_text(response) -> str:
        # LangChain responses can arrive as plain strings or structured content;
        # flatten them into one text payload for the API layer.
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
        # Use a lightweight chat round-trip to confirm the model is reachable.
        response = await self._client.ainvoke("ping")
        return {
            "status": "ok",
            "detail": "Connected to Ollama via LangChain",
            "model": self.model,
            "response": self._response_to_text(response),
        }

    async def create_response(self, prompt: str, model: str | None = None):
        # Rebind only when a request overrides the default model.
        llm = self._client if model is None or model == self.model else self._client.bind(model=model)
        response = await llm.ainvoke(prompt)
        return {
            "content": self._response_to_text(response),
            "model": model or self.model,
        }

    @staticmethod
    def _normalize_bind_kwargs(kwargs: dict) -> dict:
        # Older/newer ollama client versions differ on whether generation
        # controls like num_predict are accepted at the top level or only under
        # the options payload. Normalize them here so callers can stay stable.
        normalized = dict(kwargs)
        option_keys = {
            "num_predict",
            "num_ctx",
            "num_gpu",
            "num_thread",
            "repeat_last_n",
            "repeat_penalty",
            "seed",
            "stop",
            "temperature",
            "top_k",
            "top_p",
            "tfs_z",
            "mirostat",
            "mirostat_eta",
            "mirostat_tau",
        }

        option_values = {
            key: normalized.pop(key)
            for key in list(normalized)
            if key in option_keys
        }
        if option_values:
            existing_options = normalized.get("options")
            merged_options = dict(existing_options) if isinstance(existing_options, dict) else {}
            merged_options.update(option_values)
            normalized["options"] = merged_options

        return normalized

    def get_chat_model(self, model: str | None = None, **kwargs):
        # Expose the LangChain chat model so higher-level services can compose
        # prompts and parsers around it.
        llm = self._client if model is None or model == self.model else self._client.bind(model=model)
        bind_kwargs = self._normalize_bind_kwargs(kwargs)
        return llm.bind(**bind_kwargs) if bind_kwargs else llm


def get_llm_client():
    settings = get_settings()
    # Choose the active LLM backend from configuration so callers do not need to
    # care which provider is currently enabled.
    if settings.LLM_PROVIDER.lower() == "ollama":
        return OllamaClient(
            settings.OLLAMA_API_URL,
            settings.OLLAMA_MODEL,
            settings.LLM_TEMPERATURE,
        )
    if settings.LLM_PROVIDER.lower() == "openai":
        return get_openai_client()
    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
