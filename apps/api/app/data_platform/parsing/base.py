"""
Core abstractions for the WaterDIP engineering parser framework.

This module defines:

- ParseSource
- ParserContext
- ParserOutput protocol
- ParserResult
- BaseParser
- PipelineStage
- Utility functions for checksums and media-type detection

Concrete parsers must inherit from BaseParser.
"""

from __future__ import annotations

import hashlib
import inspect
import mimetypes
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from .exceptions import (
    InvalidParseSourceError,
    ParserExecutionError,
    ParserValidationError,
    SourceReadError,
)


def utc_now() -> datetime:
    """Return the current UTC datetime."""

    return datetime.now(timezone.utc)


def normalise_extension(extension: str | None) -> str | None:
    """
    Normalise a file extension.

    Examples
    --------
    ``PDF`` becomes ``.pdf``.
    ``.LAS`` becomes ``.las``.
    """

    if not extension:
        return None

    value = extension.strip().lower()

    if not value:
        return None

    if not value.startswith("."):
        value = f".{value}"

    return value


def sha256_bytes(content: bytes) -> str:
    """Return the SHA-256 checksum for byte content."""

    return hashlib.sha256(content).hexdigest()


def detect_media_type(filename: str | None) -> str | None:
    """Infer a media type from a filename."""

    if not filename:
        return None

    media_type, _ = mimetypes.guess_type(filename)
    return media_type


@runtime_checkable
class ParserOutput(Protocol):
    """
    Protocol implemented by canonical parsed document models.

    Part 2 of the framework will introduce a concrete Pydantic document model.
    The core framework only requires output objects to expose a document ID and
    provide a serialisable dictionary representation.
    """

    id: str

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Return a serialisable document representation."""


@dataclass(slots=True)
class ParseSource:
    """
    Input supplied to a parser.

    A source may be represented by:

    - a local filesystem path;
    - in-memory bytes;
    - a cloud/object-storage URI accompanied by downloaded bytes.

    At least one of ``path`` or ``content`` must be provided.

    Parameters
    ----------
    path:
        Optional local filesystem path.
    content:
        Optional in-memory byte content.
    uri:
        Optional canonical source URI, such as an S3 URI.
    filename:
        Optional source filename override.
    media_type:
        Optional MIME/media type.
    dataset_id:
        Dataset registry identifier.
    metadata:
        Source-level metadata propagated into parser context.
    """

    path: Path | None = None
    content: bytes | None = None
    uri: str | None = None
    filename: str | None = None
    media_type: str | None = None
    dataset_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.path is not None and not isinstance(self.path, Path):
            self.path = Path(self.path)

        if self.path is None and self.content is None:
            raise InvalidParseSourceError(
                "A parse source requires either a local path or byte content.",
                source=self.uri,
            )

        if self.path is not None:
            self.path = self.path.expanduser()

        if self.filename is None and self.path is not None:
            self.filename = self.path.name

        if self.media_type is None:
            self.media_type = detect_media_type(self.filename)

    @classmethod
    def from_path(
        cls,
        path: str | Path,
        *,
        dataset_id: str | None = None,
        uri: str | None = None,
        media_type: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ParseSource:
        """Create a parse source from a local file path."""

        resolved_path = Path(path).expanduser()

        return cls(
            path=resolved_path,
            uri=uri,
            filename=resolved_path.name,
            media_type=media_type,
            dataset_id=dataset_id,
            metadata=dict(metadata or {}),
        )

    @classmethod
    def from_bytes(
        cls,
        content: bytes,
        *,
        filename: str,
        dataset_id: str | None = None,
        uri: str | None = None,
        media_type: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ParseSource:
        """Create a parse source from in-memory bytes."""

        return cls(
            content=content,
            uri=uri,
            filename=filename,
            media_type=media_type,
            dataset_id=dataset_id,
            metadata=dict(metadata or {}),
        )

    @property
    def identifier(self) -> str:
        """Return the most useful human-readable source identifier."""

        if self.uri:
            return self.uri

        if self.path:
            return str(self.path)

        if self.filename:
            return self.filename

        return "<in-memory-source>"

    @property
    def extension(self) -> str | None:
        """Return the normalised source extension."""

        if not self.filename:
            return None

        return normalise_extension(Path(self.filename).suffix)

    @property
    def exists(self) -> bool:
        """Return whether the source is currently readable."""

        if self.content is not None:
            return True

        return bool(self.path and self.path.is_file())

    @property
    def size_bytes(self) -> int | None:
        """Return source size without unnecessarily reading the whole file."""

        if self.content is not None:
            return len(self.content)

        if self.path and self.path.is_file():
            return self.path.stat().st_size

        return None

    def validate(self) -> None:
        """Validate that this source can be parsed."""

        if self.content is not None:
            return

        if self.path is None:
            raise InvalidParseSourceError(
                "The parse source has neither content nor a filesystem path.",
                source=self.identifier,
            )

        if not self.path.exists():
            raise InvalidParseSourceError(
                "The parse source path does not exist.",
                source=self.identifier,
            )

        if not self.path.is_file():
            raise InvalidParseSourceError(
                "The parse source path is not a file.",
                source=self.identifier,
            )

    def read_bytes(self) -> bytes:
        """Read and return source bytes."""

        if self.content is not None:
            return self.content

        self.validate()

        assert self.path is not None

        try:
            return self.path.read_bytes()
        except OSError as exc:
            raise SourceReadError(
                f"Unable to read parse source: {exc}",
                source=self.identifier,
            ) from exc

    def checksum(self) -> str:
        """Calculate the source SHA-256 checksum."""

        return sha256_bytes(self.read_bytes())


@dataclass(slots=True)
class ParserContext:
    """
    Runtime information passed to a parser.

    Context is intentionally separate from ParseSource so orchestration
    settings do not contaminate source metadata.
    """

    run_id: str | None = None
    strict: bool = True
    validate_output: bool = True
    include_raw_content: bool = False
    parser_options: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


OutputT = TypeVar("OutputT", bound=ParserOutput)


@dataclass(slots=True)
class ParserResult(Generic[OutputT]):
    """
    Result returned by parser execution.

    ``document`` contains the canonical parsed document. Diagnostics and
    warnings allow parsers to report recoverable issues without failing the
    complete pipeline.
    """

    document: OutputT
    parser_name: str
    source_identifier: str
    checksum: str
    started_at: datetime
    completed_at: datetime
    warnings: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        """Return parser execution duration in seconds."""

        return max(
            0.0,
            (self.completed_at - self.started_at).total_seconds(),
        )


class BaseParser(ABC, Generic[OutputT]):
    """
    Abstract base class for all WaterDIP parsers.

    Concrete parsers must implement:

    - ``name``
    - ``supported_extensions``
    - ``parse``

    Parsers may override:

    - ``supported_media_types``
    - ``priority``
    - ``supports``
    - ``validate_document``
    - ``extract_source_metadata``
    """

    name: str
    supported_extensions: frozenset[str] = frozenset()
    supported_media_types: frozenset[str] = frozenset()
    priority: int = 100

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if inspect.isabstract(cls):
            return

        parser_name = getattr(cls, "name", None)

        if not isinstance(parser_name, str) or not parser_name.strip():
            raise TypeError(
                f"{cls.__name__} must define a non-empty parser 'name'."
            )

        extensions = getattr(cls, "supported_extensions", frozenset())

        cls.supported_extensions = frozenset(
            extension
            for extension in (
                normalise_extension(value) for value in extensions
            )
            if extension is not None
        )

        media_types = getattr(cls, "supported_media_types", frozenset())

        cls.supported_media_types = frozenset(
            value.strip().lower()
            for value in media_types
            if isinstance(value, str) and value.strip()
        )

    def supports(self, source: ParseSource) -> bool:
        """
        Return whether this parser supports the supplied source.

        Extension matching is evaluated first, followed by media-type
        matching.
        """

        extension = source.extension

        if extension and extension in self.supported_extensions:
            return True

        media_type = source.media_type

        if media_type and media_type.lower() in self.supported_media_types:
            return True

        return False

    def support_score(self, source: ParseSource) -> int:
        """
        Return a parser-selection score for the source.

        A lower score is preferred.

        Exact extension matches are ranked above media-type matches.
        """

        extension = source.extension

        if extension and extension in self.supported_extensions:
            return self.priority

        media_type = source.media_type

        if media_type and media_type.lower() in self.supported_media_types:
            return self.priority + 10

        return 10_000_000

    def extract_source_metadata(
        self,
        source: ParseSource,
        context: ParserContext,
    ) -> dict[str, Any]:
        """Return common metadata derived from the parse source."""

        return {
            "source_identifier": source.identifier,
            "filename": source.filename,
            "extension": source.extension,
            "media_type": source.media_type,
            "dataset_id": source.dataset_id,
            "size_bytes": source.size_bytes,
            "source_metadata": dict(source.metadata),
            "pipeline_metadata": dict(context.metadata),
        }

    @abstractmethod
    def parse(
        self,
        source: ParseSource,
        context: ParserContext,
    ) -> OutputT:
        """Parse a source and return a canonical document."""

    def validate_document(
        self,
        document: OutputT,
        source: ParseSource,
        context: ParserContext,
    ) -> None:
        """
        Validate parser output.

        Concrete parsers can override this method for format-specific checks.
        """

        document_id = getattr(document, "id", None)

        if not isinstance(document_id, str) or not document_id.strip():
            raise ParserValidationError(
                "Parsed document must expose a non-empty string ID.",
                parser_name=self.name,
                source=source.identifier,
            )

        model_dump = getattr(document, "model_dump", None)

        if not callable(model_dump):
            raise ParserValidationError(
                "Parsed document must implement model_dump().",
                parser_name=self.name,
                source=source.identifier,
            )

    def execute(
        self,
        source: ParseSource,
        context: ParserContext | None = None,
    ) -> ParserResult[OutputT]:
        """
        Validate the source, invoke the parser, and validate its output.

        Unexpected parser exceptions are wrapped in ParserExecutionError while
        framework ParsingError subclasses propagate unchanged.
        """

        from .exceptions import ParsingError

        runtime_context = context or ParserContext()
        started_at = utc_now()

        source.validate()

        try:
            checksum = source.checksum()
            document = self.parse(source, runtime_context)

            if runtime_context.validate_output:
                self.validate_document(
                    document,
                    source,
                    runtime_context,
                )

        except ParsingError:
            raise
        except Exception as exc:
            raise ParserExecutionError(
                f"Parser execution failed: {exc}",
                parser_name=self.name,
                source=source.identifier,
                details={
                    "exception_type": type(exc).__name__,
                },
            ) from exc

        return ParserResult(
            document=document,
            parser_name=self.name,
            source_identifier=source.identifier,
            checksum=checksum,
            started_at=started_at,
            completed_at=utc_now(),
        )


InputT = TypeVar("InputT")
StageOutputT = TypeVar("StageOutputT")


class PipelineStage(ABC, Generic[InputT, StageOutputT]):
    """
    Abstract processing stage executed after parsing.

    Future stages can perform:

    - metadata enrichment;
    - validation;
    - chunking;
    - persistence;
    - indexing;
    - graph preparation.
    """

    name: str
    order: int = 100
    enabled: bool = True

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if inspect.isabstract(cls):
            return

        stage_name = getattr(cls, "name", None)

        if not isinstance(stage_name, str) or not stage_name.strip():
            raise TypeError(
                f"{cls.__name__} must define a non-empty stage 'name'."
            )

    @abstractmethod
    def process(
        self,
        value: InputT,
        *,
        source: ParseSource,
        context: ParserContext,
    ) -> StageOutputT:
        """Process and return the stage output."""