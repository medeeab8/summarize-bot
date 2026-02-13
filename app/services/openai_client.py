from openai import AsyncOpenAI

from app.core.settings import get_settings

_settings = get_settings()
_client = AsyncOpenAI(api_key=_settings.OPENAI_API_KEY)


def get_openai_client() -> AsyncOpenAI:
    return _client
