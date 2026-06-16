from __future__ import annotations

from typing import Final, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="local", validation_alias="APP_ENV")

    request_timeout_secs: float = Field(default=30.0, validation_alias="REQUEST_TIMEOUT_SECS")
    max_tokens_default: int = Field(default=128, validation_alias="MAX_TOKENS_DEFAULT")
    max_tokens_limit: int = Field(default=2048, validation_alias="MAX_TOKENS_LIMIT")
    prompt_max_chars: int = Field(default=4000, validation_alias="PROMPT_MAX_CHARS")

    llm_provider: Literal["dummy", "openai", "waterdip"] = Field(
        default="dummy",
        validation_alias="LLM_PROVIDER",
    )

    llm_base_url: str | None = Field(default=None, validation_alias="LLM_BASE_URL")
    llm_api_key: str | None = Field(default=None, validation_alias="LLM_API_KEY")
    llm_model: str | None = Field(default=None, validation_alias="LLM_MODEL")

    embedding_provider: Literal["dummy", "openai"] = Field(
        default="dummy",
        validation_alias="EMBEDDING_PROVIDER",
    )
    embedding_model: str = Field(
        default="dummy-embedder",
        validation_alias="EMBEDDING_MODEL",
    )

    cors_origins: list[str] = [
        "http://127.0.0.1:5000",
        "http://localhost:5000",
    ]


settings: Final[Settings] = Settings()