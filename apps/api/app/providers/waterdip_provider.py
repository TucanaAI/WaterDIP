from __future__ import annotations

from typing import AsyncIterator

from app.providers.base import ChatProvider


class WaterDIPProvider(ChatProvider):
    model = "waterdip-custom-model-stub"

    async def generate_chat(self, prompt: str, max_tokens: int) -> str:
        return (
            "WaterDIP custom model is not trained yet. "
            "Current provider stub received: "
            f"{prompt[:max_tokens]}"
        )

    async def stream_chat(self, prompt: str, max_tokens: int) -> AsyncIterator[str]:
        text = await self.generate_chat(prompt, max_tokens)
        yield text