from __future__ import annotations

from pydantic import BaseModel

from app.data_platform.connectors.base import DatasetConnector


class FileInventoryItem(BaseModel):
    path: str
    filename: str
    suffix: str
    size_bytes: int | None
    source: str


def build_file_inventory(
    connector: DatasetConnector,
    prefix: str = "",
) -> list[FileInventoryItem]:
    objects = connector.list_files(prefix)

    return [
        FileInventoryItem(
            path=obj.path,
            filename=obj.name,
            suffix="." + obj.name.split(".")[-1].lower() if "." in obj.name else "",
            size_bytes=obj.size_bytes,
            source=obj.source,
        )
        for obj in objects
    ]