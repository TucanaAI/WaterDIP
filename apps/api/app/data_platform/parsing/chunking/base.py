"""
Core abstractions for WaterDIP engineering-aware chunking.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..models import (
    DocumentChunk,
    WaterDIPDocument,
)


@dataclass(slots=True)
class ChunkingContext:
    """
    Runtime configuration passed to chunkers.

    max_tokens:
        Preferred maximum size of a chunk.

    overlap_tokens:
        Approximate overlap used when textual content must be split.

    min_tokens:
        Small trailing chunks below this size may be merged where safe.
    """

    max_tokens: int = 800
    overlap_tokens: int = 100
    min_tokens: int = 50

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if self.max_tokens <= 0:
            raise ValueError(
                "max_tokens must be greater than zero."
            )

        if self.overlap_tokens < 0:
            raise ValueError(
                "overlap_tokens cannot be negative."
            )

        if self.overlap_tokens >= self.max_tokens:
            raise ValueError(
                "overlap_tokens must be smaller than max_tokens."
            )

        if self.min_tokens < 0:
            raise ValueError(
                "min_tokens cannot be negative."
            )


class BaseChunker(ABC):
    """
    Base contract for all WaterDIP chunking strategies.
    """

    name: str = "base"
    priority: int = 100

    @abstractmethod
    def supports(
        self,
        document: WaterDIPDocument,
    ) -> bool:
        """Return whether this chunker supports the document."""

    @abstractmethod
    def chunk(
        self,
        document: WaterDIPDocument,
        context: ChunkingContext,
    ) -> list[DocumentChunk]:
        """Convert a document into retrieval chunks."""