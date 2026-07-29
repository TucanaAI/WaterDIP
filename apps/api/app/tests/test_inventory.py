from __future__ import annotations

from pathlib import Path

from app.data_platform.connectors.local_filesystem import LocalFilesystemConnector
from app.data_platform.inventory.file_inventory import build_file_inventory


def test_build_file_inventory_from_local_connector(tmp_path: Path) -> None:
    local_connector = LocalFilesystemConnector(root=tmp_path)

    local_connector.write_bytes("raw/volve/production/a.csv", b"well,date,oil")
    local_connector.write_bytes("raw/volve/reports/report.pdf", b"%PDF")

    inventory = build_file_inventory(
        connector=local_connector,
        prefix="raw/volve",
    )

    assert len(inventory) == 2

    filenames = {item.filename for item in inventory}

    assert "a.csv" in filenames
    assert "report.pdf" in filenames

    sources = {item.source for item in inventory}

    assert sources == {"local"}