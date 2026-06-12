from __future__ import annotations
from pydantic import BaseModel


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


__all__ = [
    "ChatRequest",
    "ChatResponse",
    "EmbedRequest",
    "EmbedResponse",
]

