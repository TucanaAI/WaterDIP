from __future__ import annotations

from app.data_platform.connectors.base import DatasetConnector, DatasetObject


class AzureBlobConnector(DatasetConnector):
    def list_files(self, prefix: str = "") -> list[DatasetObject]:
        raise NotImplementedError("Azure Blob connector planned.")

    def exists(self, path: str) -> bool:
        raise NotImplementedError("Azure Blob connector planned.")

    def read_bytes(self, path: str) -> bytes:
        raise NotImplementedError("Azure Blob connector planned.")

    def write_bytes(self, path: str, data: bytes) -> None:
        raise NotImplementedError("Azure Blob connector planned.")

    def copy(self, source: str, destination: str) -> None:
        raise NotImplementedError("Azure Blob connector planned.")