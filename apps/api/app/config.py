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

    # Application
    app_env: str = Field(
        default="local",
        validation_alias="APP_ENV",
    )

    # API limits and timeouts
    request_timeout_secs: float = Field(
        default=30.0,
        validation_alias="REQUEST_TIMEOUT_SECS",
    )

    max_tokens_default: int = Field(
        default=128,
        validation_alias="MAX_TOKENS_DEFAULT",
    )

    max_tokens_limit: int = Field(
        default=2048,
        validation_alias="MAX_TOKENS_LIMIT",
    )

    prompt_max_chars: int = Field(
        default=4000,
        validation_alias="PROMPT_MAX_CHARS",
    )

    # LLM provider configuration
    llm_provider: Literal["dummy", "openai", "waterdip"] = Field(
        default="dummy",
        validation_alias="LLM_PROVIDER",
    )

    llm_base_url: str | None = Field(
        default=None,
        validation_alias="LLM_BASE_URL",
    )

    llm_api_key: str | None = Field(
        default=None,
        validation_alias="LLM_API_KEY",
    )

    llm_model: str | None = Field(
        default=None,
        validation_alias="LLM_MODEL",
    )

    # Embedding provider configuration
    embedding_provider: Literal["dummy", "openai"] = Field(
        default="dummy",
        validation_alias="EMBEDDING_PROVIDER",
    )

    embedding_model: str = Field(
        default="dummy-embedder",
        validation_alias="EMBEDDING_MODEL",
    )

    # Databricks configuration
    databricks_host: str | None = Field(
        default=None,
        validation_alias="DATABRICKS_HOST",
    )

    databricks_profile: str = Field(
        default="waterdip",
        validation_alias="DATABRICKS_PROFILE",
    )

    databricks_volve_transfer_job_id: int | None = Field(
        default=None,
        validation_alias="DATABRICKS_VOLVE_TRANSFER_JOB_ID",
    )

    # AWS / S3 configuration
    s3_bucket_name: str = Field(
        default="waterdip-data-lake",
        validation_alias="S3_BUCKET_NAME",
    )

    aws_region: str | None = Field(
        default=None,
        validation_alias="AWS_REGION",
    )

    # Frontend origins allowed to call the FastAPI application
    cors_origins: list[str] = [
        "http://127.0.0.1:5000",
        "http://localhost:5000",
    ]


settings: Final[Settings] = Settings()