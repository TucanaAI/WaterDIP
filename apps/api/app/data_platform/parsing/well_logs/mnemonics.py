"""
Well-log mnemonic normalization for WaterDIP.

This module contains conservative aliases for common logging mnemonics.
It is intentionally extensible as WaterDIP encounters additional datasets.
"""

from __future__ import annotations

import re


_NON_ALPHANUMERIC = re.compile(r"[^A-Z0-9_]")


def normalize_mnemonic(
    mnemonic: str,
) -> str:
    """Normalize a curve mnemonic for matching."""

    value = mnemonic.strip().upper()
    value = value.replace("-", "_")
    value = value.replace(" ", "_")
    value = _NON_ALPHANUMERIC.sub("", value)

    return value


DEPTH_MNEMONICS = frozenset(
    {
        "DEPT",
        "DEPTH",
        "MD",
        "TVD",
        "TVDSS",
    }
)

GAMMA_RAY_MNEMONICS = frozenset(
    {
        "GR",
        "GAM",
        "GAMMA",
        "GAMMA_RAY",
        "GRGC",
        "SGR",
        "CGR",
    }
)

SP_MNEMONICS = frozenset(
    {
        "SP",
        "SSP",
    }
)

RESISTIVITY_MNEMONICS = frozenset(
    {
        "RT",
        "RDEP",
        "RMED",
        "RSHAL",
        "RXO",
        "ILD",
        "ILM",
        "LLD",
        "LLS",
        "MSFL",
        "AT10",
        "AT20",
        "AT30",
        "AT60",
        "AT90",
        "RESD",
        "RESM",
        "RESS",
    }
)

DENSITY_MNEMONICS = frozenset(
    {
        "RHOB",
        "RHOZ",
        "DEN",
        "DENS",
        "ZDEN",
    }
)

NEUTRON_MNEMONICS = frozenset(
    {
        "NPHI",
        "TNPH",
        "CNPOR",
        "NPOR",
        "NEUT",
    }
)

SONIC_MNEMONICS = frozenset(
    {
        "DT",
        "DTC",
        "DTCO",
        "AC",
        "DTS",
        "DTSM",
    }
)

CALIPER_MNEMONICS = frozenset(
    {
        "CALI",
        "CAL",
        "HCAL",
        "C1",
        "C2",
    }
)

PHOTOELECTRIC_MNEMONICS = frozenset(
    {
        "PE",
        "PEF",
        "PEFZ",
    }
)

POROSITY_MNEMONICS = frozenset(
    {
        "PHI",
        "PHIT",
        "PHIE",
        "POR",
        "PORO",
    }
)

SATURATION_MNEMONICS = frozenset(
    {
        "SW",
        "SWT",
        "SWE",
        "SO",
        "SG",
    }
)

TEMPERATURE_MNEMONICS = frozenset(
    {
        "TEMP",
        "TEMPERATURE",
        "BHT",
    }
)

PRESSURE_MNEMONICS = frozenset(
    {
        "PRES",
        "PRESSURE",
        "BHP",
        "PRES_FORM",
    }
)

PERMEABILITY_MNEMONICS = frozenset(
    {
        "PERM",
        "PERMEABILITY",
        "K",
        "KH",
        "KV",
    }
)

FACIES_MNEMONICS = frozenset(
    {
        "FACIES",
        "FAC",
        "LITH",
        "LITHO",
    }
)