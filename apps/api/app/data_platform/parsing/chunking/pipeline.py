"""
Engineering-aware chunking pipeline for WaterDIP.
"""

from __future__ import annotations

from ..models import (
    DocumentChunk,
    WaterDIPDocument,
)
from .base import ChunkingContext
from .registry import (
    ChunkerRegistry,
    create_default_chunker_registry,
)


class EngineeringChunkingPipeline:
    """
    Orchestrate WaterDIP chunk generation.
    """

    def __init__(
        self,
        registry: ChunkerRegistry | None = None,
    ) -> None:
        self.registry = (
            registry
            if registry is not None
            else create_default_chunker_registry()
        )

    def run(
        self,
        document: WaterDIPDocument,
        *,
        context: ChunkingContext | None = None,
        multimodal: bool = False,
    ) -> list[DocumentChunk]:
        actual_context = (
            context
            if context is not None
            else ChunkingContext()
        )

        if multimodal:
            chunkers = self.registry.applicable(
                document
            )

            # Generic text is fallback only. If a structural chunker matched,
            # avoid duplicating the entire document through TextChunker.
            structural = [
                chunker
                for chunker in chunkers
                if chunker.name != "text"
            ]

            if structural:
                chunkers = structural

        else:
            chunkers = [
                self.registry.select(
                    document
                )
            ]

        raw_chunks: list[DocumentChunk] = []

        for chunker in chunkers:
            raw_chunks.extend(
                chunker.chunk(
                    document,
                    actual_context,
                )
            )

        return self._reindex_and_deduplicate(
            document,
            raw_chunks,
        )

    @staticmethod
    def _reindex_and_deduplicate(
        document: WaterDIPDocument,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:
        """
        Remove exact duplicate chunk content and assign globally consistent
        chunk indexes/IDs.
        """

        output: list[DocumentChunk] = []
        seen: set[
            tuple[str, str]
        ] = set()

        for chunk in chunks:
            chunker = str(
                chunk.metadata.get(
                    "chunker",
                    ""
                )
            )

            key = (
                chunker,
                chunk.text.strip(),
            )

            if key in seen:
                continue

            seen.add(key)

            new_index = len(output)

            rebuilt = DocumentChunk.create(
                document_id=document.id,
                dataset_id=chunk.dataset_id,
                index=new_index,
                text=chunk.text,
                chunk_type=chunk.chunk_type,
                position=chunk.position.model_copy(
                    update={
                        "index": new_index,
                    }
                ),
                engineering=chunk.engineering,
                metadata=dict(
                    chunk.metadata
                ),
            )

            rebuilt.token_count = (
                chunk.token_count
            )

            output.append(rebuilt)

        return output