# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — device geometry fixtures

"""Fixtures of the device-model tests: one synthetic, one anchored.

The **anchor** configuration is the printed one — the filed chapter gives
the whole liner — but the **envelope around it is declared**, because the
chapter names the surrounding hardware without dimensioning it: it says
"Helmholtz-like coils" and "a thin plastic foil" and no more.

The anchor's coil pair is declared **at** the Helmholtz condition, its
separation equal to its bore radius, and a test asserts the ratio is
exactly one. That is a property of the fixture, not a reading of the
source: the chapter says Helmholtz-*like*, so the model reports the ratio
and never imposes it.

The printed liner dimensions live in :mod:`physics_fixtures`, which is
their one home; this module imports the configuration from there.

Reproducing a printed dimension is an anchor, never a claim about that
machine.
"""

from __future__ import annotations

from physics_fixtures import anchor_configuration, reference_configuration

from scpn_mif_maglif_core.geometry.device import DeviceGeometry

#: Declared: the chapter names a thin plastic foil and no thickness.
ANCHOR_WINDOW_THICKNESS_MM = 0.05
#: Declared: the chapter names Helmholtz-like coils and no dimensions.
ANCHOR_COIL_INNER_RADIUS_MM = 8.0
ANCHOR_COIL_WALL_THICKNESS_MM = 2.0
ANCHOR_COIL_LENGTH_MM = 4.0
#: Declared equal to the coil bore radius, which is the Helmholtz
#: condition. Both operands are exactly representable, so the ratio is
#: exactly one and the test asserts an equality.
ANCHOR_COIL_SEPARATION_MM = ANCHOR_COIL_INNER_RADIUS_MM

#: Segment count of the reference tessellation.
REFERENCE_SEGMENTS = 64


def reference_geometry() -> DeviceGeometry:
    """Build the synthetic reference envelope.

    Returns
    -------
    DeviceGeometry
        A validated envelope with round dimensions that fits the
        synthetic reference configuration.
    """
    return DeviceGeometry(
        entrance_window_thickness_mm=0.1,
        coil_inner_radius_mm=10.0,
        coil_wall_thickness_mm=3.0,
        coil_length_mm=5.0,
        coil_separation_mm=12.0,
    )


def anchor_geometry() -> DeviceGeometry:
    """Build the declared envelope around the printed target.

    Returns
    -------
    DeviceGeometry
        A validated envelope whose coil pair sits at the Helmholtz
        condition.
    """
    return DeviceGeometry(
        entrance_window_thickness_mm=ANCHOR_WINDOW_THICKNESS_MM,
        coil_inner_radius_mm=ANCHOR_COIL_INNER_RADIUS_MM,
        coil_wall_thickness_mm=ANCHOR_COIL_WALL_THICKNESS_MM,
        coil_length_mm=ANCHOR_COIL_LENGTH_MM,
        coil_separation_mm=ANCHOR_COIL_SEPARATION_MM,
    )


__all__ = [
    "ANCHOR_COIL_INNER_RADIUS_MM",
    "ANCHOR_COIL_LENGTH_MM",
    "ANCHOR_COIL_SEPARATION_MM",
    "ANCHOR_COIL_WALL_THICKNESS_MM",
    "ANCHOR_WINDOW_THICKNESS_MM",
    "REFERENCE_SEGMENTS",
    "anchor_configuration",
    "anchor_geometry",
    "reference_configuration",
    "reference_geometry",
]
