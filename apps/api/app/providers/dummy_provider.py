from __future__ import annotations

from typing import AsyncIterator

from app.providers.base import ChatProvider, EmbeddingProvider


class DummyChatProvider(ChatProvider):
    model = "dummy-llm"

    async def generate_chat(self, prompt: str, max_tokens: int) -> str:
        return prompt[:max_tokens]

    async def stream_chat(self, prompt: str, max_tokens: int) -> AsyncIterator[str]:
        yield prompt[:max_tokens]


class DummyEmbeddingProvider(EmbeddingProvider):
    model = "dummy-embedder"
    dim = 3

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []

        for text in texts:
            n = float(len(text))
            vectors.append([n % 7.0, n % 3.0, 1.0])

        return vectors