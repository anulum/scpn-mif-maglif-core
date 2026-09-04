# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — three-stage drive tests

"""The three stages expressed mechanically, on the printed operating point."""

from __future__ import annotations

import math

import pytest
from physics_fixtures import (
    ANCHOR_ASPECT_RATIO,
    ANCHOR_AXIAL_FIELD_T,
    ANCHOR_IMPLOSION_VELOCITY_KM_S,
    ANCHOR_LENGTH_MM,
    ANCHOR_OUTER_DIAMETER_MM,
    ANCHOR_OUTER_RADIUS_MM,
    ANCHOR_PEAK_CURRENT_MA,
    ANCHOR_PREHEAT_ENERGY_KJ,
    ANCHOR_VELOCITY_WINDOW_KM_S,
    ANCHOR_WALL_THICKNESS_MM,
    anchor_configuration,
    anchor_inputs,
    reference_configuration,
    reference_inputs,
)

from scpn_mif_maglif_core.errors import DeviceConfigurationError
from scpn_mif_maglif_core.physics.drive import (
    BERYLLIUM_DENSITY_KG_M3,
    MU0,
    DriveInputs,
    annulus_mass_kg,
    azimuthal_field_t,
    drive_state,
    magnetic_pressure_pa,
)


def test_the_azimuthal_field_is_the_closed_form() -> None:
    """The field outside an axial current is mu0 I over two pi r."""
    assert azimuthal_field_t(18.0e6, 0.0025) == MU0 * 18.0e6 / (2.0 * math.pi * 0.0025)


def test_the_field_falls_as_one_over_the_radius() -> None:
    """Twice the radius is half the field."""
    near = azimuthal_field_t(18.0e6, 0.0025)
    far = azimuthal_field_t(18.0e6, 0.005)
    assert math.isclose(far, near / 2.0, rel_tol=1.0e-15)


@pytest.mark.parametrize(
    ("current", "radius", "field_name"),
    [
        (0.0, 0.0025, "current_a"),
        (-1.0, 0.0025, "current_a"),
        (18.0e6, 0.0, "radius_m"),
        (18.0e6, math.nan, "radius_m"),
    ],
)
def test_the_field_refuses_each_argument_by_name(
    current: float, radius: float, field_name: str
) -> None:
    """Each refusal names the field that is wrong."""
    with pytest.raises(DeviceConfigurationError, match=field_name):
        azimuthal_field_t(current, radius)


def test_the_magnetic_pressure_is_the_closed_form() -> None:
    """The pressure is B squared over twice the permeability."""
    assert magnetic_pressure_pa(1440.0) == 1440.0 * 1440.0 / (2.0 * MU0)


@pytest.mark.parametrize("field", [0.0, -1.0, math.inf, math.nan])
def test_the_pressure_refuses_a_field_outside_its_domain(field: float) -> None:
    """A field that is not strictly positive and finite is refused."""
    with pytest.raises(DeviceConfigurationError, match="field_t"):
        magnetic_pressure_pa(field)


def test_the_mass_is_measured_from_the_outside_in() -> None:
    """The mass follows the outside, because that is how the liner is declared."""
    outer, wall, length = 0.0025, 0.0005, 0.01
    inner = outer - wall
    assert annulus_mass_kg(outer, wall, length, 1850.0) == (
        1850.0 * math.pi * (outer * outer - inner * inner) * length
    )


def test_a_wall_that_leaves_no_bore_is_refused() -> None:
    """A wall at or beyond the outer radius is not a shell."""
    with pytest.raises(DeviceConfigurationError, match="wall_m"):
        annulus_mass_kg(0.0025, 0.0025, 0.01, 1850.0)


@pytest.mark.parametrize(
    ("outer", "wall", "length", "density", "field_name"),
    [
        (0.0, 0.0005, 0.01, 1850.0, "outer_radius_m"),
        (0.0025, 0.0, 0.01, 1850.0, "wall_m"),
        (0.0025, 0.0005, math.inf, 1850.0, "length_m"),
        (0.0025, 0.0005, 0.01, math.nan, "density_kg_m3"),
    ],
)
def test_the_mass_refuses_each_argument_by_name(
    outer: float, wall: float, length: float, density: float, field_name: str
) -> None:
    """Each refusal names the field that is wrong."""
    with pytest.raises(DeviceConfigurationError, match=field_name):
        annulus_mass_kg(outer, wall, length, density)


@pytest.mark.parametrize(
    ("density", "velocity", "field_name"),
    [
        (0.0, 80.0, "liner_density_kg_m3"),
        (1850.0, -1.0, "implosion_velocity_km_s"),
        (1850.0, math.inf, "implosion_velocity_km_s"),
    ],
)
def test_the_declared_inputs_refuse_each_field_by_name(
    density: float, velocity: float, field_name: str
) -> None:
    """A declared input outside its bound is refused."""
    with pytest.raises(DeviceConfigurationError, match=field_name):
        DriveInputs(liner_density_kg_m3=density, implosion_velocity_km_s=velocity)


def test_the_state_converts_the_configuration_millimetres_to_si() -> None:
    """The configuration is in millimetres and every relation is SI."""
    configuration = reference_configuration()
    state = drive_state(configuration, reference_inputs())
    liner = configuration.liner
    assert state.liner_outer_radius_m == liner.outer_radius_mm * 1.0e-3
    assert state.liner_length_m == liner.length_mm * 1.0e-3
    assert (
        state.liner_bore_radius_m
        == (liner.outer_radius_mm - liner.wall_thickness_mm) * 1.0e-3
    )


def test_the_state_composes_each_stage_from_its_own_number() -> None:
    """Each of the three stages reaches the record through its own field."""
    configuration = reference_configuration()
    state = drive_state(configuration, reference_inputs())
    drive = configuration.drive
    assert state.peak_current_a == drive.peak_current_ma * 1.0e6
    assert state.axial_field_t == drive.axial_field_t
    assert state.preheat_energy_j == drive.preheat_energy_kj * 1.0e3
    assert state.drive_field_t == azimuthal_field_t(
        state.peak_current_a, state.liner_outer_radius_m
    )
    assert state.drive_pressure_pa == magnetic_pressure_pa(state.drive_field_t)


def test_the_preheat_density_is_the_energy_over_the_bore_volume() -> None:
    """The fuel receives the energy in the volume the bore encloses."""
    state = drive_state(reference_configuration(), reference_inputs())
    volume = math.pi * state.liner_bore_radius_m**2 * state.liner_length_m
    assert state.preheat_energy_density_j_m3 == state.preheat_energy_j / volume


def test_the_state_record_keys_are_the_declared_fields() -> None:
    """The record carries one key per field, in declaration order."""
    state = drive_state(reference_configuration(), reference_inputs())
    assert list(state.to_record()) == [
        "peak_current_a",
        "liner_outer_radius_m",
        "liner_bore_radius_m",
        "liner_length_m",
        "aspect_ratio",
        "drive_field_t",
        "drive_pressure_pa",
        "axial_field_t",
        "liner_mass_kg",
        "implosion_kinetic_energy_j",
        "preheat_energy_j",
        "preheat_energy_density_j_m3",
    ]


def test_the_anchor_aspect_ratio_is_the_printed_one_exactly() -> None:
    """The two printed liner numbers give the ratio exactly.

    The outer radius is half the printed 5-mm diameter and the wall is the
    printed 0.5 mm; both are exactly representable in binary and so is
    their quotient, so this is an equality and not a closeness.
    """
    assert ANCHOR_OUTER_RADIUS_MM == ANCHOR_OUTER_DIAMETER_MM / 2.0
    state = drive_state(anchor_configuration(), anchor_inputs())
    assert state.aspect_ratio == ANCHOR_ASPECT_RATIO


def test_every_printed_field_reaches_the_anchor_state() -> None:
    """All six configuration fields of this family are printed values."""
    state = drive_state(anchor_configuration(), anchor_inputs())
    assert state.liner_outer_radius_m == ANCHOR_OUTER_RADIUS_MM * 1.0e-3
    assert state.liner_length_m == ANCHOR_LENGTH_MM * 1.0e-3
    assert (
        state.liner_bore_radius_m
        == (ANCHOR_OUTER_RADIUS_MM - ANCHOR_WALL_THICKNESS_MM) * 1.0e-3
    )
    assert state.peak_current_a == ANCHOR_PEAK_CURRENT_MA * 1.0e6
    assert state.axial_field_t == ANCHOR_AXIAL_FIELD_T
    assert state.preheat_energy_j == ANCHOR_PREHEAT_ENERGY_KJ * 1.0e3


def test_the_declared_velocity_sits_inside_the_printed_window() -> None:
    """The chapter prints a range, so the declared value must be in it."""
    low, high = ANCHOR_VELOCITY_WINDOW_KM_S
    assert low <= ANCHOR_IMPLOSION_VELOCITY_KM_S <= high


def test_the_anchor_liner_mass_is_of_the_order_the_family_uses() -> None:
    """A MagLIF liner is a fraction of a gram, and this one is.

    Not an anchor on a printed number — the chapter prints no mass — but a
    check that the printed geometry and a declared beryllium density give
    a liner of the size this family actually builds, rather than one off
    by orders of magnitude through a unit slip.
    """
    state = drive_state(anchor_configuration(), anchor_inputs())
    assert state.liner_mass_kg == annulus_mass_kg(
        ANCHOR_OUTER_RADIUS_MM * 1.0e-3,
        ANCHOR_WALL_THICKNESS_MM * 1.0e-3,
        ANCHOR_LENGTH_MM * 1.0e-3,
        BERYLLIUM_DENSITY_KG_M3,
    )
    assert 5.0e-5 < state.liner_mass_kg < 5.0e-4
