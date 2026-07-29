from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetObject:
    path: str
    name: str
    size_bytes: int | None
    source: str


class DatasetConnector(ABC):
    @abstractmethod
    def list_files(self, prefix: str = "") -> list[DatasetObject]:
        raise NotImplementedError

    @abstractmethod
    def exists(self, path: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def read_bytes(self, path: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def write_bytes(self, path: str, data: bytes) -> None:
        raise NotImplementedError

    @abstractmethod
    def copy(self, source: str, destination: str) -> None:
        raise NotImplementedError