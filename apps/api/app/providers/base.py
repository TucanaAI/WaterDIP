from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator


class ChatProvider(ABC):
    model: str

    @abstractmethod
    async def generate_chat(self, prompt: str, max_tokens: int) -> str:
        raise NotImplementedError

    @abstractmethod
    async def stream_chat(self, prompt: str, max_tokens: int) -> AsyncIterator[str]:
        raise NotImplementedError


class EmbeddingProvider(ABC):
    model: str
    dim: int

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError