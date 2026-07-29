from __future__ import annotations

from pathlib import Path

from app.data_platform.connectors.local_filesystem import LocalFilesystemConnector


def test_local_filesystem_connector_roundtrip(tmp_path: Path) -> None:
    connector = LocalFilesystemConnector(root=tmp_path)

    connector.write_bytes("raw/volve/production/test.txt", b"hello waterdip")

    assert connector.exists("raw/volve/production/test.txt")

    data = connector.read_bytes("raw/volve/production/test.txt")
    assert data == b"hello waterdip"

    files = connector.list_files("raw/volve")

    assert len(files) == 1 #how so?
    assert files[0].name == "test.txt"
    assert files[0].source == "local"


def test_local_filesystem_connector_copy(tmp_path: Path) -> None:
    connector = LocalFilesystemConnector(root=tmp_path)

    connector.write_bytes("raw/source.txt", b"copy me")
    connector.copy("raw/source.txt", "processed/copied.txt")

    assert connector.exists("processed/copied.txt")
    assert connector.read_bytes("processed/copied.txt") == b"copy me"