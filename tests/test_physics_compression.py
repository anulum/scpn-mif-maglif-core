# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — compression tests

"""Axial flux conservation and adiabatic compression, in their ideal limits."""

from __future__ import annotations

import math
from collections.abc import Callable

import pytest
from physics_fixtures import ANCHOR_AXIAL_FIELD_T

from scpn_mif_maglif_core.errors import DeviceConfigurationError
from scpn_mif_maglif_core.physics.compression import (
    MONATOMIC_GAMMA,
    adiabatic_temperature_gain,
    compressed_axial_field_t,
    density_gain,
    stagnation_state,
)


def test_the_axial_field_rises_with_the_square_of_the_convergence() -> None:
    """Flux through the liner is conserved, so B r^2 is constant."""
    assert compressed_axial_field_t(10.0, 30.0) == 10.0 * 900.0


def test_the_density_gain_is_the_area_ratio() -> None:
    """A cylindrical compression conserves the number per unit length."""
    assert density_gain(30.0) == 900.0


def test_the_temperature_gain_is_the_adiabatic_power() -> None:
    """``(r0/r)^(2(gamma-1))``; at gamma = 5/3 the exponent is 4/3."""
    assert math.isclose(
        adiabatic_temperature_gain(8.0), 8.0 ** (4.0 / 3.0), rel_tol=1.0e-12
    )


def test_the_temperature_gain_uses_the_shared_deterministic_kernel() -> None:
    """The one transcendental goes through the library, not the platform.

    That is the part of this module that genuinely needs determinism
    across back-ends; the rest is two multiplications that are exact in
    IEEE arithmetic everywhere, which is why they are not library kernels.
    """
    from scpn_reactor_kernels.numerics.transcendental import power

    assert adiabatic_temperature_gain(6.0) == power(6.0, 2.0 * (MONATOMIC_GAMMA - 1.0))


@pytest.mark.parametrize("ratio", [1.0, 0.5, 0.0])
def test_every_relation_refuses_a_ratio_that_does_not_converge(ratio: float) -> None:
    """A contract only some of the functions apply is not a contract."""
    calls: tuple[Callable[[], float], ...] = (
        lambda: compressed_axial_field_t(10.0, ratio),
        lambda: density_gain(ratio),
        lambda: adiabatic_temperature_gain(ratio),
    )
    for call in calls:
        with pytest.raises(DeviceConfigurationError, match="convergence_ratio"):
            call()


@pytest.mark.parametrize("index", [1.0, 0.5, 0.0, math.nan])
def test_an_index_that_does_not_heat_is_refused(index: float) -> None:
    """At gamma of one or below, an adiabatic compression does not raise T."""
    with pytest.raises(DeviceConfigurationError, match="adiabatic_index"):
        adiabatic_temperature_gain(30.0, index)


def test_a_power_that_leaves_the_kernel_range_is_re_raised() -> None:
    """The library's refusal reaches the caller as a device error."""
    with pytest.raises(DeviceConfigurationError, match=r"power|exponent"):
        adiabatic_temperature_gain(1.0e6, 1.0e6)


def test_a_field_outside_its_domain_is_refused() -> None:
    """The magnetising field must be strictly positive and finite."""
    with pytest.raises(DeviceConfigurationError, match="initial_field_t"):
        compressed_axial_field_t(0.0, 30.0)


def test_the_state_reports_the_stagnation_radius_of_the_bore() -> None:
    """The record carries the radius the declared ratio corresponds to."""
    state = stagnation_state(ANCHOR_AXIAL_FIELD_T, 0.002, 30.0)
    assert state.stagnation_radius_m == 0.002 / 30.0
    assert state.convergence_ratio == 30.0
    assert state.adiabatic_index == MONATOMIC_GAMMA
    assert state.compressed_axial_field_t == ANCHOR_AXIAL_FIELD_T * 900.0


def test_the_state_refuses_a_bore_outside_its_domain() -> None:
    """The bore the fuel starts in must be strictly positive and finite."""
    with pytest.raises(DeviceConfigurationError, match="bore_radius_m"):
        stagnation_state(10.0, 0.0, 30.0)


def test_the_state_record_keys_are_the_declared_fields() -> None:
    """The record carries one key per field, in declaration order."""
    assert list(stagnation_state(10.0, 0.002, 30.0).to_record()) == [
        "convergence_ratio",
        "stagnation_radius_m",
        "adiabatic_index",
        "compressed_axial_field_t",
        "density_gain",
        "temperature_gain",
    ]
