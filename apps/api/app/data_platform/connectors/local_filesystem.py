from __future__ import annotations

import shutil
from pathlib import Path

from app.data_platform.connectors.base import DatasetConnector, DatasetObject


class LocalFilesystemConnector(DatasetConnector):
    def __init__(self, root: Path) -> None:
        self.root = root

    def _resolve(self, path: str) -> Path:
        return self.root / path

    def list_files(self, prefix: str = "") -> list[DatasetObject]:
        base = self._resolve(prefix)
        if not base.exists():
            return []

        objects: list[DatasetObject] = []

        for path in base.rglob("*"):
            if not path.is_file():
                continue

            relative_path = path.relative_to(self.root).as_posix()

            objects.append(
                DatasetObject(
                    path=relative_path,
                    name=path.name,
                    size_bytes=path.stat().st_size,
                    source="local",
                )
            )

        return objects

    def exists(self, path: str) -> bool:
        return self._resolve(path).exists()

    def read_bytes(self, path: str) -> bytes:
        return self._resolve(path).read_bytes()

    def write_bytes(self, path: str, data: bytes) -> None:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def copy(self, source: str, destination: str) -> None:
        source_path = self._resolve(source)
        destination_path = self._resolve(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination_path)