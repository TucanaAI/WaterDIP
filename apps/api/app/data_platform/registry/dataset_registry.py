from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class DatasetConfig(BaseModel):
    name: str
    source: str
    category: str
    license: str
    url: str
    output_subdir: str
    filename: str | None = None
    file_types: list[str] = Field(default_factory=list)
    enabled: bool = True


class DatasetRegistry(BaseModel):
    datasets: dict[str, DatasetConfig]


def load_dataset_registry(path: Path) -> DatasetRegistry:
    if not path.exists():
        raise FileNotFoundError(f"Dataset registry not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f)

    return DatasetRegistry.model_validate(raw)


def get_enabled_datasets(registry: DatasetRegistry) -> dict[str, DatasetConfig]:
    return {
        dataset_id: config
        for dataset_id, config in registry.datasets.items()
        if config.enabled
    }