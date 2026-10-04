"""
Exception hierarchy for the WaterDIP engineering parser framework.

The parser framework raises domain-specific exceptions so callers can
distinguish unsupported files, malformed inputs, parser failures, validation
errors, and pipeline orchestration failures.
"""

from __future__ import annotations

from typing import Any


class ParsingError(Exception):
    """
    Base exception for all WaterDIP parsing errors.

    Parameters
    ----------
    message:
        Human-readable error description.
    parser_name:
        Optional parser responsible for the error.
    source:
        Optional source identifier, path, or URI.
    details:
        Optional structured diagnostic information.
    """

    def __init__(
        self,
        message: str,
        *,
        parser_name: str | None = None,
        source: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.parser_name = parser_name
        self.source = source
        self.details = details or {}

    def __str__(self) -> str:
        context: list[str] = []

        if self.parser_name:
            context.append(f"parser={self.parser_name}")

        if self.source:
            context.append(f"source={self.source}")

        if not context:
            return self.message

        return f"{self.message} ({', '.join(context)})"


class InvalidParseSourceError(ParsingError):
    """Raised when a parse source is missing, inaccessible, or malformed."""


class SourceReadError(ParsingError):
    """Raised when source bytes cannot be read."""


class UnsupportedFileTypeError(ParsingError):
    """Raised when no registered parser supports the supplied source."""


class ParserRegistrationError(ParsingError):
    """Raised when a parser cannot be registered."""


class DuplicateParserError(ParserRegistrationError):
    """Raised when a parser name has already been registered."""


class ParserNotFoundError(ParsingError):
    """Raised when a parser cannot be found by name."""


class ParserSelectionError(ParsingError):
    """Raised when parser selection cannot be completed reliably."""


class AmbiguousParserError(ParserSelectionError):
    """Raised when multiple parsers have the same selection priority."""


class ParserExecutionError(ParsingError):
    """Raised when a parser fails while processing a source."""


class ParserValidationError(ParsingError):
    """Raised when parsed output fails parser-level validation."""


class MetadataExtractionError(ParsingError):
    """Raised when metadata extraction fails."""


class PipelineStageError(ParsingError):
    """Raised when a processing pipeline stage fails."""

    def __init__(
        self,
        message: str,
        *,
        stage_name: str,
        parser_name: str | None = None,
        source: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            parser_name=parser_name,
            source=source,
            details=details,
        )
        self.stage_name = stage_name

    def __str__(self) -> str:
        return f"[stage={self.stage_name}] {super().__str__()}"


class PipelineExecutionError(ParsingError):
    """Raised when the parsing pipeline cannot complete successfully."""


class PipelineConfigurationError(ParsingError):
    """Raised when the parsing pipeline configuration is invalid."""