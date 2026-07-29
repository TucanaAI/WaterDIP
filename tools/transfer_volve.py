from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = PROJECT_ROOT / "apps" / "api"

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))


from app.data_platform.connectors.databricks import (  # noqa: E402
    DatabricksConnector,
    DatabricksTransferRequest,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transfer a Volve dataset from Databricks to WaterDIP S3."
    )

    parser.add_argument(
        "dataset_id",
        help=(
            "Dataset identifier, for example: production, reports, "
            "technical, geophysics, eclipse, rms, drilling, "
            "well_logs, or well_logs_per_well."
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing S3 object.",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=3600.0,
        help="Maximum wait time in seconds.",
    )

    parser.add_argument(
    "--allow-large-transfer",
    action="store_true",
    help=(
        "Explicitly permit very large Volve archives, including "
        "the geoscience archive and large seismic datasets."
    ),)



    args = parser.parse_args()

    connector = DatabricksConnector()

    status = connector.transfer_and_wait(
        DatabricksTransferRequest(
            dataset_id=args.dataset_id,
            target_bucket="waterdip-data-lake",
            overwrite=args.overwrite,
            allow_large_transfer=args.allow_large_transfer,
        ),
        timeout_seconds=args.timeout,
    )

    print(
        f"Transfer completed successfully: "
        f"run_id={status.run_id}, "
        f"result={status.result_state}"
    )


if __name__ == "__main__":
    main()