"""
Safe ZIP archive inventory parser for WaterDIP.
"""

from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import PurePosixPath
from zipfile import BadZipFile, ZipFile, ZipInfo

from ..base import BaseParser, ParseSource, ParserContext
from ..exceptions import ParserExecutionError
from ..models import (
    DocumentAttachment,
    DocumentType,
    WaterDIPDocument,
)
from .common import (
    build_source_provenance,
    deterministic_id,
    filename_title,
)


DEFAULT_MAX_MEMBERS = 10_000
DEFAULT_MAX_UNCOMPRESSED_BYTES = 10 * 1024 * 1024 * 1024
DEFAULT_MAX_COMPRESSION_RATIO = 1_000.0


def is_unsafe_archive_path(
    filename: str,
) -> bool:
    """Detect absolute paths and parent traversal in ZIP members."""

    path = PurePosixPath(
        filename.replace("\\", "/")
    )

    if path.is_absolute():
        return True

    return ".." in path.parts


def compression_ratio(
    member: ZipInfo,
) -> float:
    """Return the member's uncompressed/compressed size ratio."""

    if member.file_size == 0:
        return 0.0

    if member.compress_size == 0:
        return float("inf")

    return member.file_size / member.compress_size


class ZIPParser(BaseParser[WaterDIPDocument]):
    """
    Safely inventory ZIP engineering packages.

    Nested parsing will be introduced separately so archive parsing remains
    bounded and explicitly controlled.
    """

    name = "zip"
    parser_version = "1.0"

    supported_extensions = frozenset({".zip"})

    supported_media_types = frozenset(
        {
            "application/zip",
            "application/x-zip-compressed",
        }
    )

    priority = 50

    def parse(
        self,
        source: ParseSource,
        context: ParserContext,
    ) -> WaterDIPDocument:
        content = source.read_bytes()
        checksum = source.checksum()

        max_members = int(
            context.parser_options.get(
                "zip_max_members",
                DEFAULT_MAX_MEMBERS,
            )
        )

        max_uncompressed_bytes = int(
            context.parser_options.get(
                "zip_max_uncompressed_bytes",
                DEFAULT_MAX_UNCOMPRESSED_BYTES,
            )
        )

        max_compression_ratio = float(
            context.parser_options.get(
                "zip_max_compression_ratio",
                DEFAULT_MAX_COMPRESSION_RATIO,
            )
        )

        attachments: list[DocumentAttachment] = []
        text_lines: list[str] = []
        warnings: list[str] = []

        try:
            archive = ZipFile(BytesIO(content))
        except BadZipFile as exc:
            raise ParserExecutionError(
                "Invalid ZIP archive.",
                parser_name=self.name,
                source=source.identifier,
            ) from exc

        with archive:
            members = archive.infolist()

            if len(members) > max_members:
                raise ParserExecutionError(
                    (
                        f"ZIP archive contains {len(members)} members, "
                        f"exceeding the configured limit of "
                        f"{max_members}."
                    ),
                    parser_name=self.name,
                    source=source.identifier,
                )

            total_uncompressed = sum(
                member.file_size
                for member in members
            )

            if total_uncompressed > max_uncompressed_bytes:
                raise ParserExecutionError(
                    (
                        "ZIP archive uncompressed size exceeds the "
                        "configured safety limit."
                    ),
                    parser_name=self.name,
                    source=source.identifier,
                    details={
                        "uncompressed_bytes": total_uncompressed,
                        "limit_bytes": max_uncompressed_bytes,
                    },
                )

            for index, member in enumerate(members):
                if member.is_dir():
                    continue

                unsafe_path = is_unsafe_archive_path(
                    member.filename
                )

                ratio = compression_ratio(member)

                suspicious_ratio = (
                    ratio > max_compression_ratio
                )

                if unsafe_path:
                    warnings.append(
                        f"Unsafe archive path detected: "
                        f"{member.filename}"
                    )

                if suspicious_ratio:
                    warnings.append(
                        f"Suspicious compression ratio detected for "
                        f"{member.filename}: {ratio:.2f}"
                    )

                member_checksum: str | None = None

                # Only read the member when it passed basic safety checks.
                if not unsafe_path and not suspicious_ratio:
                    with archive.open(member, "r") as stream:
                        hasher = hashlib.sha256()

                        while True:
                            block = stream.read(1024 * 1024)

                            if not block:
                                break

                            hasher.update(block)

                        member_checksum = hasher.hexdigest()

                attachment = DocumentAttachment(
                    id=deterministic_id(
                        "wd-attachment",
                        checksum,
                        index,
                        member.filename,
                    ),
                    filename=member.filename,
                    size_bytes=member.file_size,
                    checksum_sha256=member_checksum,
                    metadata={
                        "compressed_size": member.compress_size,
                        "compression_ratio": ratio,
                        "unsafe_path": unsafe_path,
                        "suspicious_compression_ratio": suspicious_ratio,
                    },
                )

                attachments.append(attachment)

                text_lines.append(
                    (
                        f"{member.filename} "
                        f"({member.file_size} bytes)"
                    )
                )

        provenance = build_source_provenance(
            source,
            context,
            parser_name=self.name,
            parser_version=self.parser_version,
            checksum=checksum,
            metadata={
                "archive_member_count": len(attachments),
                "total_uncompressed_bytes": total_uncompressed,
            },
        )

        document = WaterDIPDocument.create(
            source=provenance,
            title=filename_title(source.filename),
            text="\n".join(text_lines),
            document_type=DocumentType.ARCHIVE,
            attachments=attachments,
            metadata={
                "archive_member_count": len(attachments),
                "total_uncompressed_bytes": total_uncompressed,
            },
        )

        document.warnings.extend(warnings)

        return document