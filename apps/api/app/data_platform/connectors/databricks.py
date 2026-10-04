from __future__ import annotations

import time
from dataclasses import dataclass

from databricks.sdk import WorkspaceClient

from app.config import settings
from app.data_platform.connectors.base import DatasetConnector, DatasetObject

@dataclass(frozen=True)
class DatabricksTransferRequest:
    dataset_id: str
    target_bucket: str = "waterdip-data-lake"
    overwrite: bool = False
    allow_large_transfer: bool = False


@dataclass(frozen=True)
class DatabricksTransferRun:
    run_id: int
    dataset_id: str


@dataclass(frozen=True)
class DatabricksTransferStatus:
    run_id: int
    lifecycle_state: str
    result_state: str | None
    state_message: str | None
    completed: bool
    successful: bool


class DatabricksConnector(DatasetConnector):
    """
    Orchestrates Volve Marketplace-to-S3 transfer jobs.

    The Databricks notebook performs data movement. The S3Connector is used
    afterward to list, verify, inventory, and process transferred objects.
    """

    def __init__(
        self,
        transfer_job_id: int | None = None,
        workspace_client: WorkspaceClient | None = None,
    ) -> None:
        resolved_job_id = (
            transfer_job_id
            if transfer_job_id is not None
            else settings.databricks_volve_transfer_job_id
        )

        if resolved_job_id is None or resolved_job_id <= 0:
            raise ValueError(
                "A valid Databricks transfer job ID is required. Set "
                "DATABRICKS_VOLVE_TRANSFER_JOB_ID or pass transfer_job_id."
            )

        self.transfer_job_id = resolved_job_id

        self.client = workspace_client or WorkspaceClient(
            host=settings.databricks_host,
            profile=settings.databricks_profile,
        )

    def trigger_transfer(
        self,
        request: DatabricksTransferRequest,
    ) -> DatabricksTransferRun:
        response = self.client.jobs.run_now(
            job_id=self.transfer_job_id,
            job_parameters={
                "dataset_id": request.dataset_id,
                "target_bucket": request.target_bucket,
                "overwrite": str(request.overwrite).lower(),
                "allow_large_transfer": str(
                    request.allow_large_transfer
                ).lower(),
            },
        )

        if response.run_id is None:
            raise RuntimeError("Databricks did not return a run ID.")

        return DatabricksTransferRun(
            run_id=int(response.run_id),
            dataset_id=request.dataset_id,
        )

    def get_transfer_status(
        self,
        run_id: int,
    ) -> DatabricksTransferStatus:
        run = self.client.jobs.get_run(run_id=run_id)

        lifecycle_state = (
            run.state.life_cycle_state.value
            if run.state is not None
            and run.state.life_cycle_state is not None
            else "UNKNOWN"
        )

        result_state = (
            run.state.result_state.value
            if run.state is not None
            and run.state.result_state is not None
            else None
        )

        state_message = (
            run.state.state_message
            if run.state is not None
            else None
        )

        completed = lifecycle_state in {
            "TERMINATED",
            "SKIPPED",
            "INTERNAL_ERROR",
        }

        successful = completed and result_state == "SUCCESS"

        return DatabricksTransferStatus(
            run_id=run_id,
            lifecycle_state=lifecycle_state,
            result_state=result_state,
            state_message=state_message,
            completed=completed,
            successful=successful,
        )

    def wait_for_transfer(
        self,
        run_id: int,
        timeout_seconds: float = 3600.0,
        poll_interval_seconds: float = 10.0,
    ) -> DatabricksTransferStatus:
        started_at = time.monotonic()

        while True:
            status = self.get_transfer_status(run_id)

            print(
                "Databricks run "
                f"{run_id}: lifecycle={status.lifecycle_state}, "
                f"result={status.result_state}"
            )

            if status.completed:
                if not status.successful:
                    raise RuntimeError(
                        f"Databricks transfer failed: "
                        f"{status.state_message or status.result_state}"
                    )

                return status

            if time.monotonic() - started_at >= timeout_seconds:
                raise TimeoutError(
                    f"Databricks run {run_id} exceeded "
                    f"{timeout_seconds} seconds."
                )

            time.sleep(poll_interval_seconds)

    def transfer_and_wait(
        self,
        request: DatabricksTransferRequest,
        timeout_seconds: float = 3600.0,
    ) -> DatabricksTransferStatus:
        run = self.trigger_transfer(request)

        return self.wait_for_transfer(
            run_id=run.run_id,
            timeout_seconds=timeout_seconds,
        )

    def list_files(self, prefix: str = "") -> list[DatasetObject]:
        raise NotImplementedError(
            "Use S3Connector.list_files() after transfer."
        )

    def exists(self, path: str) -> bool:
        raise NotImplementedError(
            "Use S3Connector.exists() after transfer."
        )

    def read_bytes(self, path: str) -> bytes:
        raise NotImplementedError(
            "Use S3Connector.read_bytes() after transfer."
        )

    def write_bytes(self, path: str, data: bytes) -> None:
        raise NotImplementedError(
            "DatabricksConnector orchestrates jobs and does not write bytes."
        )

    def copy(self, source: str, destination: str) -> None:
        raise NotImplementedError(
            "Use trigger_transfer() with a configured dataset ID."
        )