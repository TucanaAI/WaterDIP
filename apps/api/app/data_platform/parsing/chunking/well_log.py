"""
Well-log-aware chunking for WaterDIP.
"""

from __future__ import annotations

from typing import Any

from ..models import (
    ChunkPosition,
    ChunkType,
    DocumentChunk,
    DocumentType,
    WaterDIPDocument,
)
from .base import BaseChunker, ChunkingContext
from .tokenizer import count_tokens


def _curve_text(
    curve: dict[str, Any],
) -> str:
    """Render one canonical well-log curve description."""

    mnemonic = curve.get(
        "mnemonic",
        "UNKNOWN",
    )

    family = curve.get(
        "family",
        "unknown",
    )

    unit = curve.get("unit")
    description = curve.get(
        "description"
    )

    statistics = curve.get(
        "statistics"
    ) or {}

    parts = [
        f"Curve: {mnemonic}",
        f"Family: {family}",
    ]

    if unit:
        parts.append(
            f"Unit: {unit}"
        )

    if description:
        parts.append(
            f"Description: {description}"
        )

    if statistics:
        parts.extend(
            [
                (
                    "Valid samples: "
                    f"{statistics.get('count', 0)}"
                ),
                (
                    "Null samples: "
                    f"{statistics.get('null_count', 0)}"
                ),
            ]
        )

        for label, key in (
            ("Minimum", "minimum"),
            ("Maximum", "maximum"),
            ("Mean", "mean"),
            ("P10", "p10"),
            ("P50", "p50"),
            ("P90", "p90"),
        ):
            value = statistics.get(key)

            if value is not None:
                parts.append(
                    f"{label}: {value}"
                )

    return "\n".join(parts)


class WellLogChunker(BaseChunker):
    """
    Produce engineering retrieval chunks from canonical well-log metadata.
    """

    name = "well_log"
    priority = 10

    def supports(
        self,
        document: WaterDIPDocument,
    ) -> bool:
        return (
            document.document_type
            == DocumentType.WELL_LOG
            and isinstance(
                document.metadata.get(
                    "well_log"
                ),
                dict,
            )
        )

    def chunk(
        self,
        document: WaterDIPDocument,
        context: ChunkingContext,
    ) -> list[DocumentChunk]:
        well_log = document.metadata[
            "well_log"
        ]

        chunks: list[DocumentChunk] = []

        well_name = None

        if document.engineering.well:
            well_name = (
                document.engineering.well.well_name
            )

        depth = well_log.get(
            "depth",
            {},
        )

        summary_lines = [
            "Well Log Summary",
        ]

        if well_name:
            summary_lines.append(
                f"Well: {well_name}"
            )

        version = well_log.get(
            "las_version"
        )

        if version:
            summary_lines.append(
                f"LAS version: {version}"
            )

        start = depth.get("start")
        stop = depth.get("stop")
        unit = depth.get("unit")
        step = depth.get("step")

        if (
            start is not None
            and stop is not None
        ):
            interval = (
                f"Depth interval: "
                f"{start} to {stop}"
            )

            if unit:
                interval += f" {unit}"

            summary_lines.append(
                interval
            )

        if step is not None:
            step_text = f"Depth step: {step}"

            if unit:
                step_text += f" {unit}"

            summary_lines.append(
                step_text
            )

        curves = well_log.get(
            "curves",
            [],
        )

        summary_lines.append(
            f"Curve count: {len(curves)}"
        )

        summary_text = "\n".join(
            summary_lines
        )

        chunks.append(
            self._create_chunk(
                document=document,
                index=0,
                text=summary_text,
                metadata={
                    "well_log_chunk": "summary",
                    "depth_start": start,
                    "depth_stop": stop,
                    "depth_unit": unit,
                },
            )
        )

        chunk_index = 1

        for curve_index, curve in enumerate(
            curves
        ):
            text = _curve_text(
                curve
            )

            chunks.append(
                self._create_chunk(
                    document=document,
                    index=chunk_index,
                    text=text,
                    metadata={
                        "well_log_chunk": "curve",
                        "curve_index": curve_index,
                        "curve_mnemonic": curve.get(
                            "mnemonic"
                        ),
                        "curve_family": curve.get(
                            "family"
                        ),
                        "curve_unit": curve.get(
                            "unit"
                        ),
                        "depth_start": start,
                        "depth_stop": stop,
                        "depth_unit": unit,
                    },
                )
            )

            chunk_index += 1

        return chunks

    def _create_chunk(
        self,
        *,
        document: WaterDIPDocument,
        index: int,
        text: str,
        metadata: dict[str, Any],
    ) -> DocumentChunk:
        chunk = DocumentChunk.create(
            document_id=document.id,
            dataset_id=document.source.dataset_id,
            index=index,
            text=text,
            chunk_type=ChunkType.WELL_LOG,
            position=ChunkPosition(
                index=index,
            ),
            engineering=document.engineering,
            metadata={
                "chunker": self.name,
                "source_filename": (
                    document.source.filename
                ),
                **metadata,
            },
        )

        chunk.token_count = count_tokens(
            text
        )

        return chunk