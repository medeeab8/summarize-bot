from langchain_openai import ChatOpenAI

from app.core.settings import get_settings


class OpenAIClient:
    def __init__(self, api_key: str, model: str, temperature: float):
        self.model = model
        self._client = ChatOpenAI(
            api_key=api_key,
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
            "detail": "Connected to OpenAI via LangChain",
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


def get_openai_client() -> OpenAIClient:
    settings = get_settings()
    return OpenAIClient(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
        temperature=settings.LLM_TEMPERATURE,
    )
