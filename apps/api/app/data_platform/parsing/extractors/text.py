"""
Plain-text parser for WaterDIP.
"""

from __future__ import annotations

from ..base import BaseParser, ParseSource, ParserContext
from ..models import (
    DocumentType,
    WaterDIPDocument,
)
from .common import (
    build_source_provenance,
    decode_text,
    filename_title,
    normalise_text,
    section_from_text,
)


class TextParser(BaseParser[WaterDIPDocument]):
    """Parse plain-text engineering documents."""

    name = "text"
    parser_version = "1.0"

    supported_extensions = frozenset(
        {
            ".txt",
            ".text",
            ".md",
            ".log",
        }
    )

    supported_media_types = frozenset(
        {
            "text/plain",
            "text/markdown",
        }
    )

    priority = 100

    def parse(
        self,
        source: ParseSource,
        context: ParserContext,
    ) -> WaterDIPDocument:
        content = source.read_bytes()

        raw_text, encoding = decode_text(content)
        text = normalise_text(raw_text)

        provenance = build_source_provenance(
            source,
            context,
            parser_name=self.name,
            parser_version=self.parser_version,
            metadata={
                "encoding": encoding,
            },
        )

        sections = []

        if text:
            sections.append(
                section_from_text(
                    document_identity=provenance.checksum_sha256,
                    index=0,
                    title=filename_title(source.filename),
                    text=text,
                )
            )

        return WaterDIPDocument.create(
            source=provenance,
            title=filename_title(source.filename),
            text=text,
            document_type=DocumentType.TEXT,
            sections=sections,
            metadata={
                "encoding": encoding,
            },
        )