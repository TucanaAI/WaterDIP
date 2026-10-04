"""
Chunker registry for WaterDIP.
"""

from __future__ import annotations

from .base import BaseChunker
from .section import SectionChunker
from .table import TableChunker
from .text import TextChunker
from .well_log import WellLogChunker
from ..models import WaterDIPDocument


class ChunkerRegistry:
    """Registry and selector for engineering chunkers."""

    def __init__(self) -> None:
        self._chunkers: dict[
            str,
            BaseChunker,
        ] = {}

    def register(
        self,
        chunker: BaseChunker,
        *,
        replace: bool = False,
    ) -> None:
        name = chunker.name.strip().lower()

        if not name:
            raise ValueError(
                "Chunker name cannot be empty."
            )

        if (
            name in self._chunkers
            and not replace
        ):
            raise ValueError(
                f"Chunker '{name}' is already registered."
            )

        self._chunkers[name] = chunker

    def get(
        self,
        name: str,
    ) -> BaseChunker:
        key = name.strip().lower()

        try:
            return self._chunkers[key]
        except KeyError as exc:
            raise KeyError(
                f"Unknown chunker '{name}'."
            ) from exc

    def all(
        self,
    ) -> list[BaseChunker]:
        return sorted(
            self._chunkers.values(),
            key=lambda item: item.priority,
        )

    def applicable(
        self,
        document: WaterDIPDocument,
    ) -> list[BaseChunker]:
        return [
            chunker
            for chunker in self.all()
            if chunker.supports(document)
        ]

    def select(
        self,
        document: WaterDIPDocument,
    ) -> BaseChunker:
        candidates = self.applicable(
            document
        )

        if not candidates:
            raise ValueError(
                (
                    "No chunker supports document "
                    f"'{document.id}'."
                )
            )

        return candidates[0]

    def names(
        self,
    ) -> list[str]:
        return [
            chunker.name
            for chunker in self.all()
        ]


def create_default_chunker_registry(
) -> ChunkerRegistry:
    registry = ChunkerRegistry()

    registry.register(
        WellLogChunker()
    )

    registry.register(
        TableChunker()
    )

    registry.register(
        SectionChunker()
    )

    registry.register(
        TextChunker()
    )

    return registry