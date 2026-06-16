from __future__ import annotations

from app.reservoir.water_cut import water_cut, water_cut_change
from app.schemas import ProductionPoint


def classify_water_breakthrough(points: list[ProductionPoint]) -> tuple[str, float, float]:
    if not points:
        return "insufficient_data", 0.0, 0.0

    latest = water_cut(points[-1])
    change = water_cut_change(points)

    if latest >= 0.7 and change >= 0.25:
        return "high", latest, change

    if latest >= 0.4 and change >= 0.15:
        return "medium", latest, change

    if latest >= 0.2 and change >= 0.05:
        return "low", latest, change

    return "normal", latest, change