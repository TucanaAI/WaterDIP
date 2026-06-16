from __future__ import annotations

from app.schemas import ProductionPoint


def water_cut(point: ProductionPoint) -> float:
    liquid = point.oil_rate + point.water_rate

    if liquid <= 0:
        return 0.0

    return point.water_rate / liquid


def water_cut_change(points: list[ProductionPoint]) -> float:
    if len(points) < 2:
        return 0.0

    first = water_cut(points[0])
    latest = water_cut(points[-1])

    return latest - first