"""
CSV parser for WaterDIP tabular engineering data.
"""

from __future__ import annotations

import csv
from io import StringIO
from typing import Any

from ..base import BaseParser, ParseSource, ParserContext
from ..models import (
    DocumentTable,
    DocumentType,
    WaterDIPDocument,
)
from .common import (
    build_source_provenance,
    decode_text,
    deterministic_id,
    filename_title,
)


class CSVParser(BaseParser[WaterDIPDocument]):
    """Parse CSV engineering datasets."""

    name = "csv"
    parser_version = "1.0"

    supported_extensions = frozenset({".csv"})

    supported_media_types = frozenset(
        {
            "text/csv",
            "application/csv",
        }
    )

    priority = 30

    def parse(
        self,
        source: ParseSource,
        context: ParserContext,
    ) -> WaterDIPDocument:
        content = source.read_bytes()
        raw_text, encoding = decode_text(content)

        sample = raw_text[:8192]

        delimiter = ","

        try:
            dialect = csv.Sniffer().sniff(
                sample,
                delimiters=",;\t|",
            )
            delimiter = dialect.delimiter
        except csv.Error:
            pass

        reader = csv.reader(
            StringIO(raw_text),
            delimiter=delimiter,
        )

        all_rows = list(reader)

        if all_rows:
            columns = [
                str(value).strip()
                for value in all_rows[0]
            ]
            rows: list[list[Any]] = [
                list(row)
                for row in all_rows[1:]
            ]
        else:
            columns = []
            rows = []

        checksum = source.checksum()

        table = DocumentTable(
            id=deterministic_id(
                "wd-table",
                checksum,
                0,
            ),
            title=filename_title(source.filename),
            columns=columns,
            rows=rows,
            metadata={
                "delimiter": delimiter,
                "encoding": encoding,
                "row_count": len(rows),
            },
        )

        text_lines: list[str] = []

        if columns:
            text_lines.append(
                " | ".join(columns)
            )

        for row in rows:
            text_lines.append(
                " | ".join(
                    str(value)
                    for value in row
                )
            )

        text = "\n".join(text_lines)

        provenance = build_source_provenance(
            source,
            context,
            parser_name=self.name,
            parser_version=self.parser_version,
            checksum=checksum,
            metadata={
                "encoding": encoding,
                "delimiter": delimiter,
                "row_count": len(rows),
                "column_count": len(columns),
            },
        )

        return WaterDIPDocument.create(
            source=provenance,
            title=filename_title(source.filename),
            text=text,
            document_type=DocumentType.TABULAR_DATA,
            tables=[table],
            metadata={
                "encoding": encoding,
                "delimiter": delimiter,
                "row_count": len(rows),
                "column_count": len(columns),
            },
        )