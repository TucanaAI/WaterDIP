from __future__ import annotations


def recommend_for_water_breakthrough(severity: str) -> str:
    if severity == "high":
        return (
            "High water breakthrough risk. Recommend PLT or tracer test, "
            "review injector-producer connectivity, evaluate zonal shutoff, "
            "and check recent injection-rate changes."
        )

    if severity == "medium":
        return (
            "Moderate water breakthrough signal. Recommend surveillance review, "
            "offset-well comparison, pressure trend check, and water-cut monitoring."
        )

    if severity == "low":
        return (
            "Early water-cut increase detected. Continue monitoring and compare "
            "against expected simulation forecast."
        )

    if severity == "insufficient_data":
        return "Insufficient production data. Upload more production history."

    return "No strong water breakthrough signal detected."