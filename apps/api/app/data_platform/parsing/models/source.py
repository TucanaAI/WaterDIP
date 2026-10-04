"""
Source provenance models for WaterDIP engineering documents.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from .common import WaterDIPModel


class SourceLocation(WaterDIPModel):
    """
    Physical or logical location of an ingested source.

    Examples
    --------
    Local:
        C:/WaterDIP/data/raw/report.pdf

    S3:
        s3://waterdip-data-lake/volve/reports/report.pdf
    """

    uri: str | None = None
    path: str | None = None
    bucket: str | None = None
    key: str | None = None

    provider: str | None = None
    connector: str | None = None


class SourceProvenance(WaterDIPModel):
    """
    Complete provenance information for a parsed source.
    """

    dataset_id: str | None = None

    source_id: str | None = None
    source_name: str | None = None

    filename: str
    extension: str | None = None
    media_type: str | None = None

    size_bytes: int | None = Field(
        default=None,
        ge=0,
    )

    checksum_sha256: str

    location: SourceLocation | None = None

    created_at: datetime | None = None
    modified_at: datetime | None = None

    ingested_at: datetime | None = None
    parsed_at: datetime | None = None

    parser_name: str | None = None
    parser_version: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("checksum_sha256")
    @classmethod
    def validate_checksum(cls, value: str) -> str:
        """
        Validate a SHA-256 checksum.

        SHA-256 is represented by exactly 64 hexadecimal characters.
        """

        value = value.lower()

        if len(value) != 64:
            raise ValueError(
                "checksum_sha256 must contain exactly 64 hexadecimal characters."
            )

        try:
            int(value, 16)
        except ValueError as exc:
            raise ValueError(
                "checksum_sha256 must be a valid hexadecimal SHA-256 checksum."
            ) from exc

        return value