from __future__ import annotations

from app.schemas import ProductionPoint


def simple_oil_decline_fraction(points: list[ProductionPoint]) -> float:
    if len(points) < 2:
        return 0.0

    first = points[0].oil_rate
    latest = points[-1].oil_rate

    if first <= 0:
        return 0.0

    return (first - latest) / first