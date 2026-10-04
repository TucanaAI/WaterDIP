"""
Table-aware chunking for WaterDIP engineering datasets.
"""

from __future__ import annotations

from typing import Any

from ..models import (
    ChunkPosition,
    ChunkType,
    DocumentChunk,
    DocumentTable,
    WaterDIPDocument,
)
from .base import BaseChunker, ChunkingContext
from .tokenizer import count_tokens


def row_to_text(
    row: list[Any],
) -> str:
    return " | ".join(
        "" if value is None else str(value)
        for value in row
    )


def render_table_window(
    table: DocumentTable,
    rows: list[list[Any]],
) -> str:
    """Render a retrieval-safe table window."""

    parts: list[str] = []

    if table.title:
        parts.append(
            f"Table: {table.title}"
        )

    if table.columns:
        parts.append(
            " | ".join(table.columns)
        )

    parts.extend(
        row_to_text(row)
        for row in rows
    )

    if table.units:
        unit_text = ", ".join(
            f"{column}={unit}"
            for column, unit
            in table.units.items()
        )

        parts.append(
            f"Units: {unit_text}"
        )

    return "\n".join(parts)


class TableChunker(BaseChunker):
    """
    Chunk tabular engineering content using bounded row windows.
    """

    name = "table"
    priority = 50

    def supports(
        self,
        document: WaterDIPDocument,
    ) -> bool:
        return bool(document.tables)

    def chunk(
        self,
        document: WaterDIPDocument,
        context: ChunkingContext,
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []

        chunk_index = 0

        for table_index, table in enumerate(
            document.tables
        ):
            if not table.rows:
                text = render_table_window(
                    table,
                    [],
                )

                if text.strip():
                    chunks.append(
                        self._create_chunk(
                            document=document,
                            table=table,
                            table_index=table_index,
                            chunk_index=chunk_index,
                            row_start=None,
                            row_end=None,
                            text=text,
                        )
                    )

                    chunk_index += 1

                continue

            current_rows: list[list[Any]] = []
            row_start = 0

            for row_index, row in enumerate(
                table.rows
            ):
                candidate_rows = [
                    *current_rows,
                    row,
                ]

                candidate_text = render_table_window(
                    table,
                    candidate_rows,
                )

                if (
                    current_rows
                    and count_tokens(candidate_text)
                    > context.max_tokens
                ):
                    text = render_table_window(
                        table,
                        current_rows,
                    )

                    chunks.append(
                        self._create_chunk(
                            document=document,
                            table=table,
                            table_index=table_index,
                            chunk_index=chunk_index,
                            row_start=row_start,
                            row_end=row_index - 1,
                            text=text,
                        )
                    )

                    chunk_index += 1

                    row_start = row_index
                    current_rows = [row]

                else:
                    current_rows.append(row)

            if current_rows:
                text = render_table_window(
                    table,
                    current_rows,
                )

                chunks.append(
                    self._create_chunk(
                        document=document,
                        table=table,
                        table_index=table_index,
                        chunk_index=chunk_index,
                        row_start=row_start,
                        row_end=(
                            row_start
                            + len(current_rows)
                            - 1
                        ),
                        text=text,
                    )
                )

                chunk_index += 1

        return chunks

    def _create_chunk(
        self,
        *,
        document: WaterDIPDocument,
        table: DocumentTable,
        table_index: int,
        chunk_index: int,
        row_start: int | None,
        row_end: int | None,
        text: str,
    ) -> DocumentChunk:
        chunk = DocumentChunk.create(
            document_id=document.id,
            dataset_id=document.source.dataset_id,
            index=chunk_index,
            text=text,
            chunk_type=ChunkType.TABLE,
            position=ChunkPosition(
                index=chunk_index,
                page_start=table.page,
                page_end=table.page,
                section_id=table.section_id,
            ),
            engineering=document.engineering,
            metadata={
                "chunker": self.name,
                "table_id": table.id,
                "table_index": table_index,
                "table_title": table.title,
                "row_start": row_start,
                "row_end": row_end,
                "columns": table.columns,
                "units": table.units,
                "source_filename": (
                    document.source.filename
                ),
            },
        )

        chunk.token_count = count_tokens(
            text
        )

        return chunk