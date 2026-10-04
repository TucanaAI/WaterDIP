"""
Reusable WaterDIP well-log engineering intelligence.
"""

from .classifier import classify_curve
from .mnemonics import normalize_mnemonic
from .models import (
    CurveStatistics,
    DepthInterval,
    LogFamily,
    WellLogCurve,
    WellLogMetadata,
)
from .statistics import calculate_curve_statistics

__all__ = [
    "CurveStatistics",
    "DepthInterval",
    "LogFamily",
    "WellLogCurve",
    "WellLogMetadata",
    "calculate_curve_statistics",
    "classify_curve",
    "normalize_mnemonic",
]