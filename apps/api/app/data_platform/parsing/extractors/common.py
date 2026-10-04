"""
Shared utilities for WaterDIP concrete engineering parsers.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from ..base import ParseSource, ParserContext
from ..models import (
    DocumentSection,
    SourceLocation,
    SourceProvenance,
)


_WHITESPACE_RE = re.compile(r"[ \t]+")
_MULTIPLE_BLANK_LINES_RE = re.compile(r"\n{3,}")


def deterministic_id(
    prefix: str,
    *parts: object,
) -> str:
    """Create a deterministic WaterDIP identifier."""

    identity = "|".join(
        str(part)
        for part in parts
    )

    return f"{prefix}-{uuid5(NAMESPACE_URL, identity)}"


def normalise_text(
    text: str,
    *,
    preserve_line_breaks: bool = True,
) -> str:
    """
    Normalize extracted text while preserving useful document structure.
    """

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    if preserve_line_breaks:
        lines = [
            _WHITESPACE_RE.sub(" ", line).strip()
            for line in text.split("\n")
        ]

        output = "\n".join(lines)
        output = _MULTIPLE_BLANK_LINES_RE.sub("\n\n", output)

        return output.strip()

    return " ".join(text.split())


def decode_text(
    content: bytes,
    *,
    encodings: tuple[str, ...] = (
        "utf-8-sig",
        "utf-8",
        "utf-16",
        "cp1252",
        "latin-1",
    ),
) -> tuple[str, str]:
    """
    Decode textual source bytes using conservative fallback encodings.

    Returns
    -------
    tuple[str, str]
        Decoded text and the encoding used.
    """

    last_error: UnicodeDecodeError | None = None

    for encoding in encodings:
        try:
            return content.decode(encoding), encoding
        except UnicodeDecodeError as exc:
            last_error = exc

    if last_error is not None:
        raise last_error

    raise UnicodeDecodeError(
        "utf-8",
        content,
        0,
        len(content),
        "Unable to decode source.",
    )


def source_location(
    source: ParseSource,
) -> SourceLocation | None:
    """Build canonical location information from a ParseSource."""

    if not source.path and not source.uri:
        return None

    uri = source.uri
    path = str(source.path) if source.path else None

    bucket: str | None = None
    key: str | None = None
    provider: str | None = None

    if uri and uri.startswith("s3://"):
        provider = "aws"

        remainder = uri[5:]

        if "/" in remainder:
            bucket, key = remainder.split("/", 1)
        else:
            bucket = remainder
            key = ""

    elif uri and (
        uri.startswith("az://")
        or uri.startswith("azure://")
    ):
        provider = "azure"

    elif path:
        provider = "local"

    return SourceLocation(
        uri=uri,
        path=path,
        bucket=bucket,
        key=key,
        provider=provider,
    )


def build_source_provenance(
    source: ParseSource,
    context: ParserContext,
    *,
    parser_name: str,
    parser_version: str,
    checksum: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> SourceProvenance:
    """Build canonical provenance for a parser output."""

    checksum_value = checksum or source.checksum()

    combined_metadata = dict(source.metadata)

    if metadata:
        combined_metadata.update(metadata)

    if context.metadata:
        combined_metadata.setdefault(
            "pipeline",
            dict(context.metadata),
        )

    return SourceProvenance(
        dataset_id=source.dataset_id,
        source_id=combined_metadata.get("source_id"),
        source_name=combined_metadata.get("source_name"),
        filename=source.filename or "unknown",
        extension=source.extension,
        media_type=source.media_type,
        size_bytes=source.size_bytes,
        checksum_sha256=checksum_value,
        location=source_location(source),
        parsed_at=datetime.now(timezone.utc),
        parser_name=parser_name,
        parser_version=parser_version,
        metadata=combined_metadata,
    )


def section_from_text(
    *,
    document_identity: str,
    index: int,
    text: str,
    title: str | None = None,
    level: int = 1,
    page_start: int | None = None,
    page_end: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> DocumentSection:
    """Create a deterministic canonical document section."""

    return DocumentSection(
        id=deterministic_id(
            "wd-section",
            document_identity,
            index,
            title or "",
        ),
        title=title,
        level=level,
        text=text,
        page_start=page_start,
        page_end=page_end,
        order=index,
        metadata=metadata or {},
    )


def filename_title(
    filename: str | None,
) -> str | None:
    """Create a reasonable title from a filename."""

    if not filename:
        return None

    stem = Path(filename).stem

    stem = stem.replace("_", " ").replace("-", " ")
    stem = " ".join(stem.split())

    return stem or None