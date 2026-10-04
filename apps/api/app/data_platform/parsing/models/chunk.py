"""
Canonical retrieval chunk models for WaterDIP.

Actual chunking algorithms are implemented in a later framework phase.
"""

from __future__ import annotations

from typing import Any
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field

from .common import ChunkType, WaterDIPModel
from .engineering import EngineeringMetadata


def generate_chunk_id(
    *,
    document_id: str,
    index: int,
    text: str,
) -> str:
    """
    Generate a deterministic chunk identifier.

    The same document, chunk position, and content will produce the same ID.
    """

    identity = f"{document_id}|{index}|{text}"

    return f"wd-chunk-{uuid5(NAMESPACE_URL, identity)}"


class ChunkPosition(WaterDIPModel):
    """Location of a chunk within its source document."""

    index: int = Field(
        ge=0,
    )

    page_start: int | None = Field(
        default=None,
        ge=1,
    )

    page_end: int | None = Field(
        default=None,
        ge=1,
    )

    character_start: int | None = Field(
        default=None,
        ge=0,
    )

    character_end: int | None = Field(
        default=None,
        ge=0,
    )

    section_id: str | None = None
    section_title: str | None = None


class DocumentChunk(WaterDIPModel):
    """
    Canonical unit submitted to embedding and retrieval systems.
    """

    id: str

    document_id: str

    dataset_id: str | None = None

    chunk_type: ChunkType = ChunkType.TEXT

    text: str

    position: ChunkPosition

    engineering: EngineeringMetadata = Field(
        default_factory=EngineeringMetadata,
    )

    token_count: int | None = Field(
        default=None,
        ge=0,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @classmethod
    def create(
        cls,
        *,
        document_id: str,
        index: int,
        text: str,
        dataset_id: str | None = None,
        chunk_type: ChunkType = ChunkType.TEXT,
        position: ChunkPosition | None = None,
        engineering: EngineeringMetadata | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "DocumentChunk":
        """Create a deterministic canonical document chunk."""

        actual_position = position or ChunkPosition(
            index=index
        )

        if actual_position.index != index:
            raise ValueError(
                "Chunk position index must match the supplied chunk index."
            )

        chunk_id = generate_chunk_id(
            document_id=document_id,
            index=index,
            text=text,
        )

        return cls(
            id=chunk_id,
            document_id=document_id,
            dataset_id=dataset_id,
            chunk_type=chunk_type,
            text=text,
            position=actual_position,
            engineering=engineering or EngineeringMetadata(),
            metadata=metadata or {},
        )