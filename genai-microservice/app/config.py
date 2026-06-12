from __future__ import annotations

from typing import Literal,Final
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_name: str = Field(default="dummy-llm", validation_alias="MODEL_NAME")
    request_timeout_secs: float = Field(default=10.0, validation_alias="REQUEST_TIMEOUT_SECS")
    max_tokens_default: int = Field(default=128, validation_alias="MAX_TOKENS_DEFAULT")
    max_tokens_limit: int = Field(default=2048, validation_alias="MAX_TOKENS_LIMIT")
    prompt_max_chars: int = Field(default=4000, validation_alias="PROMPT_MAX_CHARS")

    llm_provider: Literal["dummy", "openai"] = "dummy"
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # just in case new vars is inserted later


settings: Final[Settings] = Settings()

