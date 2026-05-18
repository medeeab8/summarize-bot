from __future__ import annotations

from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_PATH = Path(__file__).resolve().parents[1] / ".env"

class Environment(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
        )

    # App metadata / routing
    APP_NAME: str = "Summarize Bot API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    # Environment / runtime behaviour
    ENVIRONMENT: Environment = Environment.LOCAL
    DEBUG: bool = True

    # Server configuration
    HOST: str = "localhost"
    PORT: int = 8000
    WORKERS: int = 1

    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/app.log"

    #Security settings
    SECRET_KEY: str = Field(default="your-secret-key", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Agent settings
    AGENT_NAME: str = "Summarize Bot"
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    # LLM provider settings
    LLM_PROVIDER: str = Field(default="openai", env="LLM_PROVIDER")  # 'openai' or 'ollama'
    OLLAMA_API_URL: str = Field(default="http://ollama:11434", env="OLLAMA_API_URL")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    OLLAMA_MODEL: str = Field(default="llama2", env="OLLAMA_MODEL")
    LLM_TEMPERATURE: float = Field(default=0.2, env="LLM_TEMPERATURE")
    SUMMARY_MAX_TOKENS: int = Field(default=400, env="SUMMARY_MAX_TOKENS")
    SUMMARY_MAX_LENGTH: int = Field(default=5000, env="SUMMARY_MAX_LENGTH")

    # File upload settings
    UPLOAD_DIR: str = "storage/uploads"
    EXTRACTED_TEXT_DIR: str = "storage/extracted_text"
    MAX_UPLOAD_SIZE_MS: int = 20
    ALLOWED_DOCUMENT_EXTENSTIONS: set[str] = {"pdf", "txt", "md"}

@lru_cache
def get_settings() -> Settings:
    return Settings()