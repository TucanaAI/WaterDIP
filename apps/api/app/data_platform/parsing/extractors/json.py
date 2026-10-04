"""
JSON parser for WaterDIP structured engineering data.
"""

from __future__ import annotations

import json
from typing import Any

from ..base import BaseParser, ParseSource, ParserContext
from ..models import (
    DocumentType,
    WaterDIPDocument,
)
from .common import (
    build_source_provenance,
    decode_text,
    filename_title,
)


class JSONParser(BaseParser[WaterDIPDocument]):
    """Parse JSON engineering datasets and metadata."""

    name = "json"
    parser_version = "1.0"

    supported_extensions = frozenset({".json"})

    supported_media_types = frozenset(
        {
            "application/json",
            "text/json",
        }
    )

    priority = 40

    def parse(
        self,
        source: ParseSource,
        context: ParserContext,
    ) -> WaterDIPDocument:
        content = source.read_bytes()
        raw_text, encoding = decode_text(content)

        payload: Any = json.loads(raw_text)

        canonical_text = json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        if isinstance(payload, dict):
            root_type = "object"
            root_keys = list(payload.keys())
            item_count = len(payload)

        elif isinstance(payload, list):
            root_type = "array"
            root_keys = []
            item_count = len(payload)

        else:
            root_type = type(payload).__name__
            root_keys = []
            item_count = 1

        provenance = build_source_provenance(
            source,
            context,
            parser_name=self.name,
            parser_version=self.parser_version,
            metadata={
                "encoding": encoding,
                "json_root_type": root_type,
            },
        )

        return WaterDIPDocument.create(
            source=provenance,
            title=filename_title(source.filename),
            text=canonical_text,
            document_type=DocumentType.STRUCTURED_DATA,
            metadata={
                "encoding": encoding,
                "json_root_type": root_type,
                "root_keys": root_keys,
                "item_count": item_count,
                "structured_data": payload,
            },
        )