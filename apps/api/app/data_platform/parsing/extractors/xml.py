"""
Secure XML parser for WaterDIP structured engineering data.
"""

from __future__ import annotations

from typing import Any

from defusedxml import ElementTree as ET

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
)


def local_tag(tag: str) -> str:
    """Remove an XML namespace from an element tag."""

    if "}" in tag:
        return tag.rsplit("}", 1)[-1]

    return tag


def element_to_dict(
    element: Any,
) -> dict[str, Any]:
    """
    Convert an XML element into a conservative serialisable representation.
    """

    node: dict[str, Any] = {
        "tag": local_tag(str(element.tag)),
    }

    if element.attrib:
        node["attributes"] = dict(element.attrib)

    text = normalise_text(
        element.text or "",
    )

    if text:
        node["text"] = text

    children = [
        element_to_dict(child)
        for child in list(element)
    ]

    if children:
        node["children"] = children

    return node


class XMLParser(BaseParser[WaterDIPDocument]):
    """Parse XML engineering datasets securely."""

    name = "xml"
    parser_version = "1.0"

    supported_extensions = frozenset({".xml"})

    supported_media_types = frozenset(
        {
            "application/xml",
            "text/xml",
        }
    )

    priority = 40

    def parse(
        self,
        source: ParseSource,
        context: ParserContext,
    ) -> WaterDIPDocument:
        content = source.read_bytes()

        # Decode separately for human-readable canonical text metadata.
        _, encoding = decode_text(content)

        root = ET.fromstring(content)

        structured = element_to_dict(root)

        text_values = [
            normalise_text(value)
            for value in root.itertext()
            if normalise_text(value)
        ]

        text = "\n".join(text_values)

        root_tag = local_tag(str(root.tag))

        provenance = build_source_provenance(
            source,
            context,
            parser_name=self.name,
            parser_version=self.parser_version,
            metadata={
                "encoding": encoding,
                "xml_root_tag": root_tag,
            },
        )

        return WaterDIPDocument.create(
            source=provenance,
            title=filename_title(source.filename),
            text=text,
            document_type=DocumentType.STRUCTURED_DATA,
            metadata={
                "encoding": encoding,
                "xml_root_tag": root_tag,
                "structured_data": structured,
            },
        )