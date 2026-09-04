# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — level-0 physics fixtures

"""Fixtures of the level-0 physics tests: one synthetic, one anchored.

The **reference** pair is synthetic and describes nothing.

The **anchor** pair is unusual for this group in that **every field of
both configuration objects is a printed value**. The filed chapter
SAND2021-3239B prints a complete MagLIF target — "a 10-mm tall, 5-mm outer
diameter, 0.5-mm wall thickness metal cylinder" — and the operating point
of the first integrated experiment: "a 10 T axial field, 0.5 kJ laser
preheat energy deposited, and 18 MA peak load current".

**What the record must keep straight.** That chapter is a RELATED public
source, not the cited S. A. Slutz et al., Phys. Plasmas 17 (2010) 056303,
which is behind a subscription and is not on file. The anchor reproduces
what the chapter prints; nothing here implies the 2010 paper was read.

Declared here, and said to be declared: the liner material density and the
implosion velocity. The chapter prints a velocity **range** of 70 to 100
kilometres per second rather than a value, so a value is declared from
inside it and the range is asserted separately.

Reproducing a printed value is an anchor, never a claim about that
machine.
"""

from __future__ import annotations

from scpn_mif_maglif_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_mif_maglif_core.parameters import Liner, ThreeStageDrive
from scpn_mif_maglif_core.physics import BERYLLIUM_DENSITY_KG_M3, DriveInputs

REGISTRY = RegistryBinding(version="1.0.0", digest_sha256="0" * 64)

#: Liner geometry printed by the filed chapter: a 10-mm tall, 5-mm outer
#: diameter, 0.5-mm wall thickness cylinder.
ANCHOR_OUTER_DIAMETER_MM = 5.0
ANCHOR_OUTER_RADIUS_MM = ANCHOR_OUTER_DIAMETER_MM / 2.0
ANCHOR_WALL_THICKNESS_MM = 0.5
ANCHOR_LENGTH_MM = 10.0
#: The aspect ratio those two printed numbers give. Exact in binary: both
#: operands are exactly representable and so is the quotient.
ANCHOR_ASPECT_RATIO = 5.0

#: Operating point of the first integrated experiment, printed together:
#: 10 T axial field, 0.5 kJ preheat deposited, 18 MA peak load current.
ANCHOR_AXIAL_FIELD_T = 10.0
ANCHOR_PREHEAT_ENERGY_KJ = 0.5
ANCHOR_PEAK_CURRENT_MA = 18.0

#: Printed as a range rather than a value: the peak implosion velocity is
#: given as 70 to 100 kilometres per second.
ANCHOR_VELOCITY_WINDOW_KM_S = (70.0, 100.0)
#: Declared from inside that window.
ANCHOR_IMPLOSION_VELOCITY_KM_S = 85.0
#: Declared: the chapter names no liner material density.
ANCHOR_LINER_DENSITY_KG_M3 = BERYLLIUM_DENSITY_KG_M3


def reference_configuration() -> DeviceConfiguration:
    """Build the synthetic reference configuration.

    Returns
    -------
    DeviceConfiguration
        A validated configuration whose numbers are round.
    """
    return DeviceConfiguration(
        identifier="maglif",
        liner=Liner(outer_radius_mm=3.0, wall_thickness_mm=1.0, length_mm=8.0),
        drive=ThreeStageDrive(
            peak_current_ma=20.0, axial_field_t=15.0, preheat_energy_kj=1.0
        ),
        registry=REGISTRY,
    )


def reference_inputs() -> DriveInputs:
    """Build the synthetic reference declared inputs.

    Returns
    -------
    DriveInputs
        Round declared inputs for the reference configuration.
    """
    return DriveInputs(
        liner_density_kg_m3=BERYLLIUM_DENSITY_KG_M3,
        implosion_velocity_km_s=80.0,
    )


def anchor_configuration() -> DeviceConfiguration:
    """Build the configuration of the printed target and operating point.

    Returns
    -------
    DeviceConfiguration
        A validated configuration whose every field is printed.
    """
    return DeviceConfiguration(
        identifier="maglif",
        liner=Liner(
            outer_radius_mm=ANCHOR_OUTER_RADIUS_MM,
            wall_thickness_mm=ANCHOR_WALL_THICKNESS_MM,
            length_mm=ANCHOR_LENGTH_MM,
        ),
        drive=ThreeStageDrive(
            peak_current_ma=ANCHOR_PEAK_CURRENT_MA,
            axial_field_t=ANCHOR_AXIAL_FIELD_T,
            preheat_energy_kj=ANCHOR_PREHEAT_ENERGY_KJ,
        ),
        registry=REGISTRY,
    )


def anchor_inputs() -> DriveInputs:
    """Build the declared inputs of the anchored operating point.

    Returns
    -------
    DriveInputs
        The declared density and a velocity from inside the printed
        window.
    """
    return DriveInputs(
        liner_density_kg_m3=ANCHOR_LINER_DENSITY_KG_M3,
        implosion_velocity_km_s=ANCHOR_IMPLOSION_VELOCITY_KM_S,
    )
