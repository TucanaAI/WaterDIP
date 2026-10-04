"""
Pipeline orchestration for the WaterDIP engineering parser framework.

The pipeline:

1. selects and executes a parser;
2. runs zero or more ordered post-processing stages;
3. records stage timings and diagnostics;
4. supports strict and non-strict stage failure behaviour.

Future stages will include metadata enrichment, chunking, persistence,
vector indexing, and graph preparation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any, Generic, TypeVar
from uuid import uuid4

from .base import (
    ParseSource,
    ParserContext,
    ParserOutput,
    ParserResult,
    PipelineStage,
    utc_now,
)
from .dispatcher import ParserDispatcher
from .exceptions import (
    ParsingError,
    PipelineConfigurationError,
    PipelineExecutionError,
    PipelineStageError,
)
from .registry import ParserRegistry


FinalOutputT = TypeVar("FinalOutputT")


@dataclass(slots=True)
class StageExecution:
    """Execution record for a pipeline stage."""

    stage_name: str
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    success: bool
    input_type: str
    output_type: str | None = None
    error: str | None = None


@dataclass(slots=True)
class PipelineResult(Generic[FinalOutputT]):
    """
    Final pipeline execution result.

    ``parser_result`` preserves parser-level diagnostics while ``output`` is
    the final value returned after all enabled stages have executed.
    """

    run_id: str
    source_identifier: str
    parser_result: ParserResult[ParserOutput]
    output: FinalOutputT
    stages: list[StageExecution]
    started_at: datetime
    completed_at: datetime
    warnings: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Return whether every recorded stage succeeded."""

        return all(stage.success for stage in self.stages)

    @property
    def duration_seconds(self) -> float:
        """Return total pipeline duration."""

        return max(
            0.0,
            (self.completed_at - self.started_at).total_seconds(),
        )


class ParsingPipeline:
    """
    Orchestrate parsing and post-processing stages.

    Parameters
    ----------
    registry:
        Parser registry used by the dispatcher.
    dispatcher:
        Optional custom dispatcher. Do not provide both dispatcher and
        registry.
    stages:
        Optional processing stages.
    continue_on_stage_error:
        Continue to later stages when a non-strict context encounters a stage
        failure.
    """

    def __init__(
        self,
        *,
        registry: ParserRegistry | None = None,
        dispatcher: ParserDispatcher | None = None,
        stages: list[PipelineStage[Any, Any]] | None = None,
        continue_on_stage_error: bool = False,
    ) -> None:
        if registry is not None and dispatcher is not None:
            raise PipelineConfigurationError(
                "Provide either a parser registry or dispatcher, not both."
            )

        self.dispatcher = dispatcher or ParserDispatcher(
            registry=registry,
        )
        self.continue_on_stage_error = continue_on_stage_error
        self._stages: list[PipelineStage[Any, Any]] = []

        for stage in stages or []:
            self.add_stage(stage)

    @property
    def stages(self) -> tuple[PipelineStage[Any, Any], ...]:
        """Return ordered processing stages."""

        return tuple(self._stages)

    def add_stage(
        self,
        stage: PipelineStage[Any, Any],
        *,
        replace: bool = False,
    ) -> None:
        """Add a processing stage and maintain deterministic ordering."""

        if not isinstance(stage, PipelineStage):
            raise PipelineConfigurationError(
                "Pipeline stages must inherit from PipelineStage.",
                details={
                    "received_type": type(stage).__name__,
                },
            )

        existing_index = next(
            (
                index
                for index, current_stage in enumerate(self._stages)
                if current_stage.name.lower() == stage.name.lower()
            ),
            None,
        )

        if existing_index is not None:
            if not replace:
                raise PipelineConfigurationError(
                    f"Pipeline stage '{stage.name}' is already configured.",
                    details={
                        "stage_name": stage.name,
                    },
                )

            self._stages.pop(existing_index)

        self._stages.append(stage)
        self._stages.sort(
            key=lambda current_stage: (
                current_stage.order,
                current_stage.name.lower(),
            )
        )

    def remove_stage(self, name: str) -> PipelineStage[Any, Any]:
        """Remove a configured stage by name."""

        normalised_name = name.strip().lower()

        for index, stage in enumerate(self._stages):
            if stage.name.lower() == normalised_name:
                return self._stages.pop(index)

        raise PipelineConfigurationError(
            f"Pipeline stage '{name}' is not configured.",
            details={
                "stage_name": name,
            },
        )

    def clear_stages(self) -> None:
        """Remove all configured processing stages."""

        self._stages.clear()

    def run(
        self,
        source: ParseSource,
        *,
        parser_name: str | None = None,
        context: ParserContext | None = None,
    ) -> PipelineResult[Any]:
        """
        Parse a source and execute configured processing stages.

        Strict context behaviour:

        - parser failures always terminate execution;
        - stage failures terminate execution when ``context.strict`` is true;
        - when non-strict, failures are recorded and may be skipped.
        """

        runtime_context = context or ParserContext()

        if not runtime_context.run_id:
            runtime_context.run_id = str(uuid4())

        started_at = utc_now()

        try:
            parser_result = self.dispatcher.dispatch(
                source,
                parser_name=parser_name,
                context=runtime_context,
            )
        except ParsingError:
            raise
        except Exception as exc:
            raise PipelineExecutionError(
                f"Parser dispatch failed: {exc}",
                source=source.identifier,
                details={
                    "exception_type": type(exc).__name__,
                },
            ) from exc

        current_value: Any = parser_result.document
        stage_executions: list[StageExecution] = []
        warnings = list(parser_result.warnings)

        for stage in self._stages:
            if not stage.enabled:
                continue

            stage_started_at = utc_now()
            timer_started_at = perf_counter()
            input_type = type(current_value).__name__

            try:
                stage_output = stage.process(
                    current_value,
                    source=source,
                    context=runtime_context,
                )

                elapsed = perf_counter() - timer_started_at
                stage_completed_at = utc_now()

                stage_executions.append(
                    StageExecution(
                        stage_name=stage.name,
                        started_at=stage_started_at,
                        completed_at=stage_completed_at,
                        duration_seconds=elapsed,
                        success=True,
                        input_type=input_type,
                        output_type=type(stage_output).__name__,
                    )
                )

                current_value = stage_output

            except Exception as exc:
                elapsed = perf_counter() - timer_started_at
                stage_completed_at = utc_now()

                stage_executions.append(
                    StageExecution(
                        stage_name=stage.name,
                        started_at=stage_started_at,
                        completed_at=stage_completed_at,
                        duration_seconds=elapsed,
                        success=False,
                        input_type=input_type,
                        error=str(exc),
                    )
                )

                stage_error = PipelineStageError(
                    f"Pipeline stage failed: {exc}",
                    stage_name=stage.name,
                    parser_name=parser_result.parser_name,
                    source=source.identifier,
                    details={
                        "exception_type": type(exc).__name__,
                    },
                )

                if runtime_context.strict:
                    raise stage_error from exc

                warnings.append(str(stage_error))

                if not self.continue_on_stage_error:
                    break

        return PipelineResult(
            run_id=runtime_context.run_id,
            source_identifier=source.identifier,
            parser_result=parser_result,
            output=current_value,
            stages=stage_executions,
            started_at=started_at,
            completed_at=utc_now(),
            warnings=warnings,
        )

    def run_path(
        self,
        path: str | Path,
        *,
        parser_name: str | None = None,
        dataset_id: str | None = None,
        uri: str | None = None,
        media_type: str | None = None,
        source_metadata: dict[str, Any] | None = None,
        context: ParserContext | None = None,
    ) -> PipelineResult[Any]:
        """Run the parsing pipeline for a local file."""

        source = ParseSource.from_path(
            path,
            dataset_id=dataset_id,
            uri=uri,
            media_type=media_type,
            metadata=source_metadata,
        )

        return self.run(
            source,
            parser_name=parser_name,
            context=context,
        )

    def run_bytes(
        self,
        content: bytes,
        *,
        filename: str,
        parser_name: str | None = None,
        dataset_id: str | None = None,
        uri: str | None = None,
        media_type: str | None = None,
        source_metadata: dict[str, Any] | None = None,
        context: ParserContext | None = None,
    ) -> PipelineResult[Any]:
        """Run the parsing pipeline for in-memory byte content."""

        source = ParseSource.from_bytes(
            content,
            filename=filename,
            dataset_id=dataset_id,
            uri=uri,
            media_type=media_type,
            metadata=source_metadata,
        )

        return self.run(
            source,
            parser_name=parser_name,
            context=context,
        )