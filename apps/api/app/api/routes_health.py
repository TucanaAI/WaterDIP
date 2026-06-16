from __future__ import annotations

from fastapi import APIRouter, Response

router = APIRouter(tags=["health"])


@router.get("/")
async def root() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "WaterDIP GenAI Platform running. See /docs.",
    }


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "healthy"}


@router.head("/healthz")
async def healthz_head() -> Response:
    return Response(status_code=200)