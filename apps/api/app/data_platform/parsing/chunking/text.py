"""
Generic recursive text chunking for WaterDIP.
"""

from __future__ import annotations

from ..models import (
    ChunkPosition,
    ChunkType,
    DocumentChunk,
    WaterDIPDocument,
)
from .base import BaseChunker, ChunkingContext
from .tokenizer import (
    count_tokens,
    join_tokens,
    tokenize,
)


def split_token_window(
    text: str,
    *,
    max_tokens: int,
    overlap_tokens: int,
) -> list[str]:
    """Split oversized text using deterministic token windows."""

    tokens = tokenize(text)

    if len(tokens) <= max_tokens:
        return [text.strip()] if text.strip() else []

    chunks: list[str] = []

    step = max_tokens - overlap_tokens

    start = 0

    while start < len(tokens):
        end = min(
            start + max_tokens,
            len(tokens),
        )

        chunk_text = join_tokens(
            tokens[start:end]
        ).strip()

        if chunk_text:
            chunks.append(chunk_text)

        if end >= len(tokens):
            break

        start += step

    return chunks


def split_paragraphs(
    text: str,
) -> list[str]:
    """Split text into non-empty paragraphs."""

    return [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]


def chunk_text_content(
    text: str,
    *,
    max_tokens: int,
    overlap_tokens: int,
) -> list[str]:
    """
    Chunk text while preferring paragraph boundaries.

    Oversized individual paragraphs fall back to token windows.
    """

    text = text.strip()

    if not text:
        return []

    if count_tokens(text) <= max_tokens:
        return [text]

    paragraphs = split_paragraphs(text)

    if len(paragraphs) <= 1:
        return split_token_window(
            text,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
        )

    output: list[str] = []
    current: list[str] = []

    for paragraph in paragraphs:
        paragraph_tokens = count_tokens(
            paragraph
        )

        if paragraph_tokens > max_tokens:
            if current:
                output.append(
                    "\n\n".join(current)
                )
                current = []

            output.extend(
                split_token_window(
                    paragraph,
                    max_tokens=max_tokens,
                    overlap_tokens=overlap_tokens,
                )
            )

            continue

        candidate = "\n\n".join(
            [
                *current,
                paragraph,
            ]
        )

        if (
            current
            and count_tokens(candidate)
            > max_tokens
        ):
            output.append(
                "\n\n".join(current)
            )
            current = [paragraph]
        else:
            current.append(paragraph)

    if current:
        output.append(
            "\n\n".join(current)
        )

    return output


class TextChunker(BaseChunker):
    """Fallback chunker for generic canonical document text."""

    name = "text"
    priority = 1000

    def supports(
        self,
        document: WaterDIPDocument,
    ) -> bool:
        return bool(document.text.strip())

    def chunk(
        self,
        document: WaterDIPDocument,
        context: ChunkingContext,
    ) -> list[DocumentChunk]:
        parts = chunk_text_content(
            document.text,
            max_tokens=context.max_tokens,
            overlap_tokens=context.overlap_tokens,
        )

        chunks: list[DocumentChunk] = []

        search_start = 0

        for index, text in enumerate(parts):
            character_start = document.text.find(
                text,
                search_start,
            )

            if character_start < 0:
                character_start = None
                character_end = None
            else:
                character_end = (
                    character_start
                    + len(text)
                )
                search_start = character_start + 1

            chunks.append(
                DocumentChunk.create(
                    document_id=document.id,
                    dataset_id=document.source.dataset_id,
                    index=index,
                    text=text,
                    chunk_type=ChunkType.TEXT,
                    position=ChunkPosition(
                        index=index,
                        character_start=character_start,
                        character_end=character_end,
                    ),
                    engineering=document.engineering,
                    metadata={
                        "chunker": self.name,
                        "source_filename": (
                            document.source.filename
                        ),
                    },
                )
            )

            chunks[-1].token_count = count_tokens(
                text
            )

        return chunks