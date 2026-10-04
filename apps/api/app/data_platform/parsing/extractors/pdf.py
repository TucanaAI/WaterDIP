"""
PDF parser for WaterDIP engineering documents.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from pypdf import PdfReader

from ..base import BaseParser, ParseSource, ParserContext
from ..models import (
    DocumentType,
    WaterDIPDocument,
)
from .common import (
    build_source_provenance,
    filename_title,
    normalise_text,
    section_from_text,
)


class PDFParser(BaseParser[WaterDIPDocument]):
    """
    Extract text and page structure from text-based PDF documents.

    This parser intentionally does not perform OCR.
    """

    name = "pdf"
    parser_version = "1.0"

    supported_extensions = frozenset({".pdf"})

    supported_media_types = frozenset(
        {
            "application/pdf",
        }
    )

    priority = 20

    def parse(
        self,
        source: ParseSource,
        context: ParserContext,
    ) -> WaterDIPDocument:
        content = source.read_bytes()

        reader = PdfReader(
            BytesIO(content),
            strict=False,
        )

        page_texts: list[str] = []
        sections = []
        warnings: list[str] = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            try:
                extracted = page.extract_text() or ""
            except Exception as exc:
                extracted = ""
                warnings.append(
                    f"Unable to extract text from page "
                    f"{page_number}: {exc}"
                )

            text = normalise_text(extracted)

            page_texts.append(text)

            if text:
                sections.append(
                    section_from_text(
                        document_identity=source.checksum(),
                        index=page_number - 1,
                        title=f"Page {page_number}",
                        text=text,
                        page_start=page_number,
                        page_end=page_number,
                        metadata={
                            "page_number": page_number,
                        },
                    )
                )

        text = "\n\n".join(
            page_text
            for page_text in page_texts
            if page_text
        )

        pdf_metadata: dict[str, Any] = {}

        if reader.metadata:
            for key, value in reader.metadata.items():
                if value is None:
                    continue

                pdf_metadata[str(key)] = str(value)

        title = None

        if reader.metadata:
            metadata_title = getattr(
                reader.metadata,
                "title",
                None,
            )

            if metadata_title:
                title = str(metadata_title).strip() or None

        title = title or filename_title(source.filename)

        provenance = build_source_provenance(
            source,
            context,
            parser_name=self.name,
            parser_version=self.parser_version,
            metadata={
                "pdf_metadata": pdf_metadata,
                "page_count": len(reader.pages),
            },
        )

        if not text and len(reader.pages) > 0:
            warnings.append(
                "No extractable PDF text was found. "
                "The document may require OCR."
            )

        document = WaterDIPDocument.create(
            source=provenance,
            title=title,
            text=text,
            document_type=DocumentType.DOCUMENT,
            sections=sections,
            metadata={
                "page_count": len(reader.pages),
                "pdf_metadata": pdf_metadata,
            },
        )

        document.warnings.extend(warnings)

        return document