from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_chat import router as chat_router
from app.api.routes_embed import router as embed_router
from app.api.routes_health import router as health_router
from app.api.routes_metrics import router as metrics_router
from app.api.routes_waterdip import router as waterdip_router
from app.config import settings
from app.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="WaterDIP GenAI Platform",
        version="2.0.0",
        description="LLM + Reservoir Decision Intelligence API",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(metrics_router)
    app.include_router(chat_router)
    app.include_router(embed_router)
    app.include_router(waterdip_router)

    return app


app = create_app()