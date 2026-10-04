"""
Canonical WaterDIP engineering document model.

Every engineering parser should ultimately produce a WaterDIPDocument.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field, computed_field, field_validator

from .common import (
    DataQualityStatus,
    DocumentType,
    WaterDIPModel,
)
from .content import (
    DocumentAttachment,
    DocumentFigure,
    DocumentSection,
    DocumentTable,
)
from .engineering import EngineeringMetadata
from .source import SourceProvenance


def generate_document_id(
    *,
    checksum_sha256: str,
    dataset_id: str | None = None,
    filename: str | None = None,
) -> str:
    """
    Generate a deterministic WaterDIP document ID.

    Reprocessing the same source within the same dataset therefore produces
    the same canonical document identifier.
    """

    identity = "|".join(
        (
            dataset_id or "",
            filename or "",
            checksum_sha256.lower(),
        )
    )

    return f"wd-doc-{uuid5(NAMESPACE_URL, identity)}"


class WaterDIPDocument(WaterDIPModel):
    """
    Canonical parsed engineering document.

    This object forms the contract between parsing and all downstream
    intelligence layers.
    """

    id: str

    schema_version: str = "1.0"

    document_type: DocumentType = DocumentType.UNKNOWN

    title: str | None = None

    text: str = ""

    source: SourceProvenance

    engineering: EngineeringMetadata = Field(
        default_factory=EngineeringMetadata,
    )

    sections: list[DocumentSection] = Field(
        default_factory=list,
    )

    tables: list[DocumentTable] = Field(
        default_factory=list,
    )

    figures: list[DocumentFigure] = Field(
        default_factory=list,
    )

    attachments: list[DocumentAttachment] = Field(
        default_factory=list,
    )

    quality_status: DataQualityStatus = DataQualityStatus.UNKNOWN

    warnings: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator("id")
    @classmethod
    def validate_id(
        cls,
        value: str,
    ) -> str:
        if not value:
            raise ValueError(
                "Document ID cannot be empty."
            )

        return value

    @field_validator("warnings")
    @classmethod
    def clean_warnings(
        cls,
        values: list[str],
    ) -> list[str]:
        """Remove duplicate parser warnings."""

        output: list[str] = []
        seen: set[str] = set()

        for value in values:
            cleaned = value.strip()

            if not cleaned:
                continue

            if cleaned in seen:
                continue

            seen.add(cleaned)
            output.append(cleaned)

        return output

    @computed_field
    @property
    def character_count(self) -> int:
        """Number of characters in canonical document text."""

        return len(self.text)

    @computed_field
    @property
    def section_count(self) -> int:
        return len(self.sections)

    @computed_field
    @property
    def table_count(self) -> int:
        return len(self.tables)

    @computed_field
    @property
    def figure_count(self) -> int:
        return len(self.figures)

    @classmethod
    def create(
        cls,
        *,
        source: SourceProvenance,
        text: str = "",
        title: str | None = None,
        document_type: DocumentType = DocumentType.UNKNOWN,
        engineering: EngineeringMetadata | None = None,
        sections: list[DocumentSection] | None = None,
        tables: list[DocumentTable] | None = None,
        figures: list[DocumentFigure] | None = None,
        attachments: list[DocumentAttachment] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "WaterDIPDocument":
        """
        Construct a document with a deterministic ID.
        """

        document_id = generate_document_id(
            checksum_sha256=source.checksum_sha256,
            dataset_id=source.dataset_id,
            filename=source.filename,
        )

        return cls(
            id=document_id,
            document_type=document_type,
            title=title,
            text=text,
            source=source,
            engineering=engineering or EngineeringMetadata(),
            sections=sections or [],
            tables=tables or [],
            figures=figures or [],
            attachments=attachments or [],
            metadata=metadata or {},
        )

    def content_hash(self) -> str:
        """
        Generate a SHA-256 hash of canonical text content.

        This is distinct from the source checksum. The source checksum
        identifies the binary input while this hash identifies extracted text.
        """

        return hashlib.sha256(
            self.text.encode("utf-8")
        ).hexdigest()