"""
Parser registry for the WaterDIP engineering parser framework.

The registry owns parser discovery and selection. Concrete parsers register
once and are selected dynamically by extension, media type, and priority.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from threading import RLock
from typing import Any

from .base import BaseParser, ParseSource
from .exceptions import (
    AmbiguousParserError,
    DuplicateParserError,
    ParserNotFoundError,
    ParserRegistrationError,
    UnsupportedFileTypeError,
)


class ParserRegistry:
    """
    Thread-safe registry for parser instances.

    Parser names are unique and case-insensitive.
    """

    def __init__(self) -> None:
        self._parsers: dict[str, BaseParser[Any]] = {}
        self._lock = RLock()

    @staticmethod
    def _normalise_name(name: str) -> str:
        value = name.strip().lower()

        if not value:
            raise ParserRegistrationError(
                "Parser name cannot be empty."
            )

        return value

    def register(
        self,
        parser: BaseParser[Any],
        *,
        replace: bool = False,
    ) -> BaseParser[Any]:
        """
        Register a parser instance.

        Parameters
        ----------
        parser:
            Parser instance to register.
        replace:
            Replace an existing parser with the same name.
        """

        if not isinstance(parser, BaseParser):
            raise ParserRegistrationError(
                "Registered parser must inherit from BaseParser.",
                details={
                    "received_type": type(parser).__name__,
                },
            )

        key = self._normalise_name(parser.name)

        with self._lock:
            if key in self._parsers and not replace:
                raise DuplicateParserError(
                    f"A parser named '{parser.name}' is already registered.",
                    parser_name=parser.name,
                )

            self._parsers[key] = parser

        return parser

    def register_class(
        self,
        parser_class: type[BaseParser[Any]],
        *,
        replace: bool = False,
        **constructor_kwargs: Any,
    ) -> BaseParser[Any]:
        """Instantiate and register a parser class."""

        if not issubclass(parser_class, BaseParser):
            raise ParserRegistrationError(
                "Parser class must inherit from BaseParser.",
                details={
                    "received_type": parser_class.__name__,
                },
            )

        parser = parser_class(**constructor_kwargs)

        return self.register(parser, replace=replace)

    def unregister(self, name: str) -> BaseParser[Any]:
        """Remove and return a registered parser."""

        key = self._normalise_name(name)

        with self._lock:
            try:
                return self._parsers.pop(key)
            except KeyError as exc:
                raise ParserNotFoundError(
                    f"No parser named '{name}' is registered.",
                    parser_name=name,
                ) from exc

    def get(self, name: str) -> BaseParser[Any]:
        """Return a parser by name."""

        key = self._normalise_name(name)

        with self._lock:
            try:
                return self._parsers[key]
            except KeyError as exc:
                raise ParserNotFoundError(
                    f"No parser named '{name}' is registered.",
                    parser_name=name,
                ) from exc

    def contains(self, name: str) -> bool:
        """Return whether a parser name is registered."""

        try:
            key = self._normalise_name(name)
        except ParserRegistrationError:
            return False

        with self._lock:
            return key in self._parsers

    def all(self) -> tuple[BaseParser[Any], ...]:
        """Return all registered parsers ordered by priority and name."""

        with self._lock:
            parsers = tuple(self._parsers.values())

        return tuple(
            sorted(
                parsers,
                key=lambda parser: (
                    parser.priority,
                    parser.name.lower(),
                ),
            )
        )

    def names(self) -> tuple[str, ...]:
        """Return registered parser names."""

        return tuple(parser.name for parser in self.all())

    def clear(self) -> None:
        """Remove all parsers."""

        with self._lock:
            self._parsers.clear()

    def extend(
        self,
        parsers: Iterable[BaseParser[Any]],
        *,
        replace: bool = False,
    ) -> None:
        """Register multiple parser instances."""

        for parser in parsers:
            self.register(parser, replace=replace)

    def candidates(
        self,
        source: ParseSource,
    ) -> tuple[BaseParser[Any], ...]:
        """Return parsers supporting the supplied source."""

        supported = [
            parser
            for parser in self.all()
            if parser.supports(source)
        ]

        return tuple(
            sorted(
                supported,
                key=lambda parser: (
                    parser.support_score(source),
                    parser.priority,
                    parser.name.lower(),
                ),
            )
        )

    def select(
        self,
        source: ParseSource,
        *,
        parser_name: str | None = None,
        reject_ambiguous: bool = False,
    ) -> BaseParser[Any]:
        """
        Select the best parser for a source.

        An explicit parser name bypasses automatic detection but still verifies
        that the parser supports the source.

        When ``reject_ambiguous`` is enabled, equally ranked parsers produce an
        AmbiguousParserError rather than silently selecting by name.
        """

        if parser_name:
            parser = self.get(parser_name)

            if not parser.supports(source):
                raise UnsupportedFileTypeError(
                    (
                        f"Parser '{parser.name}' does not support source "
                        f"'{source.identifier}'."
                    ),
                    parser_name=parser.name,
                    source=source.identifier,
                    details={
                        "extension": source.extension,
                        "media_type": source.media_type,
                    },
                )

            return parser

        candidates = self.candidates(source)

        if not candidates:
            raise UnsupportedFileTypeError(
                (
                    "No registered parser supports the supplied source. "
                    f"Extension={source.extension!r}, "
                    f"media_type={source.media_type!r}."
                ),
                source=source.identifier,
                details={
                    "extension": source.extension,
                    "media_type": source.media_type,
                    "registered_parsers": list(self.names()),
                },
            )

        selected = candidates[0]

        if reject_ambiguous and len(candidates) > 1:
            first_score = selected.support_score(source)
            equally_ranked = [
                parser
                for parser in candidates
                if parser.support_score(source) == first_score
            ]

            if len(equally_ranked) > 1:
                raise AmbiguousParserError(
                    "Multiple equally ranked parsers support the source.",
                    source=source.identifier,
                    details={
                        "parsers": [
                            parser.name
                            for parser in equally_ranked
                        ],
                        "score": first_score,
                    },
                )

        return selected

    def describe(self) -> list[dict[str, Any]]:
        """Return serialisable parser registry information."""

        return [
            {
                "name": parser.name,
                "priority": parser.priority,
                "extensions": sorted(parser.supported_extensions),
                "media_types": sorted(parser.supported_media_types),
                "class": (
                    f"{parser.__class__.__module__}."
                    f"{parser.__class__.__qualname__}"
                ),
            }
            for parser in self.all()
        ]

    def __len__(self) -> int:
        with self._lock:
            return len(self._parsers)

    def __iter__(self) -> Iterator[BaseParser[Any]]:
        return iter(self.all())

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and self.contains(name)


default_parser_registry = ParserRegistry()


def register_parser(
    parser: BaseParser[Any],
    *,
    replace: bool = False,
) -> BaseParser[Any]:
    """Register a parser in the global default registry."""

    return default_parser_registry.register(
        parser,
        replace=replace,
    )


def parser_plugin(
    *,
    replace: bool = False,
    registry: ParserRegistry | None = None,
):
    """
    Class decorator that instantiates and registers a parser.

    Example
    -------
    ``@parser_plugin()``
    ``class TextParser(BaseParser[Document]): ...``
    """

    target_registry = registry or default_parser_registry

    def decorator(
        parser_class: type[BaseParser[Any]],
    ) -> type[BaseParser[Any]]:
        target_registry.register_class(
            parser_class,
            replace=replace,
        )
        return parser_class

    return decorator