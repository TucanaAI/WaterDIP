"""
Parser dispatcher for the WaterDIP engineering parser framework.

The dispatcher converts paths or byte content into ParseSource objects,
selects a parser through the registry, and executes it.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .base import (
    BaseParser,
    ParseSource,
    ParserContext,
    ParserOutput,
    ParserResult,
)
from .registry import ParserRegistry, default_parser_registry


class ParserDispatcher:
    """
    Select and execute registered parsers.

    Parameters
    ----------
    registry:
        Parser registry to use. The global registry is used by default.
    reject_ambiguous:
        Raise when multiple equally ranked parsers support a source.
    """

    def __init__(
        self,
        registry: ParserRegistry | None = None,
        *,
        reject_ambiguous: bool = False,
    ) -> None:
        self.registry = registry or default_parser_registry
        self.reject_ambiguous = reject_ambiguous

    def select_parser(
        self,
        source: ParseSource,
        *,
        parser_name: str | None = None,
    ) -> BaseParser[Any]:
        """Select a parser for the supplied source."""

        source.validate()

        return self.registry.select(
            source,
            parser_name=parser_name,
            reject_ambiguous=self.reject_ambiguous,
        )

    def dispatch(
        self,
        source: ParseSource,
        *,
        parser_name: str | None = None,
        context: ParserContext | None = None,
    ) -> ParserResult[ParserOutput]:
        """Select and execute a parser."""

        parser = self.select_parser(
            source,
            parser_name=parser_name,
        )

        return parser.execute(
            source,
            context=context,
        )

    def dispatch_path(
        self,
        path: str | Path,
        *,
        parser_name: str | None = None,
        dataset_id: str | None = None,
        uri: str | None = None,
        media_type: str | None = None,
        source_metadata: Mapping[str, Any] | None = None,
        context: ParserContext | None = None,
    ) -> ParserResult[ParserOutput]:
        """Parse a local filesystem path."""

        source = ParseSource.from_path(
            path,
            dataset_id=dataset_id,
            uri=uri,
            media_type=media_type,
            metadata=source_metadata,
        )

        return self.dispatch(
            source,
            parser_name=parser_name,
            context=context,
        )

    def dispatch_bytes(
        self,
        content: bytes,
        *,
        filename: str,
        parser_name: str | None = None,
        dataset_id: str | None = None,
        uri: str | None = None,
        media_type: str | None = None,
        source_metadata: Mapping[str, Any] | None = None,
        context: ParserContext | None = None,
    ) -> ParserResult[ParserOutput]:
        """Parse in-memory byte content."""

        source = ParseSource.from_bytes(
            content,
            filename=filename,
            dataset_id=dataset_id,
            uri=uri,
            media_type=media_type,
            metadata=source_metadata,
        )

        return self.dispatch(
            source,
            parser_name=parser_name,
            context=context,
        )