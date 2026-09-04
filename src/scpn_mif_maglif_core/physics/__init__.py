# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — level-0 device physics package

"""Level-0 device physics of the MagLIF family.

Two closed forms on the validated configuration: the three stages of the
drive expressed mechanically — the azimuthal field the axial current puts
at the liner surface and its pressure, the liner's mass and implosion
energy, and the preheat energy density in the bore — and what the
convergence does to the magnetised fuel, by axial flux conservation and by
adiabatic compression. Both compressions are ideal limits recorded as
upper bounds. No equation is solved and no value describes a real machine.
Design record: ADR 0005.
"""

from __future__ import annotations

from scpn_mif_maglif_core.physics.compression import (
    MONATOMIC_GAMMA,
    StagnationState,
    adiabatic_temperature_gain,
    compressed_axial_field_t,
    density_gain,
    require_convergence_ratio,
    stagnation_state,
)
from scpn_mif_maglif_core.physics.drive import (
    ALUMINIUM_DENSITY_KG_M3,
    BERYLLIUM_DENSITY_KG_M3,
    MM_PER_M,
    MU0,
    DriveInputs,
    DriveState,
    annulus_mass_kg,
    azimuthal_field_t,
    drive_state,
    magnetic_pressure_pa,
)
from scpn_mif_maglif_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    Level0Physics,
    level0_physics,
)

__all__ = [
    "ALUMINIUM_DENSITY_KG_M3",
    "BERYLLIUM_DENSITY_KG_M3",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MM_PER_M",
    "MONATOMIC_GAMMA",
    "MU0",
    "DriveInputs",
    "DriveState",
    "Level0Physics",
    "StagnationState",
    "adiabatic_temperature_gain",
    "annulus_mass_kg",
    "azimuthal_field_t",
    "compressed_axial_field_t",
    "density_gain",
    "drive_state",
    "level0_physics",
    "magnetic_pressure_pa",
    "require_convergence_ratio",
    "stagnation_state",
]
