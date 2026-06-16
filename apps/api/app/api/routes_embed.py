from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException

from app.observability.metrics import PROVIDER_LATENCY_MS, REQUEST_LATENCY_MS, REQUESTS_TOTAL
from app.providers.factory import get_embedding_provider
from app.schemas import EmbedRequest, EmbedResponse

router = APIRouter(tags=["embeddings"])

_provider = get_embedding_provider()


@router.post("/embed", response_model=EmbedResponse)
async def embed(req: EmbedRequest) -> EmbedResponse:
    t0 = time.perf_counter()
    code = "200"

    try:
        if not req.texts:
            raise HTTPException(status_code=400, detail="texts must not be empty")

        provider_t0 = time.perf_counter()
        vectors = await _provider.embed_texts(req.texts)
        PROVIDER_LATENCY_MS.labels(_provider.model, "embed").observe(
            (time.perf_counter() - provider_t0) * 1000.0
        )

        return EmbedResponse(
            vectors=vectors,
            dim=_provider.dim,
            model=_provider.model,
        )

    except HTTPException as exc:
        code = str(exc.status_code)
        raise

    finally:
        REQUEST_LATENCY_MS.labels("/embed", "POST").observe(
            (time.perf_counter() - t0) * 1000.0
        )
        REQUESTS_TOTAL.labels("/embed", "POST", code).inc()