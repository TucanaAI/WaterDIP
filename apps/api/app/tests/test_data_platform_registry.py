from __future__ import annotations

from pathlib import Path

from app.data_platform.registry.dataset_registry import load_dataset_registry


def test_load_dataset_registry() -> None:
    registry = load_dataset_registry(Path("data/registry/datasets.yaml"))

    assert "opm_spe1" in registry.datasets
    assert registry.datasets["opm_spe1"].source == "OPM Project"