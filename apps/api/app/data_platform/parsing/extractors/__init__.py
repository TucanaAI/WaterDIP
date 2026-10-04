"""
Built-in WaterDIP document parsers.
"""

from __future__ import annotations

from ..registry import ParserRegistry, default_parser_registry
from .csv import CSVParser
from .docx import DOCXParser
from .excel import ExcelParser
from .json import JSONParser
from .pdf import PDFParser
from .text import TextParser
from .xml import XMLParser
from .zip import ZIPParser
from .las import LASParser


BUILTIN_PARSER_CLASSES = (
    LASParser,
    PDFParser,
    CSVParser,
    ExcelParser,
    DOCXParser,
    JSONParser,
    XMLParser,
    ZIPParser,
    TextParser,
)


def register_builtin_parsers(
    registry: ParserRegistry | None = None,
    *,
    replace: bool = False,
) -> ParserRegistry:
    """
    Register all built-in WaterDIP parsers.

    Registration is explicit rather than occurring as an import side effect.
    """

    #target = registry or default_parser_registry

    target = (registry if registry is not None else default_parser_registry)

    for parser_class in BUILTIN_PARSER_CLASSES:
        target.register_class(
            parser_class,
            replace=replace,
        )

    return target


__all__ = [
    "BUILTIN_PARSER_CLASSES",
    "LASParser",
    "CSVParser",
    "DOCXParser",
    "ExcelParser",
    "JSONParser",
    "PDFParser",
    "TextParser",
    "XMLParser",
    "ZIPParser",
    "register_builtin_parsers",
]