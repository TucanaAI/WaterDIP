from __future__ import annotations

from fastapi import APIRouter
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import PlainTextResponse

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics() -> PlainTextResponse:
    data = generate_latest()
    return PlainTextResponse(
        data.decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST,
    )