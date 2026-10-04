from __future__ import annotations

import hashlib

from app.data_platform.parsing import (
    ChunkType,
    ChunkingContext,
    DocumentSection,
    DocumentTable,
    DocumentType,
    EngineeringChunkingPipeline,
    SectionChunker,
    SourceProvenance,
    TableChunker,
    TextChunker,
    WaterDIPDocument,
    WellLogChunker,
    count_tokens,
    create_default_chunker_registry,
)


def checksum() -> str:
    return hashlib.sha256(
        b"WaterDIP chunking test"
    ).hexdigest()


def source() -> SourceProvenance:
    return SourceProvenance(
        dataset_id="test",
        filename="engineering.txt",
        checksum_sha256=checksum(),
    )


def test_token_count() -> None:
    assert count_tokens(
        "Reservoir pressure is stable."
    ) > 0


def test_text_chunker_small_document() -> None:
    document = WaterDIPDocument.create(
        source=source(),
        text=(
            "Reservoir pressure is stable. "
            "Water injection remains active."
        ),
        document_type=DocumentType.TEXT,
    )

    chunks = TextChunker().chunk(
        document,
        ChunkingContext(
            max_tokens=100,
            overlap_tokens=10,
        ),
    )

    assert len(chunks) == 1
    assert chunks[0].chunk_type == ChunkType.TEXT
    assert chunks[0].document_id == document.id


def test_text_chunker_splits_large_content() -> None:
    text = " ".join(
        f"word{index}"
        for index in range(100)
    )

    document = WaterDIPDocument.create(
        source=source(),
        text=text,
        document_type=DocumentType.TEXT,
    )

    chunks = TextChunker().chunk(
        document,
        ChunkingContext(
            max_tokens=20,
            overlap_tokens=5,
        ),
    )

    assert len(chunks) > 1

    assert all(
        chunk.token_count is not None
        for chunk in chunks
    )


def test_section_chunker_preserves_section() -> None:
    document = WaterDIPDocument.create(
        source=source(),
        text="Reservoir pressure analysis.",
        document_type=DocumentType.TECHNICAL_REPORT,
        sections=[
            DocumentSection(
                id="section-pressure",
                title="Reservoir Pressure",
                level=1,
                text=(
                    "Reservoir pressure remains "
                    "stable across the field."
                ),
                page_start=5,
                page_end=6,
                order=0,
            )
        ],
    )

    chunks = SectionChunker().chunk(
        document,
        ChunkingContext(),
    )

    assert len(chunks) == 1

    chunk = chunks[0]

    assert (
        chunk.position.section_title
        == "Reservoir Pressure"
    )

    assert chunk.position.page_start == 5

    assert (
        "Reservoir Pressure"
        in chunk.text
    )


def test_table_chunker_repeats_headers() -> None:
    document = WaterDIPDocument.create(
        source=source(),
        document_type=DocumentType.TABULAR_DATA,
        tables=[
            DocumentTable(
                id="production",
                title="Production History",
                columns=[
                    "DATE",
                    "OIL_RATE",
                    "WATER_RATE",
                ],
                rows=[
                    [
                        f"2026-01-{day:02d}",
                        1000 - day,
                        500 + day,
                    ]
                    for day in range(
                        1,
                        21,
                    )
                ],
                units={
                    "OIL_RATE": "STB/d",
                    "WATER_RATE": "STB/d",
                },
            )
        ],
    )

    chunks = TableChunker().chunk(
        document,
        ChunkingContext(
            max_tokens=40,
            overlap_tokens=5,
        ),
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert "DATE" in chunk.text
        assert "OIL_RATE" in chunk.text
        assert "WATER_RATE" in chunk.text
        assert chunk.chunk_type == ChunkType.TABLE


def test_registry_prefers_table_over_text() -> None:
    document = WaterDIPDocument.create(
        source=source(),
        text="Generic table representation.",
        document_type=DocumentType.TABULAR_DATA,
        tables=[
            DocumentTable(
                id="table-1",
                columns=["A", "B"],
                rows=[[1, 2]],
            )
        ],
    )

    registry = (
        create_default_chunker_registry()
    )

    selected = registry.select(
        document
    )

    assert isinstance(
        selected,
        TableChunker,
    )


def test_registry_prefers_section_over_text() -> None:
    document = WaterDIPDocument.create(
        source=source(),
        text="Reservoir engineering report.",
        sections=[
            DocumentSection(
                id="section-1",
                title="Reservoir",
                text="Reservoir engineering.",
            )
        ],
    )

    registry = (
        create_default_chunker_registry()
    )

    selected = registry.select(
        document
    )

    assert isinstance(
        selected,
        SectionChunker,
    )


def test_well_log_chunker() -> None:
    document = WaterDIPDocument.create(
        source=source(),
        document_type=DocumentType.WELL_LOG,
        text="Well log.",
        metadata={
            "well_log": {
                "las_version": "2.0",
                "depth": {
                    "start": 1000.0,
                    "stop": 1200.0,
                    "step": 0.5,
                    "unit": "M",
                },
                "curves": [
                    {
                        "mnemonic": "GR",
                        "family": "gamma_ray",
                        "unit": "API",
                        "description": "Gamma Ray",
                        "statistics": {
                            "count": 400,
                            "null_count": 1,
                            "minimum": 20.0,
                            "maximum": 140.0,
                            "mean": 75.0,
                            "p10": 35.0,
                            "p50": 70.0,
                            "p90": 115.0,
                        },
                    }
                ],
            }
        },
    )

    chunker = WellLogChunker()

    assert chunker.supports(
        document
    )

    chunks = chunker.chunk(
        document,
        ChunkingContext(),
    )

    # One summary + one curve.
    assert len(chunks) == 2

    assert (
        chunks[0].chunk_type
        == ChunkType.WELL_LOG
    )

    assert (
        chunks[1].metadata[
            "curve_mnemonic"
        ]
        == "GR"
    )

    assert "Gamma Ray" in chunks[1].text


def test_pipeline_uses_primary_chunker() -> None:
    document = WaterDIPDocument.create(
        source=source(),
        text="Production data.",
        document_type=DocumentType.TABULAR_DATA,
        tables=[
            DocumentTable(
                id="production",
                columns=[
                    "DATE",
                    "OIL",
                ],
                rows=[
                    [
                        "2026-01-01",
                        1000,
                    ]
                ],
            )
        ],
    )

    pipeline = (
        EngineeringChunkingPipeline()
    )

    chunks = pipeline.run(
        document
    )

    assert len(chunks) == 1

    assert (
        chunks[0].chunk_type
        == ChunkType.TABLE
    )


def test_chunk_ids_are_deterministic() -> None:
    document = WaterDIPDocument.create(
        source=source(),
        text="Reservoir engineering.",
        document_type=DocumentType.TEXT,
    )

    pipeline = (
        EngineeringChunkingPipeline()
    )

    first = pipeline.run(
        document
    )

    second = pipeline.run(
        document
    )

    assert [
        chunk.id
        for chunk in first
    ] == [
        chunk.id
        for chunk in second
    ]


def test_multimodal_document_chunking() -> None:
    document = WaterDIPDocument.create(
        source=source(),
        text="Reservoir section and table.",
        document_type=DocumentType.TECHNICAL_REPORT,
        sections=[
            DocumentSection(
                id="section-1",
                title="Production",
                text=(
                    "Production performance "
                    "remained stable."
                ),
            )
        ],
        tables=[
            DocumentTable(
                id="table-1",
                title="Production Rates",
                columns=[
                    "DATE",
                    "OIL_RATE",
                ],
                rows=[
                    [
                        "2026-01-01",
                        1000,
                    ]
                ],
            )
        ],
    )

    pipeline = (
        EngineeringChunkingPipeline()
    )

    chunks = pipeline.run(
        document,
        multimodal=True,
    )

    types = {
        chunk.chunk_type
        for chunk in chunks
    }

    assert ChunkType.SECTION in types
    assert ChunkType.TABLE in types
    assert ChunkType.TEXT not in types