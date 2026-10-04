"""
Conservative well-log curve-family classification.
"""

from __future__ import annotations

from .mnemonics import (
    CALIPER_MNEMONICS,
    DENSITY_MNEMONICS,
    DEPTH_MNEMONICS,
    FACIES_MNEMONICS,
    GAMMA_RAY_MNEMONICS,
    NEUTRON_MNEMONICS,
    PERMEABILITY_MNEMONICS,
    PHOTOELECTRIC_MNEMONICS,
    POROSITY_MNEMONICS,
    PRESSURE_MNEMONICS,
    RESISTIVITY_MNEMONICS,
    SATURATION_MNEMONICS,
    SONIC_MNEMONICS,
    SP_MNEMONICS,
    TEMPERATURE_MNEMONICS,
    normalize_mnemonic,
)
from .models import LogFamily


_FAMILY_LOOKUP = {
    LogFamily.DEPTH: DEPTH_MNEMONICS,
    LogFamily.GAMMA_RAY: GAMMA_RAY_MNEMONICS,
    LogFamily.SPONTANEOUS_POTENTIAL: SP_MNEMONICS,
    LogFamily.RESISTIVITY: RESISTIVITY_MNEMONICS,
    LogFamily.DENSITY: DENSITY_MNEMONICS,
    LogFamily.NEUTRON: NEUTRON_MNEMONICS,
    LogFamily.SONIC: SONIC_MNEMONICS,
    LogFamily.CALIPER: CALIPER_MNEMONICS,
    LogFamily.PHOTOELECTRIC: PHOTOELECTRIC_MNEMONICS,
    LogFamily.POROSITY: POROSITY_MNEMONICS,
    LogFamily.SATURATION: SATURATION_MNEMONICS,
    LogFamily.TEMPERATURE: TEMPERATURE_MNEMONICS,
    LogFamily.PRESSURE: PRESSURE_MNEMONICS,
    LogFamily.PERMEABILITY: PERMEABILITY_MNEMONICS,
    LogFamily.FACIES: FACIES_MNEMONICS,
}


def classify_curve(
    mnemonic: str,
) -> LogFamily:
    """
    Classify a well-log mnemonic into a broad engineering family.

    Exact normalized matches are used deliberately. Unknown mnemonics are not
    guessed from loose substrings.
    """

    normalized = normalize_mnemonic(mnemonic)

    for family, mnemonics in _FAMILY_LOOKUP.items():
        if normalized in mnemonics:
            return family

    return LogFamily.UNKNOWN