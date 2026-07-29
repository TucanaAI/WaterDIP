from __future__ import annotations

import httpx

from app.data_platform.connectors.base import DatasetConnector, DatasetObject


class HTTPConnector(DatasetConnector):
    def list_files(self, prefix: str = "") -> list[DatasetObject]:
        raise NotImplementedError("HTTP listing is source-specific.")

    def exists(self, path: str) -> bool:
        response = httpx.head(path, follow_redirects=True, timeout=30.0)
        return response.status_code < 400

    def read_bytes(self, path: str) -> bytes:
        response = httpx.get(path, follow_redirects=True, timeout=120.0)
        response.raise_for_status()
        return response.content

    def write_bytes(self, path: str, data: bytes) -> None:
        raise NotImplementedError("Generic HTTP connector is read-only.")

    def copy(self, source: str, destination: str) -> None:
        raise NotImplementedError("Generic HTTP connector cannot copy directly.")