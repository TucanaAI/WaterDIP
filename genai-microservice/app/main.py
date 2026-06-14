from __future__ import annotations

import time
from typing import Final

from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import StreamingResponse

#allows Flask origin:   http://127.0.0.1:5000 & FastAPI API origin:  http://127.0.0.1:8080 share resource
from fastapi.middleware.cors import CORSMiddleware 

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5000", #Fast API backend (:8080), allows dev machine Flask frontend (:5000) to make requests
        "http://localhost:5000", #Fast API backend (:8080), allows server machine Flask frontend (:5000) to make requests
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("provider setttings is \n")
print(settings.llm_provider)

# Initialize provider once
if settings.llm_provider != "dummy": #e.g.: it is "openai", "waterdip"

    if settings.llm_provider == "waterdip":
        pass #will train the waterdip model. waterdipAIProvider Class should implement stream_chat().
    else:
        _provider = OpenAIProvider() #OpenAIProvider Class Implements stream_chat().

    _provider_model = _provider.model or "openai"
else: #it is dummy. No provider model is available
    _provider = None #dummy
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
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    t0 = time.perf_counter()
    code = "200"

    # Measure click -> server receive latency
    client_submit_started_at_ms = request.headers.get(
        "x-client-submit-started-at-ms"
    )

    if client_submit_started_at_ms:
        try:
            server_received_at_ms = int(time.time() * 1000)

            submit_to_server_ms = (
                server_received_at_ms
                - int(client_submit_started_at_ms)
            )

            print(
                f"Submit -> Server Receive Latency: "
                f"{submit_to_server_ms} ms"
            )
        except ValueError:
            pass

    try:
        _validate_chat(req)

        if settings.llm_provider == "openai":
            assert _provider is not None

            provider_t0 = time.perf_counter()

            text = await _provider.generate_chat(
                req.prompt,
                req.max_tokens
            )

            provider_latency_ms = (
                time.perf_counter() - provider_t0
            ) * 1000.0

            print(
                f"OpenAI Provider Latency: " #consider using "Provider Latency" (to accomodate waterdip model)
                f"{provider_latency_ms:.2f} ms"
            )

            model_name = _provider_model
            
            #  Consider elif: for waterdip custom model or consider if-block changed to settings.llm_provider != "dummy"
        else:
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
        total_latency_ms = (
            time.perf_counter() - t0
        ) * 1000.0

        print(
            f"Total Server Latency: "
            f"{total_latency_ms:.2f} ms"
        )

        LATENCY_MS.labels(
            "/chat",
            "POST"
        ).observe(total_latency_ms)

        REQUESTS_TOTAL.labels(
            "/chat",
            "POST",
            code
        ).inc()


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    _validate_chat(req)

    async def generate():
        if settings.llm_provider == "openai":
            assert _provider is not None

            async for chunk in _provider.stream_chat(
                req.prompt,
                req.max_tokens,
            ):
                yield chunk

        #  Consider elif: for waterdip custom model or consider if-block changed to settings.llm_provider != "dummy"
        else:
            yield req.prompt[: req.max_tokens]

    return StreamingResponse(
        generate(),
        media_type="text/plain",
    )

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

