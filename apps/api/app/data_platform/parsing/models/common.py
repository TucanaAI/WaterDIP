"""
Shared enums and utility models for WaterDIP parsed engineering documents.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class WaterDIPModel(BaseModel):
    """
    Base model for canonical WaterDIP parsing models.

    Unknown fields are rejected deliberately so schema drift is detected
    during development rather than silently propagated downstream.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=False,
    )


class DocumentType(str, Enum):
    """High-level classification of an engineering document."""

    UNKNOWN = "unknown"

    REPORT = "report"
    TECHNICAL_REPORT = "technical_report"
    PRODUCTION_REPORT = "production_report"
    DRILLING_REPORT = "drilling_report"
    COMPLETION_REPORT = "completion_report"
    WELL_REPORT = "well_report"
    RESERVOIR_REPORT = "reservoir_report"
    GEOPHYSICS_REPORT = "geophysics_report"

    WELL_LOG = "well_log"
    PRODUCTION_DATA = "production_data"
    INJECTION_DATA = "injection_data"
    PRESSURE_DATA = "pressure_data"

    TABULAR_DATA = "tabular_data"
    SPREADSHEET = "spreadsheet"

    SEISMIC_METADATA = "seismic_metadata"
    GEOSCIENCE_DATA = "geoscience_data"

    SIMULATION_MODEL = "simulation_model"
    ECLIPSE_DECK = "eclipse_deck"
    RMS_DATA = "rms_data"

    DOCUMENT = "document"
    TEXT = "text"
    STRUCTURED_DATA = "structured_data"
    ARCHIVE = "archive"


class ContentType(str, Enum):
    """Canonical content categories extracted from source documents."""

    TEXT = "text"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    FIGURE = "figure"
    LIST = "list"
    CODE = "code"
    EQUATION = "equation"
    METADATA = "metadata"
    UNKNOWN = "unknown"


class EngineeringEntityType(str, Enum):
    """Engineering entities that may be associated with a document."""

    FIELD = "field"
    BLOCK = "block"
    LICENSE = "license"
    RESERVOIR = "reservoir"
    FORMATION = "formation"
    WELL = "well"
    WELLBORE = "wellbore"
    COMPLETION = "completion"
    ZONE = "zone"
    FACILITY = "facility"
    OPERATOR = "operator"
    COUNTRY = "country"
    BASIN = "basin"
    UNKNOWN = "unknown"


class DataQualityStatus(str, Enum):
    """High-level quality state of parsed information."""

    UNKNOWN = "unknown"
    VALID = "valid"
    PARTIAL = "partial"
    INVALID = "invalid"


class ExtractionMethod(str, Enum):
    """How a piece of information was obtained."""

    SOURCE = "source"
    PARSER = "parser"
    RULE = "rule"
    REGEX = "regex"
    HEURISTIC = "heuristic"
    LLM = "llm"
    HUMAN = "human"
    UNKNOWN = "unknown"


class ChunkType(str, Enum):
    """Semantic category assigned to a retrieval chunk."""

    TEXT = "text"
    SECTION = "section"
    TABLE = "table"
    FIGURE = "figure"
    WELL_LOG = "well_log"
    TIMESERIES = "timeseries"
    METADATA = "metadata"
    MIXED = "mixed"