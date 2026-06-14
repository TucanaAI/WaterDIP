from __future__ import annotations

from typing import Any, AsyncIterator
import json

import httpx

from app.config import settings


class OpenAIProvider:
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

        timeout = settings.request_timeout_secs

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.post(url, headers=headers, json=payload)
                r.raise_for_status()

                data = r.json()
                return data["choices"][0]["message"]["content"]

        except httpx.TimeoutException as e:
            raise RuntimeError("OpenAI request timed out") from e

        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"OpenAI HTTP error {e.response.status_code}: {e.response.text}"
            ) from e

        except Exception as e:
            raise RuntimeError(f"OpenAI provider error: {str(e)}") from e

    async def stream_chat(
        self,
        prompt: str,
        max_tokens: int,
    ) -> AsyncIterator[str]:
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

        timeout = httpx.Timeout(
            settings.request_timeout_secs,
            connect=10.0,
        )

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "POST",
                    url,
                    headers=headers,
                    json=payload,
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        if not line.startswith("data: "):
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
                            yield content

        except httpx.TimeoutException as e:
            raise RuntimeError("OpenAI streaming request timed out") from e

        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"OpenAI streaming HTTP error {e.response.status_code}: {e.response.text}"
            ) from e

        except Exception as e:
            raise RuntimeError(f"OpenAI streaming provider error: {str(e)}") from e