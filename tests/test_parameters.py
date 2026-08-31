# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — parameter model tests

"""Every validation branch of the MagLIF parameter model.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import math

import pytest

from scpn_mif_maglif_core.errors import DeviceConfigurationError
from scpn_mif_maglif_core.parameters import (
    Liner,
    ThreeStageDrive,
    require_finite,
    require_positive,
)


def synthetic_liner(**overrides: float) -> Liner:
    """Build a valid synthetic liner with optional overrides."""
    values: dict[str, float] = {
        "outer_radius_mm": 3.0,
        "wall_thickness_mm": 0.5,
        "length_mm": 10.0,
    }
    values.update(overrides)
    return Liner(**values)


def synthetic_drive(**overrides: float) -> ThreeStageDrive:
    """Build a valid synthetic drive with optional overrides."""
    values: dict[str, float] = {
        "peak_current_ma": 20.0,
        "axial_field_t": 15.0,
        "preheat_energy_kj": 2.0,
    }
    values.update(overrides)
    return ThreeStageDrive(**values)


def test_require_finite_accepts_and_rejects() -> None:
    """The finite guard returns the value and rejects NaN and infinity."""
    assert require_finite("x", 1.5) == 1.5
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(DeviceConfigurationError, match="x: must be finite"):
            require_finite("x", bad)


def test_require_positive_accepts_and_rejects() -> None:
    """The positive guard returns the value and rejects zero and below."""
    assert require_positive("x", 0.1) == 0.1
    for bad in (0.0, -2.0):
        with pytest.raises(DeviceConfigurationError, match="strictly positive"):
            require_positive("x", bad)
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_positive("x", math.nan)


def test_valid_liner_and_aspect_ratio() -> None:
    """A valid liner constructs and derives its aspect ratio."""
    assert synthetic_liner().aspect_ratio == pytest.approx(6.0)


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"outer_radius_mm": 0.0}, "outer_radius_mm"),
        ({"wall_thickness_mm": -1.0}, "wall_thickness_mm"),
        ({"length_mm": 0.0}, "length_mm"),
        ({"wall_thickness_mm": 3.0}, "strictly smaller than"),
        ({"wall_thickness_mm": 4.0}, "strictly smaller than"),
    ],
)
def test_invalid_liner_is_rejected(overrides: dict[str, float], fragment: str) -> None:
    """Each liner violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_liner(**overrides)


def test_valid_drive_constructs() -> None:
    """A valid three-stage drive constructs unchanged."""
    assert synthetic_drive().axial_field_t == 15.0


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"peak_current_ma": 0.0}, "peak_current_ma"),
        ({"axial_field_t": 0.0}, "axial_field_t"),
        ({"preheat_energy_kj": -1.0}, "preheat_energy_kj"),
        ({"axial_field_t": math.nan}, "axial_field_t"),
    ],
)
def test_invalid_drive_is_rejected(overrides: dict[str, float], fragment: str) -> None:
    """Each drive violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_drive(**overrides)
