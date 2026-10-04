from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.data_platform.parsing import (
    BaseParser,
    ParseSource,
    ParserContext,
    ParserDispatcher,
    ParserRegistry,
    ParsingPipeline,
    PipelineStage,
)


@dataclass
class TestDocument:
    id: str
    text: str

    def model_dump(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
        }


class TextParser(BaseParser[TestDocument]):
    name = "text"
    supported_extensions = frozenset({".txt"})
    supported_media_types = frozenset({"text/plain"})
    priority = 10

    def parse(
        self,
        source: ParseSource,
        context: ParserContext,
    ) -> TestDocument:
        text = source.read_bytes().decode("utf-8")

        return TestDocument(
            id=source.checksum(),
            text=text,
        )


class UppercaseStage(
    PipelineStage[TestDocument, TestDocument]
):
    name = "uppercase"
    order = 10

    def process(
        self,
        value: TestDocument,
        *,
        source: ParseSource,
        context: ParserContext,
    ) -> TestDocument:
        return TestDocument(
            id=value.id,
            text=value.text.upper(),
        )


def test_registry_selects_text_parser() -> None:
    registry = ParserRegistry()
    registry.register(TextParser())

    source = ParseSource.from_bytes(
        b"WaterDIP",
        filename="report.txt",
    )

    parser = registry.select(source)

    assert parser.name == "text"


def test_dispatcher_executes_parser() -> None:
    registry = ParserRegistry()
    registry.register(TextParser())

    dispatcher = ParserDispatcher(registry)

    result = dispatcher.dispatch_bytes(
        b"Reservoir engineering",
        filename="notes.txt",
    )

    assert result.parser_name == "text"
    assert result.document.text == "Reservoir engineering"
    assert len(result.checksum) == 64


def test_pipeline_executes_stage() -> None:
    registry = ParserRegistry()
    registry.register(TextParser())

    pipeline = ParsingPipeline(
        registry=registry,
        stages=[UppercaseStage()],
    )

    result = pipeline.run_bytes(
        b"water management",
        filename="report.txt",
    )

    assert result.success is True
    assert result.output.text == "WATER MANAGEMENT"
    assert len(result.stages) == 1
    assert result.stages[0].stage_name == "uppercase"