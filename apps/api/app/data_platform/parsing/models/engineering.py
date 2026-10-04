"""
Reservoir and petroleum engineering metadata models for WaterDIP.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import Field, field_validator, model_validator

from .common import (
    EngineeringEntityType,
    ExtractionMethod,
    WaterDIPModel,
)


class Measurement(WaterDIPModel):
    """
    Generic engineering measurement.

    Examples
    --------
    pressure:
        value=3500
        unit="psi"

    porosity:
        value=0.22
        unit="fraction"
    """

    value: float

    unit: str | None = None

    normalized_value: float | None = None
    normalized_unit: str | None = None

    qualifier: str | None = None

    extraction_method: ExtractionMethod = ExtractionMethod.UNKNOWN

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class EngineeringEntity(WaterDIPModel):
    """
    Named engineering entity extracted from a source.
    """

    entity_type: EngineeringEntityType

    name: str

    normalized_name: str | None = None

    identifier: str | None = None

    aliases: list[str] = Field(
        default_factory=list,
    )

    extraction_method: ExtractionMethod = ExtractionMethod.UNKNOWN

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    attributes: dict[str, Any] = Field(
        default_factory=dict,
    )


class WellContext(WaterDIPModel):
    """Well and wellbore context associated with a document."""

    well_name: str | None = None
    well_id: str | None = None

    wellbore_name: str | None = None
    wellbore_id: str | None = None

    completion_name: str | None = None

    api_number: str | None = None
    uwi: str | None = None

    status: str | None = None
    well_type: str | None = None

    surface_latitude: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
    )

    surface_longitude: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
    )

    spud_date: date | None = None
    completion_date: date | None = None

    kb_elevation: Measurement | None = None
    water_depth: Measurement | None = None

    total_depth: Measurement | None = None
    measured_depth: Measurement | None = None
    true_vertical_depth: Measurement | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class ReservoirContext(WaterDIPModel):
    """Reservoir and formation context associated with a document."""

    field_name: str | None = None
    field_id: str | None = None

    reservoir_name: str | None = None
    reservoir_id: str | None = None

    formation_name: str | None = None
    formation_id: str | None = None

    zone_name: str | None = None

    basin_name: str | None = None

    block: str | None = None
    license: str | None = None

    country: str | None = None
    operator: str | None = None

    depth_top: Measurement | None = None
    depth_base: Measurement | None = None

    porosity: Measurement | None = None
    permeability: Measurement | None = None

    net_to_gross: Measurement | None = None

    oil_saturation: Measurement | None = None
    water_saturation: Measurement | None = None
    gas_saturation: Measurement | None = None

    reservoir_pressure: Measurement | None = None
    reservoir_temperature: Measurement | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class ProductionContext(WaterDIPModel):
    """
    Production/injection engineering values associated with a document.

    These values represent document-level context. Detailed time-series data
    will remain in tables or dedicated engineering data structures rather than
    being flattened into this model.
    """

    timestamp: datetime | None = None

    oil_rate: Measurement | None = None
    gas_rate: Measurement | None = None
    water_rate: Measurement | None = None

    liquid_rate: Measurement | None = None

    injection_rate: Measurement | None = None
    water_injection_rate: Measurement | None = None
    gas_injection_rate: Measurement | None = None

    water_cut: Measurement | None = None
    gas_oil_ratio: Measurement | None = None

    tubing_head_pressure: Measurement | None = None
    bottom_hole_pressure: Measurement | None = None

    cumulative_oil: Measurement | None = None
    cumulative_gas: Measurement | None = None
    cumulative_water: Measurement | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class EngineeringMetadata(WaterDIPModel):
    """
    Canonical petroleum engineering context for a parsed document.

    This model is intentionally extensible. It contains common engineering
    properties while allowing format-specific information to remain in the
    attributes dictionary.
    """

    well: WellContext | None = None
    reservoir: ReservoirContext | None = None
    production: ProductionContext | None = None

    entities: list[EngineeringEntity] = Field(
        default_factory=list,
    )

    measurements: dict[str, Measurement] = Field(
        default_factory=dict,
    )

    keywords: list[str] = Field(
        default_factory=list,
    )

    attributes: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("keywords")
    @classmethod
    def clean_keywords(
        cls,
        values: list[str],
    ) -> list[str]:
        """Remove empty and duplicate engineering keywords."""

        output: list[str] = []
        seen: set[str] = set()

        for value in values:
            cleaned = value.strip()

            if not cleaned:
                continue

            key = cleaned.casefold()

            if key in seen:
                continue

            seen.add(key)
            output.append(cleaned)

        return output

    @model_validator(mode="after")
    def validate_saturation_context(
        self,
    ) -> "EngineeringMetadata":
        """
        Perform deliberately conservative engineering validation.

        We do not reject saturation values merely because their sum differs
        from one: source documents may contain phase subsets, rounded values,
        historical measurements, or independently reported properties.
        """

        return self