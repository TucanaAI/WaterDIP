from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str
    max_tokens: int = 128


class ChatResponse(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int
    model: str


class EmbedRequest(BaseModel):
    texts: list[str]


class EmbedResponse(BaseModel):
    vectors: list[list[float]]
    dim: int
    model: str


class ProductionPoint(BaseModel):
    date: str
    oil_rate: float = Field(ge=0)
    water_rate: float = Field(ge=0)
    gas_rate: float = Field(default=0, ge=0)


class WaterDIPDiagnoseRequest(BaseModel):
    well_id: str
    production: list[ProductionPoint]


class WaterDIPDiagnoseResponse(BaseModel):
    well_id: str
    finding: str
    water_cut_latest: float
    water_cut_change: float
    severity: str
    recommendation: str