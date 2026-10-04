"""
LAS well-log parser for WaterDIP.
"""

from __future__ import annotations

from io import StringIO
from typing import Any

import lasio
import numpy as np

from ..base import BaseParser, ParseSource, ParserContext
from ..models import (
    DocumentType,
    EngineeringEntity,
    EngineeringEntityType,
    EngineeringMetadata,
    ExtractionMethod,
    Measurement,
    WaterDIPDocument,
    WellContext,
)
from ..well_logs import (
    DepthInterval,
    LogFamily,
    WellLogCurve,
    WellLogMetadata,
    calculate_curve_statistics,
    classify_curve,
    normalize_mnemonic,
)
from .common import (
    build_source_provenance,
    decode_text,
    filename_title,
)


def _header_value(
    las: lasio.LASFile,
    mnemonic: str,
) -> Any | None:
    """Safely retrieve a LAS well-header value."""

    try:
        item = las.well[mnemonic]
    except (KeyError, TypeError):
        return None

    value = getattr(
        item,
        "value",
        None,
    )

    if value in (None, ""):
        return None

    return value


def _header_unit(
    las: lasio.LASFile,
    mnemonic: str,
) -> str | None:
    """Safely retrieve the unit from a LAS well-header item."""

    try:
        item = las.well[mnemonic]
    except (KeyError, TypeError):
        return None

    unit = getattr(
        item,
        "unit",
        None,
    )

    if unit in (None, ""):
        return None

    return str(unit).strip() or None


def _float_or_none(
    value: Any,
) -> float | None:
    """Convert a LAS header value to float where possible."""

    if value in (None, ""):
        return None

    try:
        number = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return None

    if not np.isfinite(number):
        return None

    return number


def _string_or_none(
    value: Any,
) -> str | None:
    if value in (None, ""):
        return None

    output = str(value).strip()

    return output or None


def _parameter_values(
    las: lasio.LASFile,
) -> dict[str, Any]:
    """Extract serialisable LAS parameter-section values."""

    parameters: dict[str, Any] = {}

    for item in las.params:
        mnemonic = normalize_mnemonic(
            str(item.mnemonic)
        )

        parameters[mnemonic] = {
            "value": (
                item.value
                if isinstance(
                    item.value,
                    (str, int, float, bool, type(None)),
                )
                else str(item.value)
            ),
            "unit": _string_or_none(item.unit),
            "description": _string_or_none(item.descr),
        }

    return parameters


class LASParser(BaseParser[WaterDIPDocument]):
    """
    Parse LAS well logs into canonical WaterDIP engineering documents.
    """

    name = "las"
    parser_version = "1.0"

    supported_extensions = frozenset({".las"})

    supported_media_types = frozenset(
        {
            "application/x-las",
            "text/x-las",
            "text/plain",
        }
    )

    # More specific than TextParser for .las files.
    priority = 10

    def parse(
        self,
        source: ParseSource,
        context: ParserContext,
    ) -> WaterDIPDocument:
        content = source.read_bytes()

        raw_text, encoding = decode_text(content)

        las = lasio.read(
            StringIO(raw_text),
            ignore_header_errors=False,
        )

        checksum = source.checksum()

        well_name = (
            _string_or_none(
                _header_value(las, "WELL")
            )
            or filename_title(source.filename)
        )

        field_name = _string_or_none(
            _header_value(las, "FLD")
        )

        company = _string_or_none(
            _header_value(las, "COMP")
        )

        location = _string_or_none(
            _header_value(las, "LOC")
        )

        uwi = _string_or_none(
            _header_value(las, "UWI")
        )

        api = _string_or_none(
            _header_value(las, "API")
        )

        start = _float_or_none(
            _header_value(las, "STRT")
        )

        stop = _float_or_none(
            _header_value(las, "STOP")
        )

        step = _float_or_none(
            _header_value(las, "STEP")
        )

        null_value = _float_or_none(
            _header_value(las, "NULL")
        )

        depth_unit = (
            _header_unit(las, "STRT")
            or _header_unit(las, "STOP")
            or _header_unit(las, "STEP")
        )

        try:
            index_values = np.asarray(
                las.index,
                dtype=float,
            )
        except (
            TypeError,
            ValueError,
        ):
            index_values = np.asarray(
                [],
                dtype=float,
            )

        finite_index = index_values[
            np.isfinite(index_values)
        ]

        if finite_index.size:
            if start is None:
                start = float(finite_index[0])

            if stop is None:
                stop = float(finite_index[-1])

        increasing: bool | None = None

        if finite_index.size >= 2:
            differences = np.diff(finite_index)

            if np.all(differences >= 0):
                increasing = True
            elif np.all(differences <= 0):
                increasing = False

        curve_models: list[WellLogCurve] = []

        for curve_index, curve in enumerate(
            las.curves
        ):
            original_mnemonic = str(
                curve.mnemonic
            ).strip()

            mnemonic = normalize_mnemonic(
                original_mnemonic
            )

            family = classify_curve(
                mnemonic
            )

            try:
                values = np.asarray(
                    las[curve.mnemonic],
                    dtype=float,
                )
                statistics = calculate_curve_statistics(
                    values
                )
                sample_count = int(values.size)

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                statistics = None
                sample_count = 0

            curve_models.append(
                WellLogCurve(
                    mnemonic=mnemonic,
                    original_mnemonic=original_mnemonic,
                    unit=_string_or_none(
                        curve.unit
                    ),
                    description=_string_or_none(
                        curve.descr
                    ),
                    family=family,
                    is_index=(curve_index == 0),
                    sample_count=sample_count,
                    statistics=statistics,
                    metadata={
                        "curve_index": curve_index,
                    },
                )
            )

        version = None

        try:
            version = _string_or_none(
                las.version["VERS"].value
            )
        except (
            KeyError,
            TypeError,
        ):
            pass

        wrap: bool | None = None

        try:
            wrap_value = str(
                las.version["WRAP"].value
            ).strip().upper()

            if wrap_value == "YES":
                wrap = True
            elif wrap_value == "NO":
                wrap = False

        except (
            KeyError,
            TypeError,
        ):
            pass

        well_log_metadata = WellLogMetadata(
            las_version=version,
            wrap=wrap,
            null_value=null_value,
            depth=DepthInterval(
                start=start,
                stop=stop,
                step=step,
                unit=depth_unit,
                sample_count=int(
                    finite_index.size
                ),
                increasing=increasing,
            ),
            curves=curve_models,
            other_text=(
                _string_or_none(las.other)
                if hasattr(las, "other")
                else None
            ),
            parameters=_parameter_values(las),
            metadata={
                "encoding": encoding,
            },
        )

        well_context = WellContext(
            well_name=well_name,
            api_number=api,
            uwi=uwi,
            total_depth=(
                Measurement(
                    value=max(start, stop),
                    unit=depth_unit,
                    extraction_method=ExtractionMethod.SOURCE,
                    confidence=1.0,
                )
                if start is not None
                and stop is not None
                else None
            ),
            measured_depth=(
                Measurement(
                    value=max(start, stop),
                    unit=depth_unit,
                    extraction_method=ExtractionMethod.SOURCE,
                    confidence=1.0,
                )
                if start is not None
                and stop is not None
                else None
            ),
            metadata={
                "company": company,
                "location": location,
            },
        )

        entities: list[EngineeringEntity] = []

        if well_name:
            entities.append(
                EngineeringEntity(
                    entity_type=EngineeringEntityType.WELL,
                    name=well_name,
                    extraction_method=ExtractionMethod.SOURCE,
                    confidence=1.0,
                )
            )

        if field_name:
            entities.append(
                EngineeringEntity(
                    entity_type=EngineeringEntityType.FIELD,
                    name=field_name,
                    extraction_method=ExtractionMethod.SOURCE,
                    confidence=1.0,
                )
            )

        engineering = EngineeringMetadata(
            well=well_context,
            entities=entities,
            keywords=[
                "well log",
                "LAS",
                *[
                    curve.family.value
                    for curve in curve_models
                    if curve.family
                    not in {
                        LogFamily.UNKNOWN,
                        LogFamily.DEPTH,
                    }
                ],
            ],
            attributes={
                "field_name": field_name,
                "company": company,
            },
        )

        curve_lines = []

        for curve in curve_models:
            line = curve.mnemonic

            if curve.unit:
                line += f" [{curve.unit}]"

            line += f" - {curve.family.value}"

            if curve.description:
                line += f": {curve.description}"

            curve_lines.append(line)

        text_parts = [
            "Well Log",
            f"Well: {well_name or 'Unknown'}",
        ]

        if field_name:
            text_parts.append(
                f"Field: {field_name}"
            )

        if company:
            text_parts.append(
                f"Company: {company}"
            )

        if start is not None and stop is not None:
            depth_description = (
                f"Depth interval: {start} to {stop}"
            )

            if depth_unit:
                depth_description += (
                    f" {depth_unit}"
                )

            text_parts.append(
                depth_description
            )

        text_parts.extend(
            [
                f"LAS version: {version or 'Unknown'}",
                f"Curve count: {len(curve_models)}",
                "",
                "Curves:",
                *curve_lines,
            ]
        )

        provenance = build_source_provenance(
            source,
            context,
            parser_name=self.name,
            parser_version=self.parser_version,
            checksum=checksum,
            metadata={
                "encoding": encoding,
                "las_version": version,
                "curve_count": len(curve_models),
                "sample_count": int(
                    finite_index.size
                ),
            },
        )

        return WaterDIPDocument.create(
            source=provenance,
            title=(
                f"{well_name} Well Log"
                if well_name
                else filename_title(source.filename)
            ),
            text="\n".join(text_parts),
            document_type=DocumentType.WELL_LOG,
            engineering=engineering,
            metadata={
                "well_log": well_log_metadata.model_dump(
                    mode="json"
                ),
            },
        )