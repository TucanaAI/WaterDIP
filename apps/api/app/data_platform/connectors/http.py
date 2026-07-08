from __future__ import annotations

from pathlib import Path

import httpx

from app.data_platform.registry.dataset_registry import DatasetConfig


class DownloadResult:
    def __init__(
        self,
        dataset_id: str,
        path: Path | None,
        skipped: bool,
        message: str,
    ) -> None:
        self.dataset_id = dataset_id
        self.path = path
        self.skipped = skipped
        self.message = message


async def download_dataset(
    dataset_id: str,
    config: DatasetConfig,
    raw_data_root: Path,
    timeout_seconds: float = 60.0,
) -> DownloadResult:
    if not config.enabled:
        return DownloadResult(
            dataset_id=dataset_id,
            path=None,
            skipped=True,
            message="Dataset disabled in registry.",
        )

    if config.filename is None:
        return DownloadResult(
            dataset_id=dataset_id,
            path=None,
            skipped=True,
            message="No direct filename configured. Manual/download-gated dataset.",
        )

    output_dir = raw_data_root / config.output_subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / config.filename

    if output_path.exists() and output_path.stat().st_size > 0:
        return DownloadResult(
            dataset_id=dataset_id,
            path=output_path,
            skipped=True,
            message="File already exists.",
        )

    async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
        response = await client.get(config.url)
        response.raise_for_status()

    output_path.write_bytes(response.content)

    return DownloadResult(
        dataset_id=dataset_id,
        path=output_path,
        skipped=False,
        message="Downloaded successfully.",
    )