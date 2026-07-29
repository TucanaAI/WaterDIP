from __future__ import annotations

from pathlib import PurePosixPath

import boto3
from botocore.client import BaseClient

from app.data_platform.connectors.base import DatasetConnector, DatasetObject


class S3Connector(DatasetConnector):
    def __init__(
        self,
        bucket: str = "waterdip-data-lake",
        client: BaseClient | None = None,
    ) -> None:
        self.bucket = bucket
        self.client = client or boto3.client("s3")

    def list_files(self, prefix: str = "") -> list[DatasetObject]:
        objects: list[DatasetObject] = []
        paginator = self.client.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for item in page.get("Contents", []):
                key = item["Key"]

                if key.endswith("/"):
                    continue

                objects.append(
                    DatasetObject(
                        path=key,
                        name=PurePosixPath(key).name,
                        size_bytes=int(item["Size"]),
                        source="s3",
                    )
                )

        return objects

    def exists(self, path: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=path)
            return True
        except Exception:
            return False

    def read_bytes(self, path: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=path)
        body = response["Body"]
        return bytes(body.read())

    def write_bytes(self, path: str, data: bytes) -> None:
        self.client.put_object(
            Bucket=self.bucket,
            Key=path,
            Body=data,
        )

    def copy(self, source: str, destination: str) -> None:
        self.client.copy_object(
            Bucket=self.bucket,
            CopySource={"Bucket": self.bucket, "Key": source},
            Key=destination,
        )