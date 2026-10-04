"""
Structured content models extracted from engineering documents.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator

from .common import ContentType, WaterDIPModel


class BoundingBox(WaterDIPModel):
    """
    Optional document-coordinate bounding box.

    Useful for PDFs and other layout-aware document formats.
    """

    x0: float
    y0: float
    x1: float
    y1: float

    page: int | None = Field(
        default=None,
        ge=1,
    )


class DocumentSection(WaterDIPModel):
    """
    Logical section extracted from a document.
    """

    id: str

    title: str | None = None

    level: int = Field(
        default=1,
        ge=1,
    )

    content_type: ContentType = ContentType.TEXT

    text: str = ""

    page_start: int | None = Field(
        default=None,
        ge=1,
    )

    page_end: int | None = Field(
        default=None,
        ge=1,
    )

    parent_id: str | None = None

    order: int = Field(
        default=0,
        ge=0,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class TableCell(WaterDIPModel):
    """Canonical table cell."""

    value: Any = None

    row: int = Field(
        ge=0,
    )

    column: int = Field(
        ge=0,
    )

    row_span: int = Field(
        default=1,
        ge=1,
    )

    column_span: int = Field(
        default=1,
        ge=1,
    )

    is_header: bool = False


class DocumentTable(WaterDIPModel):
    """
    Table extracted from an engineering document.

    Both row-oriented data and cell-level representations are supported.
    """

    id: str

    title: str | None = None

    page: int | None = Field(
        default=None,
        ge=1,
    )

    section_id: str | None = None

    columns: list[str] = Field(
        default_factory=list,
    )

    rows: list[list[Any]] = Field(
        default_factory=list,
    )

    cells: list[TableCell] = Field(
        default_factory=list,
    )

    units: dict[str, str] = Field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("columns")
    @classmethod
    def clean_columns(
        cls,
        values: list[str],
    ) -> list[str]:
        """Normalize column labels without changing their order."""

        return [
            value.strip()
            for value in values
        ]


class DocumentFigure(WaterDIPModel):
    """Figure, image, chart, or diagram extracted from a document."""

    id: str

    title: str | None = None
    caption: str | None = None

    page: int | None = Field(
        default=None,
        ge=1,
    )

    section_id: str | None = None

    figure_type: str | None = None

    bounding_box: BoundingBox | None = None

    image_path: str | None = None

    extracted_text: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class DocumentAttachment(WaterDIPModel):
    """
    Embedded or related source artifact.

    Particularly useful for ZIP archives and compound engineering packages.
    """

    id: str

    filename: str

    media_type: str | None = None

    size_bytes: int | None = Field(
        default=None,
        ge=0,
    )

    checksum_sha256: str | None = None

    source_uri: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )