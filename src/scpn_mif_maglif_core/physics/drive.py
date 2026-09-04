# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — the three-stage drive

"""What the three stages of a MagLIF drive do, in closed form.

The family is defined by driving one target three ways in sequence:
magnetise it with an axial field, preheat the fuel with a laser, then
implode the liner with a large axial current. The configuration carries
one number for each stage, and this module says what each one means
mechanically.

**The implosion stage.** The current runs axially through the liner, so
outside it the field is azimuthal, ``B = mu0 I / (2 pi r)`` at radius
``r``. Evaluated at the liner's outer surface that is the field doing the
pushing, and its magnetic pressure ``B^2 / 2 mu0`` is the drive pressure.

**The liner it pushes.** The configuration gives the outer radius and the
wall, so the bore is their difference and the shell is an annulus. Its
mass follows from a declared material density, and its kinetic energy from
a declared implosion velocity — neither is in the configuration, and both
are recorded as declared.

**The preheat stage.** The energy deposited divided by the fuel volume the
bore encloses, which is what the fuel actually receives per unit volume.

Reference for the arrangement and for the anchor: the public chapter
SAND2021-3239B (Slutz a co-author), which prints a MagLIF target and the
operating point of the first integrated experiment. It is a RELATED
chapter, not the cited 2010 paper, which is not freely obtainable.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final

from scpn_mif_maglif_core.configuration import DeviceConfiguration
from scpn_mif_maglif_core.errors import DeviceConfigurationError
from scpn_mif_maglif_core.parameters import require_positive

#: Vacuum permeability, SI, CODATA.
MU0: Final = 1.25663706212e-6
#: Density of beryllium, the material MagLIF liners are usually made of.
BERYLLIUM_DENSITY_KG_M3: Final = 1850.0
#: Density of aluminium, the other liner material in common use.
ALUMINIUM_DENSITY_KG_M3: Final = 2700.0
#: Metres per millimetre; the configuration is in millimetres and every
#: relation here is SI.
MM_PER_M: Final = 1.0e-3


@dataclass(frozen=True, slots=True)
class DriveInputs:
    """Declared inputs the configuration does not carry.

    Parameters
    ----------
    liner_density_kg_m3
        Mass density of the liner material; strictly positive.
    implosion_velocity_km_s
        Peak implosion velocity; strictly positive. The filed chapter
        prints a range of 70 to 100 kilometres per second, so a value is
        declared from it rather than derived.

    Raises
    ------
    DeviceConfigurationError
        If either input is non-finite or not strictly positive.
    """

    liner_density_kg_m3: float
    implosion_velocity_km_s: float

    def __post_init__(self) -> None:
        """Validate both declared inputs.

        Raises
        ------
        DeviceConfigurationError
            If either input is non-finite or not strictly positive.
        """
        require_positive("liner_density_kg_m3", self.liner_density_kg_m3)
        require_positive("implosion_velocity_km_s", self.implosion_velocity_km_s)

    def to_record(self) -> dict[str, float]:
        """Project the inputs to a JSON-serialisable record.

        Returns
        -------
        dict[str, float]
            One key per declared input.
        """
        return {
            "liner_density_kg_m3": self.liner_density_kg_m3,
            "implosion_velocity_km_s": self.implosion_velocity_km_s,
        }


def azimuthal_field_t(current_a: float, radius_m: float) -> float:
    """Return the azimuthal field of an axial current at a radius.

    Parameters
    ----------
    current_a
        Axial current in ampere; strictly positive.
    radius_m
        Radius at which the field is evaluated; strictly positive.

    Returns
    -------
    float
        ``mu0 I / (2 pi r)``, the field outside a cylindrical conductor
        carrying ``I`` along its axis.

    Raises
    ------
    DeviceConfigurationError
        If either argument is non-finite or not strictly positive.
    """
    current = require_positive("current_a", current_a)
    radius = require_positive("radius_m", radius_m)
    return MU0 * current / (2.0 * math.pi * radius)


def magnetic_pressure_pa(field_t: float) -> float:
    """Return the magnetic pressure of a field.

    Parameters
    ----------
    field_t
        Magnetic flux density in tesla; strictly positive.

    Returns
    -------
    float
        ``B^2 / 2 mu0`` in pascal.

    Raises
    ------
    DeviceConfigurationError
        If the field is non-finite or not strictly positive.
    """
    field = require_positive("field_t", field_t)
    return field * field / (2.0 * MU0)


def annulus_mass_kg(
    outer_radius_m: float, wall_m: float, length_m: float, density_kg_m3: float
) -> float:
    """Return the mass of an annular cylindrical shell given its outside.

    Parameters
    ----------
    outer_radius_m
        Outer radius; strictly positive.
    wall_m
        Radial wall thickness; strictly positive and strictly smaller
        than the outer radius, or the shell has no bore.
    length_m
        Axial length; strictly positive.
    density_kg_m3
        Material density; strictly positive.

    Returns
    -------
    float
        ``rho pi (R^2 - (R - w)^2) l``: the exact annulus, measured from
        the outside in, which is the way this family's configuration
        declares a liner.

    Raises
    ------
    DeviceConfigurationError
        If any argument is non-finite or not strictly positive, or if the
        wall is not strictly smaller than the outer radius.
    """
    outer = require_positive("outer_radius_m", outer_radius_m)
    wall = require_positive("wall_m", wall_m)
    length = require_positive("length_m", length_m)
    density = require_positive("density_kg_m3", density_kg_m3)
    if wall >= outer:
        raise DeviceConfigurationError(
            f"wall_m: must be strictly smaller than outer_radius_m, got "
            f"{wall!r} >= {outer!r}"
        )
    inner = outer - wall
    return density * math.pi * (outer * outer - inner * inner) * length


@dataclass(frozen=True, slots=True)
class DriveState:
    """The three stages of one configuration, expressed mechanically.

    Parameters
    ----------
    peak_current_a
        Peak load current in ampere, from the configuration.
    liner_outer_radius_m, liner_bore_radius_m, liner_length_m
        The liner in SI, from the configuration's millimetres.
    aspect_ratio
        ``R / dR`` of the validated liner.
    drive_field_t
        Azimuthal field at the liner's outer surface at peak current.
    drive_pressure_pa
        Magnetic pressure of that field.
    axial_field_t
        The magnetising field before the implosion, from the
        configuration.
    liner_mass_kg
        Mass of the annular shell at the declared density.
    implosion_kinetic_energy_j
        ``m v^2 / 2`` at the declared velocity.
    preheat_energy_j
        Laser energy deposited, from the configuration.
    preheat_energy_density_j_m3
        That energy divided by the fuel volume the bore encloses.
    """

    peak_current_a: float
    liner_outer_radius_m: float
    liner_bore_radius_m: float
    liner_length_m: float
    aspect_ratio: float
    drive_field_t: float
    drive_pressure_pa: float
    axial_field_t: float
    liner_mass_kg: float
    implosion_kinetic_energy_j: float
    preheat_energy_j: float
    preheat_energy_density_j_m3: float

    def to_record(self) -> dict[str, Any]:
        """Project the state to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "peak_current_a": self.peak_current_a,
            "liner_outer_radius_m": self.liner_outer_radius_m,
            "liner_bore_radius_m": self.liner_bore_radius_m,
            "liner_length_m": self.liner_length_m,
            "aspect_ratio": self.aspect_ratio,
            "drive_field_t": self.drive_field_t,
            "drive_pressure_pa": self.drive_pressure_pa,
            "axial_field_t": self.axial_field_t,
            "liner_mass_kg": self.liner_mass_kg,
            "implosion_kinetic_energy_j": self.implosion_kinetic_energy_j,
            "preheat_energy_j": self.preheat_energy_j,
            "preheat_energy_density_j_m3": self.preheat_energy_density_j_m3,
        }


def drive_state(configuration: DeviceConfiguration, inputs: DriveInputs) -> DriveState:
    """Compose the drive state of one validated configuration.

    Parameters
    ----------
    configuration
        Validated MagLIF configuration; its liner and its three-stage
        drive supply every quantity except the two declared inputs.
    inputs
        Declared liner density and implosion velocity.

    Returns
    -------
    DriveState
        The composed state.

    Raises
    ------
    DeviceConfigurationError
        If a declared input falls outside its bound; the refusals name
        the field.
    """
    liner = configuration.liner
    drive = configuration.drive
    outer = liner.outer_radius_mm * MM_PER_M
    wall = liner.wall_thickness_mm * MM_PER_M
    length = liner.length_mm * MM_PER_M
    bore = outer - wall
    current = drive.peak_current_ma * 1.0e6
    velocity = inputs.implosion_velocity_km_s * 1.0e3
    field = azimuthal_field_t(current, outer)
    mass = annulus_mass_kg(outer, wall, length, inputs.liner_density_kg_m3)
    preheat = drive.preheat_energy_kj * 1.0e3
    return DriveState(
        peak_current_a=current,
        liner_outer_radius_m=outer,
        liner_bore_radius_m=bore,
        liner_length_m=length,
        aspect_ratio=liner.aspect_ratio,
        drive_field_t=field,
        drive_pressure_pa=magnetic_pressure_pa(field),
        axial_field_t=drive.axial_field_t,
        liner_mass_kg=mass,
        implosion_kinetic_energy_j=0.5 * mass * velocity * velocity,
        preheat_energy_j=preheat,
        preheat_energy_density_j_m3=preheat / (math.pi * bore * bore * length),
    )
