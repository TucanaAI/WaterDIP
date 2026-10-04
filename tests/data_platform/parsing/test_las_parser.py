from __future__ import annotations

from app.data_platform.parsing import (
    DocumentType,
    LASParser,
    ParseSource,
    ParserContext,
    ParserRegistry,
    register_builtin_parsers,
)
from app.data_platform.parsing.well_logs import (
    LogFamily,
    calculate_curve_statistics,
    classify_curve,
    normalize_mnemonic,
)


SAMPLE_LAS = """~Version Information
 VERS.                  2.0 : CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.                   NO : ONE LINE PER DEPTH STEP
~Well Information
 STRT.M               1000.0 : START DEPTH
 STOP.M               1002.0 : STOP DEPTH
 STEP.M                  0.5 : STEP
 NULL.                -999.25 : NULL VALUE
 COMP.              Equinor : COMPANY
 WELL.           15/9-F-1 C : WELL
 FLD.                  Volve : FIELD
 LOC.          North Sea : LOCATION
 UWI.            VOLVE-001 : UNIQUE WELL ID
~Curve Information
 DEPT.M                     : DEPTH
 GR.API                     : GAMMA RAY
 RHOB.G/C3                  : BULK DENSITY
 NPHI.V/V                   : NEUTRON POROSITY
 RDEP.OHMM                  : DEEP RESISTIVITY
 CALI.IN                    : CALIPER
~Parameter Information
 RUN .             1 : LOGGING RUN
~Other Information
 Synthetic WaterDIP LAS test fixture.
~ASCII Log Data
1000.0  75.0  2.35  0.22  10.0  8.50
1000.5  80.0  2.40  0.20  12.0  8.60
1001.0 -999.25 2.45  0.18  15.0  8.55
1001.5  95.0  2.50  0.16  20.0  8.70
1002.0 100.0  2.55  0.14  25.0  8.65
"""


def parse_sample():
    source = ParseSource.from_bytes(
        SAMPLE_LAS.encode("utf-8"),
        filename="15_9_F_1_C.las",
        dataset_id="well_logs",
    )

    result = LASParser().execute(
        source,
        ParserContext(),
    )

    return result.document


def test_mnemonic_normalization() -> None:
    assert normalize_mnemonic(
        " rhob "
    ) == "RHOB"

    assert normalize_mnemonic(
        "gamma-ray"
    ) == "GAMMA_RAY"


def test_curve_classification() -> None:
    assert (
        classify_curve("GR")
        == LogFamily.GAMMA_RAY
    )

    assert (
        classify_curve("RHOB")
        == LogFamily.DENSITY
    )

    assert (
        classify_curve("NPHI")
        == LogFamily.NEUTRON
    )

    assert (
        classify_curve("RDEP")
        == LogFamily.RESISTIVITY
    )

    assert (
        classify_curve("UNFAMILIAR_CURVE")
        == LogFamily.UNKNOWN
    )


def test_curve_statistics() -> None:
    statistics = calculate_curve_statistics(
        [
            10.0,
            20.0,
            float("nan"),
            30.0,
        ]
    )

    assert statistics.count == 3
    assert statistics.null_count == 1
    assert statistics.minimum == 10.0
    assert statistics.maximum == 30.0
    assert statistics.mean == 20.0


def test_las_parser_document_type() -> None:
    document = parse_sample()

    assert (
        document.document_type
        == DocumentType.WELL_LOG
    )

    assert document.source.parser_name == "las"


def test_las_parser_well_context() -> None:
    document = parse_sample()

    well = document.engineering.well

    assert well is not None
    assert well.well_name == "15/9-F-1 C"
    assert well.uwi == "VOLVE-001"


def test_las_parser_depth_interval() -> None:
    document = parse_sample()

    well_log = document.metadata[
        "well_log"
    ]

    depth = well_log["depth"]

    assert depth["start"] == 1000.0
    assert depth["stop"] == 1002.0
    assert depth["step"] == 0.5
    assert depth["unit"] == "M"
    assert depth["sample_count"] == 5
    assert depth["increasing"] is True


def test_las_parser_curves() -> None:
    document = parse_sample()

    well_log = document.metadata[
        "well_log"
    ]

    curves = {
        curve["mnemonic"]: curve
        for curve in well_log["curves"]
    }

    assert curves["GR"]["family"] == "gamma_ray"
    assert curves["RHOB"]["family"] == "density"
    assert curves["NPHI"]["family"] == "neutron"
    assert curves["RDEP"]["family"] == "resistivity"
    assert curves["CALI"]["family"] == "caliper"


def test_las_null_values_are_excluded() -> None:
    document = parse_sample()

    curves = {
        curve["mnemonic"]: curve
        for curve in document.metadata[
            "well_log"
        ]["curves"]
    }

    gr_statistics = curves["GR"][
        "statistics"
    ]

    assert gr_statistics["count"] == 4
    assert gr_statistics["null_count"] == 1
    assert gr_statistics["minimum"] == 75.0
    assert gr_statistics["maximum"] == 100.0


def test_las_engineering_entities() -> None:
    document = parse_sample()

    entities = {
        (
            entity.entity_type.value,
            entity.name,
        )
        for entity in document.engineering.entities
    }

    assert (
        "well",
        "15/9-F-1 C",
    ) in entities

    assert (
        "field",
        "Volve",
    ) in entities


def test_registry_selects_las_parser() -> None:
    registry = ParserRegistry()

    register_builtin_parsers(
        registry
    )

    source = ParseSource.from_bytes(
        SAMPLE_LAS.encode("utf-8"),
        filename="well.las",
    )

    parser = registry.select(source)

    assert parser.name == "las"