from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.config import settings
from app.observability.metrics import (
    PROVIDER_LATENCY_MS,
    REQUEST_LATENCY_MS,
    REQUESTS_TOTAL,
    TOKENS_TOTAL,
)
from app.providers.factory import get_chat_provider
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])

_provider = get_chat_provider()


def _validate_chat(req: ChatRequest) -> None:
    if len(req.prompt) > settings.prompt_max_chars:
        raise HTTPException(status_code=400, detail="prompt too long")

    if req.max_tokens > settings.max_tokens_limit or req.max_tokens <= 0:
        raise HTTPException(status_code=400, detail="invalid max_tokens")


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    t0 = time.perf_counter()
    code = "200"

    try:
        _validate_chat(req)

        client_submit_started_at_ms = request.headers.get(
            "x-client-submit-started-at-ms"
        )

        if client_submit_started_at_ms:
            try:
                submit_to_server_ms = int(time.time() * 1000) - int(
                    client_submit_started_at_ms
                )
                print(f"Submit -> Server Receive Latency: {submit_to_server_ms} ms")
            except ValueError:
                pass

        provider_t0 = time.perf_counter()
        text = await _provider.generate_chat(req.prompt, req.max_tokens)
        provider_latency_ms = (time.perf_counter() - provider_t0) * 1000.0

        PROVIDER_LATENCY_MS.labels(
            settings.llm_provider,
            "chat",
        ).observe(provider_latency_ms)

        input_tokens = max(1, len(req.prompt.split()))
        output_tokens = min(req.max_tokens, max(1, len(text.split())))

        TOKENS_TOTAL.labels("input", settings.llm_provider, _provider.model).inc(
            input_tokens
        )
        TOKENS_TOTAL.labels("output", settings.llm_provider, _provider.model).inc(
            output_tokens
        )

        return ChatResponse(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=_provider.model,
        )

    except HTTPException as exc:
        code = str(exc.status_code)
        raise

    finally:
        REQUEST_LATENCY_MS.labels("/chat", "POST").observe(
            (time.perf_counter() - t0) * 1000.0
        )
        REQUESTS_TOTAL.labels("/chat", "POST", code).inc()


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    _validate_chat(req)

    async def generate() -> object:
        async for chunk in _provider.stream_chat(req.prompt, req.max_tokens):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")