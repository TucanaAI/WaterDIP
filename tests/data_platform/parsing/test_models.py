from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from app.data_platform.parsing import (
    ChunkPosition,
    DocumentChunk,
    DocumentSection,
    DocumentTable,
    DocumentType,
    EngineeringEntity,
    EngineeringEntityType,
    EngineeringMetadata,
    ExtractionMethod,
    Measurement,
    ReservoirContext,
    SourceLocation,
    SourceProvenance,
    WaterDIPDocument,
    WellContext,
)


def make_checksum(
    content: bytes = b"WaterDIP engineering document",
) -> str:
    return hashlib.sha256(content).hexdigest()


def make_source() -> SourceProvenance:
    return SourceProvenance(
        dataset_id="volve",
        source_id="source-001",
        source_name="Volve",
        filename="reservoir_report.pdf",
        extension=".pdf",
        media_type="application/pdf",
        size_bytes=2048,
        checksum_sha256=make_checksum(),
        parser_name="pdf",
        parser_version="1.0",
        location=SourceLocation(
            uri=(
                "s3://waterdip-data-lake/"
                "volve/reports/reservoir_report.pdf"
            ),
            bucket="waterdip-data-lake",
            key="volve/reports/reservoir_report.pdf",
            provider="aws",
            connector="s3",
        ),
    )


def test_source_provenance() -> None:
    source = make_source()

    assert source.dataset_id == "volve"
    assert source.filename == "reservoir_report.pdf"
    assert source.location is not None
    assert source.location.bucket == "waterdip-data-lake"
    assert len(source.checksum_sha256) == 64


def test_invalid_checksum_rejected() -> None:
    with pytest.raises(ValidationError):
        SourceProvenance(
            filename="bad.pdf",
            checksum_sha256="not-a-sha256",
        )


def test_engineering_metadata() -> None:
    engineering = EngineeringMetadata(
        well=WellContext(
            well_name="15/9-F-1 C",
            well_id="well-001",
        ),
        reservoir=ReservoirContext(
            field_name="Volve",
            formation_name="Hugin",
            operator="Equinor",
            porosity=Measurement(
                value=0.22,
                unit="fraction",
                extraction_method=ExtractionMethod.PARSER,
                confidence=0.95,
            ),
            permeability=Measurement(
                value=500.0,
                unit="mD",
            ),
        ),
        entities=[
            EngineeringEntity(
                entity_type=EngineeringEntityType.FIELD,
                name="Volve",
                extraction_method=ExtractionMethod.SOURCE,
                confidence=1.0,
            )
        ],
        keywords=[
            "reservoir",
            "water injection",
            "Reservoir",
        ],
    )

    assert engineering.well is not None
    assert engineering.well.well_name == "15/9-F-1 C"

    assert engineering.reservoir is not None
    assert engineering.reservoir.porosity is not None
    assert engineering.reservoir.porosity.value == 0.22

    # Duplicate keywords are removed case-insensitively.
    assert engineering.keywords == [
        "reservoir",
        "water injection",
    ]


def test_document_creation_is_deterministic() -> None:
    source = make_source()

    first = WaterDIPDocument.create(
        source=source,
        title="Reservoir Engineering Report",
        text="Reservoir pressure and production analysis.",
        document_type=DocumentType.RESERVOIR_REPORT,
    )

    second = WaterDIPDocument.create(
        source=source,
        title="Reservoir Engineering Report",
        text="Reservoir pressure and production analysis.",
        document_type=DocumentType.RESERVOIR_REPORT,
    )

    assert first.id == second.id
    assert first.id.startswith("wd-doc-")
    assert first.character_count == len(first.text)


def test_document_structured_content() -> None:
    source = make_source()

    document = WaterDIPDocument.create(
        source=source,
        title="Water Management Report",
        text=(
            "Water injection performance. "
            "Production performance."
        ),
        document_type=DocumentType.RESERVOIR_REPORT,
        sections=[
            DocumentSection(
                id="section-1",
                title="Water Injection",
                level=1,
                text="Water injection performance.",
                page_start=1,
                page_end=2,
                order=0,
            ),
            DocumentSection(
                id="section-2",
                title="Production",
                level=1,
                text="Production performance.",
                page_start=3,
                page_end=4,
                order=1,
            ),
        ],
        tables=[
            DocumentTable(
                id="table-1",
                title="Production Rates",
                page=3,
                columns=[
                    "Date",
                    "Oil Rate",
                    "Water Rate",
                ],
                rows=[
                    [
                        "2026-01-01",
                        1000.0,
                        500.0,
                    ]
                ],
                units={
                    "Oil Rate": "STB/d",
                    "Water Rate": "STB/d",
                },
            )
        ],
    )

    assert document.section_count == 2
    assert document.table_count == 1
    assert document.figure_count == 0

    assert (
        document.tables[0].units["Water Rate"]
        == "STB/d"
    )


def test_document_model_dump() -> None:
    document = WaterDIPDocument.create(
        source=make_source(),
        title="Volve Reservoir Report",
        text="Engineering intelligence.",
    )

    payload = document.model_dump(
        mode="json",
    )

    assert payload["id"] == document.id
    assert payload["source"]["dataset_id"] == "volve"
    assert payload["character_count"] == len(
        "Engineering intelligence."
    )


def test_chunk_creation_is_deterministic() -> None:
    document = WaterDIPDocument.create(
        source=make_source(),
        text="Reservoir engineering content.",
    )

    position = ChunkPosition(
        index=0,
        page_start=1,
        page_end=1,
        character_start=0,
        character_end=30,
        section_title="Reservoir",
    )

    first = DocumentChunk.create(
        document_id=document.id,
        dataset_id="volve",
        index=0,
        text="Reservoir engineering content.",
        position=position,
    )

    second = DocumentChunk.create(
        document_id=document.id,
        dataset_id="volve",
        index=0,
        text="Reservoir engineering content.",
        position=position,
    )

    assert first.id == second.id
    assert first.id.startswith("wd-chunk-")
    assert first.position.index == 0


def test_measurement_confidence_validation() -> None:
    with pytest.raises(ValidationError):
        Measurement(
            value=100.0,
            unit="psi",
            confidence=1.5,
        )


def test_well_coordinate_validation() -> None:
    with pytest.raises(ValidationError):
        WellContext(
            well_name="Invalid Well",
            surface_latitude=100.0,
        )