from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_waterdip_diagnose_high_breakthrough() -> None:
    response = client.post(
        "/waterdip/diagnose",
        json={
            "well_id": "WELL-A",
            "production": [
                {
                    "date": "2025-01-01",
                    "oil_rate": 1000,
                    "water_rate": 100,
                    "gas_rate": 0,
                },
                {
                    "date": "2025-02-01",
                    "oil_rate": 300,
                    "water_rate": 900,
                    "gas_rate": 0,
                },
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["well_id"] == "WELL-A"
    assert data["severity"] == "high"
    assert data["water_cut_latest"] > 0.7