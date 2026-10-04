"""
Section-aware engineering document chunker.
"""

from __future__ import annotations

from ..models import (
    ChunkPosition,
    ChunkType,
    DocumentChunk,
    WaterDIPDocument,
)
from .base import BaseChunker, ChunkingContext
from .text import chunk_text_content
from .tokenizer import count_tokens


class SectionChunker(BaseChunker):
    """
    Chunk structured documents while preserving section semantics.
    """

    name = "section"
    priority = 100

    def supports(
        self,
        document: WaterDIPDocument,
    ) -> bool:
        return bool(document.sections)

    def chunk(
        self,
        document: WaterDIPDocument,
        context: ChunkingContext,
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []

        chunk_index = 0

        for section in sorted(
            document.sections,
            key=lambda item: item.order,
        ):
            section_text = section.text.strip()

            if not section_text:
                continue

            parts = chunk_text_content(
                section_text,
                max_tokens=context.max_tokens,
                overlap_tokens=context.overlap_tokens,
            )

            for part_index, part in enumerate(
                parts
            ):
                if section.title:
                    chunk_text = (
                        f"{section.title}\n\n{part}"
                    )
                else:
                    chunk_text = part

                chunk = DocumentChunk.create(
                    document_id=document.id,
                    dataset_id=document.source.dataset_id,
                    index=chunk_index,
                    text=chunk_text,
                    chunk_type=ChunkType.SECTION,
                    position=ChunkPosition(
                        index=chunk_index,
                        page_start=section.page_start,
                        page_end=section.page_end,
                        section_id=section.id,
                        section_title=section.title,
                    ),
                    engineering=document.engineering,
                    metadata={
                        "chunker": self.name,
                        "section_level": section.level,
                        "section_order": section.order,
                        "section_part": part_index,
                        "source_filename": (
                            document.source.filename
                        ),
                    },
                )

                chunk.token_count = count_tokens(
                    chunk_text
                )

                chunks.append(chunk)

                chunk_index += 1

        return chunks