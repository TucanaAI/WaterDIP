from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = PROJECT_ROOT / "apps" / "api"

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))


from app.data_platform.connectors.databricks import (  # noqa: E402
    DatabricksConnector,
)


DEFAULT_POLL_SECONDS = 30.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Watch an existing Databricks transfer run.",
    )

    parser.add_argument(
        "run_id",
        type=int,
        help="Existing Databricks run ID.",
    )

    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=DEFAULT_POLL_SECONDS,
        help="Seconds between status checks.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.run_id <= 0:
        raise ValueError("run_id must be a positive integer")

    if args.poll_seconds <= 0:
        raise ValueError("poll-seconds must be greater than zero")

    connector = DatabricksConnector()

    print(f"Watching Databricks run {args.run_id}")
    print("Press Ctrl+C to stop watching. The Databricks job will continue.\n")

    previous_state: tuple[str, str | None] | None = None

    while True:
        try:
            status = connector.get_transfer_status(args.run_id)

            current_state = (
                status.lifecycle_state,
                status.result_state,
            )

            if current_state != previous_state:
                print(
                    f"Run {status.run_id}: "
                    f"lifecycle={status.lifecycle_state}, "
                    f"result={status.result_state}, "
                    f"message={status.state_message!r}"
                )
                previous_state = current_state

            if status.completed:
                if status.successful:
                    print("\nTransfer completed successfully.")
                    return 0

                print(
                    "\nTransfer did not complete successfully: "
                    f"{status.state_message or status.result_state}"
                )
                return 2

            time.sleep(args.poll_seconds)

        except KeyboardInterrupt:
            print(
                "\nStopped watching. "
                "The Databricks run was not cancelled."
            )
            return 0

        except Exception as exc:
            print(
                f"Unable to retrieve run status: "
                f"{type(exc).__name__}: {exc}"
            )
            print(
                f"Retrying in {args.poll_seconds:g} seconds..."
            )
            time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())