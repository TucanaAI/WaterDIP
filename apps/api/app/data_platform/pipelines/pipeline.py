from __future__ import annotations

import asyncio
from pathlib import Path

from app.data_platform.registry.dataset_registry import load_dataset_registry
from app.data_platform.connectors.http import DownloadResult, download_dataset
from app.data_platform.inventory.file_inventory import FileInventoryItem, build_file_inventory


class IngestionPipelineResult:
    def __init__(
        self,
        downloads: list[DownloadResult],
        inventory: list[FileInventoryItem],
    ) -> None:
        self.downloads = downloads
        self.inventory = inventory


async def run_download_pipeline(
    registry_path: Path,
    raw_data_root: Path,
    source: str | None = None,
) -> IngestionPipelineResult:
    registry = load_dataset_registry(registry_path)

    downloads: list[DownloadResult] = []

    for dataset_id, config in registry.datasets.items():
        if source is not None and dataset_id != source:
            continue

        result = await download_dataset(
            dataset_id=dataset_id,
            config=config,
            raw_data_root=raw_data_root,
        )
        downloads.append(result)

    inventory = build_file_inventory(raw_data_root)

    return IngestionPipelineResult(
        downloads=downloads,
        inventory=inventory,
    )


def run_download_pipeline_sync(
    registry_path: Path,
    raw_data_root: Path,
    source: str | None = None,
) -> IngestionPipelineResult:
    return asyncio.run(
        run_download_pipeline(
            registry_path=registry_path,
            raw_data_root=raw_data_root,
            source=source,
        )
    )