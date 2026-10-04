"""
Numerical well-log statistics for WaterDIP.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .models import CurveStatistics


def calculate_curve_statistics(
    values: Any,
) -> CurveStatistics:
    """
    Calculate finite-value statistics for a well-log curve.

    NaN and infinite values are treated as unavailable observations.
    """

    array = np.asarray(
        values,
        dtype=float,
    ).reshape(-1)

    total_count = int(array.size)

    finite_mask = np.isfinite(array)
    valid = array[finite_mask]

    valid_count = int(valid.size)
    null_count = total_count - valid_count

    if valid_count == 0:
        return CurveStatistics(
            count=0,
            null_count=null_count,
        )

    return CurveStatistics(
        count=valid_count,
        null_count=null_count,
        minimum=float(np.min(valid)),
        maximum=float(np.max(valid)),
        mean=float(np.mean(valid)),
        standard_deviation=float(np.std(valid)),
        p10=float(np.percentile(valid, 10)),
        p50=float(np.percentile(valid, 50)),
        p90=float(np.percentile(valid, 90)),
    )