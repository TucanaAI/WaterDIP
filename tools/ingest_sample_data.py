from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = PROJECT_ROOT / "apps" / "api"

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))


from app.data_platform.pipelines.pipeline import run_download_pipeline_sync  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WaterDIP public dataset ingestion tool"
    )

    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Optional dataset id from data/registry/datasets.yaml",
    )

    parser.add_argument(
        "--registry",
        type=Path,
        default=PROJECT_ROOT / "data" / "registry" / "datasets.yaml",
        help="Path to dataset registry YAML file.",
    )

    parser.add_argument(
        "--raw-root",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw",
        help="Root directory for raw downloaded data.",
    )

    args = parser.parse_args()

    result = run_download_pipeline_sync(
        registry_path=args.registry,
        raw_data_root=args.raw_root,
        source=args.source,
    )

    print("\nDownload results")
    print("----------------")

    for item in result.downloads:
        status = "SKIPPED" if item.skipped else "DOWNLOADED"
        print(f"{status}: {item.dataset_id} - {item.message}")

        if item.path is not None:
            print(f"  -> {item.path}")

    print("\nInventory")
    print("---------")

    for item in result.inventory:
        print(f"{item.suffix or '[no suffix]'} | {item.size_bytes} bytes | {item.path}")


if __name__ == "__main__":
    main()