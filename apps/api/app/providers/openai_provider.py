from __future__ import annotations

import json
from typing import Any, AsyncIterator

import httpx

from app.config import settings
from app.providers.base import ChatProvider, EmbeddingProvider


class OpenAIProvider(ChatProvider):
    def __init__(self) -> None:
        if not settings.llm_api_key or not settings.llm_model:
            raise RuntimeError("OpenAI provider requires LLM_API_KEY and LLM_MODEL")

        self.base_url = settings.llm_base_url or "https://api.openai.com/v1"
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model

    async def generate_chat(self, prompt: str, max_tokens: int) -> str:
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_secs) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return str(data["choices"][0]["message"]["content"])

    async def stream_chat(self, prompt: str, max_tokens: int) -> AsyncIterator[str]:
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "stream": True,
        }

        timeout = httpx.Timeout(settings.request_timeout_secs, connect=10.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue

                    data_text = line.removeprefix("data: ").strip()

                    if data_text == "[DONE]":
                        break

                    try:
                        data = json.loads(data_text)
                    except json.JSONDecodeError:
                        continue

                    delta = data["choices"][0].get("delta", {})
                    content = delta.get("content")

                    if content:
                        yield str(content)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        if not settings.llm_api_key:
            raise RuntimeError("OpenAI embeddings require LLM_API_KEY")

        self.base_url = settings.llm_base_url or "https://api.openai.com/v1"
        self.api_key = settings.llm_api_key
        self.model = settings.embedding_model
        self.dim = 1536

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        url = f"{self.base_url}/embeddings"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "model": self.model,
            "input": texts,
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_secs) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        vectors = [item["embedding"] for item in data["data"]]
        return vectors