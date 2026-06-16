from __future__ import annotations

from app.config import settings
from app.providers.base import ChatProvider, EmbeddingProvider
from app.providers.dummy_provider import DummyChatProvider, DummyEmbeddingProvider
from app.providers.openai_provider import OpenAIEmbeddingProvider, OpenAIProvider
from app.providers.waterdip_provider import WaterDIPProvider


def get_chat_provider() -> ChatProvider:
    if settings.llm_provider == "openai":
        return OpenAIProvider()

    if settings.llm_provider == "waterdip":
        return WaterDIPProvider()

    return DummyChatProvider()


def get_embedding_provider() -> EmbeddingProvider:
    if settings.embedding_provider == "openai":
        return OpenAIEmbeddingProvider()

    return DummyEmbeddingProvider()