from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException

from app.observability.metrics import (
    REQUEST_LATENCY_MS,
    REQUESTS_TOTAL,
    WATERDIP_DIAGNOSES_TOTAL,
)
from app.reservoir.breakthrough import classify_water_breakthrough
from app.reservoir.recommendations import recommend_for_water_breakthrough
from app.schemas import WaterDIPDiagnoseRequest, WaterDIPDiagnoseResponse

router = APIRouter(prefix="/waterdip", tags=["waterdip"])


@router.post("/diagnose", response_model=WaterDIPDiagnoseResponse)
async def diagnose_water_breakthrough(
    req: WaterDIPDiagnoseRequest,
) -> WaterDIPDiagnoseResponse:
    t0 = time.perf_counter()
    code = "200"

    try:
        if not req.production:
            raise HTTPException(status_code=400, detail="production data is required")

        severity, latest, change = classify_water_breakthrough(req.production)
        recommendation = recommend_for_water_breakthrough(severity)

        WATERDIP_DIAGNOSES_TOTAL.labels(severity).inc()

        return WaterDIPDiagnoseResponse(
            well_id=req.well_id,
            finding=f"Water breakthrough severity classified as {severity}.",
            water_cut_latest=latest,
            water_cut_change=change,
            severity=severity,
            recommendation=recommendation,
        )

    except HTTPException as exc:
        code = str(exc.status_code)
        raise

    finally:
        REQUEST_LATENCY_MS.labels("/waterdip/diagnose", "POST").observe(
            (time.perf_counter() - t0) * 1000.0
        )
        REQUESTS_TOTAL.labels("/waterdip/diagnose", "POST", code).inc()