"""
Canonical WaterDIP engineering document models.
"""

from .chunk import (
    ChunkPosition,
    DocumentChunk,
    generate_chunk_id,
)
from .common import (
    ChunkType,
    ContentType,
    DataQualityStatus,
    DocumentType,
    EngineeringEntityType,
    ExtractionMethod,
    WaterDIPModel,
)
from .content import (
    BoundingBox,
    DocumentAttachment,
    DocumentFigure,
    DocumentSection,
    DocumentTable,
    TableCell,
)
from .document import (
    WaterDIPDocument,
    generate_document_id,
)
from .engineering import (
    EngineeringEntity,
    EngineeringMetadata,
    Measurement,
    ProductionContext,
    ReservoirContext,
    WellContext,
)
from .source import (
    SourceLocation,
    SourceProvenance,
)

__all__ = [
    "BoundingBox",
    "ChunkPosition",
    "ChunkType",
    "ContentType",
    "DataQualityStatus",
    "DocumentAttachment",
    "DocumentChunk",
    "DocumentFigure",
    "DocumentSection",
    "DocumentTable",
    "DocumentType",
    "EngineeringEntity",
    "EngineeringEntityType",
    "EngineeringMetadata",
    "ExtractionMethod",
    "Measurement",
    "ProductionContext",
    "ReservoirContext",
    "SourceLocation",
    "SourceProvenance",
    "TableCell",
    "WaterDIPDocument",
    "WaterDIPModel",
    "WellContext",
    "generate_chunk_id",
    "generate_document_id",
]