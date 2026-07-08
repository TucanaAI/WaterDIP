from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class FileInventoryItem(BaseModel):
    path: str
    filename: str
    suffix: str
    size_bytes: int


def build_file_inventory(root: Path) -> list[FileInventoryItem]:
    if not root.exists():
        return []

    items: list[FileInventoryItem] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        items.append(
            FileInventoryItem(
                path=str(path),
                filename=path.name,
                suffix=path.suffix.lower(),
                size_bytes=path.stat().st_size,
            )
        )

    return items