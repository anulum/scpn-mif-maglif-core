# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — MagLIF parameter model

"""Validated parameter objects of a MagLIF configuration.

The derived quantity implements one standard design measure and nothing
more: the liner aspect ratio ``AR = R / dR`` (S. A. Slutz et al., Phys.
Plasmas 17 (2010) 056303, baseline AR = 6). It is a rough consistency
instrument with documented applicability bounds; no claim about any real
machine follows from it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from scpn_mif_maglif_core.errors import DeviceConfigurationError


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class Liner:
    """Metal-liner parameters of a MagLIF configuration.

    Parameters
    ----------
    outer_radius_mm
        Liner outer radius ``R`` in millimetres; strictly positive.
    wall_thickness_mm
        Liner wall thickness ``dR`` in millimetres; strictly positive
        and strictly smaller than ``outer_radius_mm``.
    length_mm
        Liner length in millimetres; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If any parameter is non-finite or the wall does not fit inside
        the radius.
    """

    outer_radius_mm: float
    wall_thickness_mm: float
    length_mm: float

    def __post_init__(self) -> None:
        """Validate the liner invariants.

        Raises
        ------
        DeviceConfigurationError
            If any parameter is non-finite or the wall does not fit
            inside the radius.
        """
        require_positive("outer_radius_mm", self.outer_radius_mm)
        require_positive("wall_thickness_mm", self.wall_thickness_mm)
        require_positive("length_mm", self.length_mm)
        if self.wall_thickness_mm >= self.outer_radius_mm:
            raise DeviceConfigurationError(
                "wall_thickness_mm: must be strictly smaller than "
                f"outer_radius_mm ({self.wall_thickness_mm!r} >= "
                f"{self.outer_radius_mm!r})"
            )

    @property
    def aspect_ratio(self) -> float:
        """Liner aspect ratio ``AR = R / dR``.

        Returns
        -------
        float
            Aspect ratio of the validated liner.
        """
        return self.outer_radius_mm / self.wall_thickness_mm


@dataclass(frozen=True, slots=True)
class ThreeStageDrive:
    """Three-stage drive of a MagLIF configuration.

    Parameters
    ----------
    peak_current_ma
        Peak liner-drive current in mega-amperes; strictly positive.
    axial_field_t
        Axial premagnetisation field in tesla; strictly positive — the
        premagnetisation stage is a defining feature of MagLIF.
    preheat_energy_kj
        Laser-preheat energy in kilojoules; strictly positive — the
        preheat stage is a defining feature of MagLIF.

    Raises
    ------
    DeviceConfigurationError
        If any parameter is non-finite or not strictly positive.
    """

    peak_current_ma: float
    axial_field_t: float
    preheat_energy_kj: float

    def __post_init__(self) -> None:
        """Validate the three-stage-drive invariants.

        Raises
        ------
        DeviceConfigurationError
            If any parameter is non-finite or not strictly positive.
        """
        require_positive("peak_current_ma", self.peak_current_ma)
        require_positive("axial_field_t", self.axial_field_t)
        require_positive("preheat_energy_kj", self.preheat_energy_kj)
