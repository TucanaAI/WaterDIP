"""
Canonical well-log models for WaterDIP.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from ..models.common import WaterDIPModel


class LogFamily(str, Enum):
    """
    High-level petrophysical/logging families.

    Classification is intentionally conservative. UNKNOWN is preferable to
    incorrectly assigning engineering meaning to an unfamiliar mnemonic.
    """

    DEPTH = "depth"
    GAMMA_RAY = "gamma_ray"
    SPONTANEOUS_POTENTIAL = "spontaneous_potential"
    RESISTIVITY = "resistivity"
    DENSITY = "density"
    NEUTRON = "neutron"
    SONIC = "sonic"
    CALIPER = "caliper"
    PHOTOELECTRIC = "photoelectric"
    POROSITY = "porosity"
    SATURATION = "saturation"
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    PERMEABILITY = "permeability"
    FACIES = "facies"
    OTHER = "other"
    UNKNOWN = "unknown"


class CurveStatistics(WaterDIPModel):
    """Numerical statistics for a well-log curve."""

    count: int = Field(default=0, ge=0)
    null_count: int = Field(default=0, ge=0)

    minimum: float | None = None
    maximum: float | None = None
    mean: float | None = None
    standard_deviation: float | None = None

    p10: float | None = None
    p50: float | None = None
    p90: float | None = None


class WellLogCurve(WaterDIPModel):
    """Canonical metadata for one well-log curve."""

    mnemonic: str
    original_mnemonic: str | None = None

    unit: str | None = None
    description: str | None = None

    family: LogFamily = LogFamily.UNKNOWN

    is_index: bool = False

    sample_count: int = Field(default=0, ge=0)

    statistics: CurveStatistics | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class DepthInterval(WaterDIPModel):
    """Depth coverage of a log."""

    start: float | None = None
    stop: float | None = None
    step: float | None = None
    unit: str | None = None

    sample_count: int = Field(default=0, ge=0)

    increasing: bool | None = None


class WellLogMetadata(WaterDIPModel):
    """
    Canonical well-log metadata extracted from LAS or future log formats.
    """

    las_version: str | None = None
    wrap: bool | None = None

    null_value: float | None = None

    depth: DepthInterval = Field(
        default_factory=DepthInterval,
    )

    curves: list[WellLogCurve] = Field(
        default_factory=list,
    )

    other_text: str | None = None

    parameters: dict[str, Any] = Field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )