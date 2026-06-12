from __future__ import annotations

import time
from typing import Final

from fastapi import FastAPI, HTTPException, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import PlainTextResponse

from app.config import settings
from app.schemas import ChatRequest, ChatResponse, EmbedRequest, EmbedResponse

# Provider imports
from providers.openai_provider import OpenAIProvider

# metrics
REQUESTS_TOTAL: Final = Counter("requests_total", "Total HTTP requests", ["path", "method", "code"])
LATENCY_MS:    Final = Histogram("request_latency_ms", "Request latency in ms", ["path", "method"],
                                 buckets=(5,10,25,50,100,250,500,1000))

app = FastAPI(title="GenAI Microservice", version="1.0.0")

# #connect to different (crossing) origin location backend (https://api.harrisonobidinnu.com)
# from fastapi.middleware.cors import CORSMiddleware

# ALLOWED_ORIGINS = [
#     "https://harrisonobidinnu.com",
#     "https://www.harrisonobidinnu.com",
#     # add "http://localhost:5173" only if you dev from Vite locally
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=ALLOWED_ORIGINS,
#     allow_credentials=False,      # keep False unless you use cookies
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

print("provider setttings is \n")
print(settings.llm_provider)

# Initialize provider once
if settings.llm_provider == "openai":
    _provider = OpenAIProvider()
    _provider_model = _provider.model or "openai"
else:
    _provider = None
    _provider_model = settings.model_name  # "dummy-llm"

def _validate_chat(req: ChatRequest) -> None:
    if len(req.prompt) > settings.prompt_max_chars:
        raise HTTPException(status_code=400, detail="prompt too long")
    if req.max_tokens > settings.max_tokens_limit or req.max_tokens <= 0:
        raise HTTPException(status_code=400, detail="invalid max_tokens")

def _dummy_embed(texts: list[str]) -> list[list[float]]:
    out: list[list[float]] = []
    for t in texts:
        n = float(len(t))
        out.append([n % 7.0, n % 3.0, 1.0])
    return out

@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "message": "GenAI microservice running. See /docs."}

@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "healthy"}

@app.head("/healthz")
async def healthz_head() -> Response:
    return Response(status_code=200)

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    t0 = time.perf_counter()
    code = "200"
    try:
        _validate_chat(req)
        if settings.llm_provider == "openai":
            assert _provider is not None
            text = await _provider.generate_chat(req.prompt, req.max_tokens)
            model_name = _provider_model
        else:
            # dummy echo
            text = req.prompt[: req.max_tokens]
            model_name = settings.model_name

        return ChatResponse(
            text=text,
            input_tokens=len(req.prompt.split()),
            output_tokens=req.max_tokens,
            model=model_name,
        )
    except HTTPException as e:
        code = str(e.status_code)
        raise
    finally:
        LATENCY_MS.labels("/chat", "POST").observe((time.perf_counter() - t0) * 1000.0)
        REQUESTS_TOTAL.labels("/chat", "POST", code).inc()

@app.post("/embed", response_model=EmbedResponse)
async def embed(req: EmbedRequest) -> EmbedResponse:
    t0 = time.perf_counter()
    code = "200"
    try:
        if not req.texts:
            raise HTTPException(status_code=400, detail="texts must not be empty")
        vectors = _dummy_embed(req.texts)
        return EmbedResponse(vectors=vectors, dim=3, model="dummy-embedder")
    except HTTPException as e:
        code = str(e.status_code)
        raise
    finally:
        LATENCY_MS.labels("/embed", "POST").observe((time.perf_counter() - t0) * 1000.0)
        REQUESTS_TOTAL.labels("/embed", "POST", code).inc()

@app.get("/metrics")
async def metrics() -> PlainTextResponse:
    data = generate_latest()  # type: ignore[arg-type]
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

