# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — compression at stagnation

"""What the converging liner does to the magnetised, preheated fuel.

Two conservation laws in their ideal limit, both upper bounds.

**Axial flux compression.** The liner traps the axial flux the magnetising
stage put through the fuel, so ``B_z pi r^2`` is constant and
``B_z(r) = B_z0 (r_0 / r)^2``. A real liner has finite conductivity and
loses flux, so this is a ceiling on the field at stagnation.

**Adiabatic compression.** A cylindrical compression that loses no heat
raises the density as ``(r_0 / r)^2`` and the temperature as
``n^(gamma - 1)``. A real compression radiates and conducts, so this too
is a ceiling.

**Why these are here and not in the shared library.** The library declares
``shared_physics_kernels`` as an owned domain and that domain is empty, so
the question was asked properly rather than skipped. The answer is that
the content is two multiplications and one call into a kernel that is
already shared: ``B_0 r^2`` and ``r^2`` are exact in IEEE arithmetic on
every platform, so the bit-exactness argument that justifies every kernel
the library does own does not apply to them, and the library's kernel
contract would demand a native mirror, parity by bit pattern and a
benchmark row for them. That is ceremony larger than the content. The one
part that genuinely needs determinism — the non-integer power — already
goes through the library's transcendental kernel, here as everywhere else
in the group.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.errors import NumericsError
from scpn_reactor_kernels.numerics.transcendental import power

from scpn_mif_maglif_core.errors import DeviceConfigurationError
from scpn_mif_maglif_core.parameters import require_positive

#: Adiabatic index of a monatomic ideal gas.
MONATOMIC_GAMMA: Final = 5.0 / 3.0


def require_convergence_ratio(ratio: float) -> float:
    """Return a convergence ratio strictly greater than one.

    Parameters
    ----------
    ratio
        Ratio of the initial bore to the stagnation radius.

    Returns
    -------
    float
        The validated ratio.

    Raises
    ------
    DeviceConfigurationError
        If the ratio is not strictly greater than one. A liner that does
        not converge compresses nothing.
    """
    value = require_positive("convergence_ratio", ratio)
    if value <= 1.0:
        raise DeviceConfigurationError(
            f"convergence_ratio: must be strictly greater than one, got {value!r}"
        )
    return value


def compressed_axial_field_t(initial_field_t: float, convergence_ratio: float) -> float:
    """Return the axial field after a perfectly flux-conserving compression.

    Parameters
    ----------
    initial_field_t
        Field the magnetising stage applied; strictly positive.
    convergence_ratio
        ``r_0 / r``; strictly greater than one.

    Returns
    -------
    float
        ``B_z0 (r_0 / r)^2``, an upper bound.

    Raises
    ------
    DeviceConfigurationError
        If the field or the ratio falls outside its bound.
    """
    field = require_positive("initial_field_t", initial_field_t)
    ratio = require_convergence_ratio(convergence_ratio)
    return field * ratio * ratio


def density_gain(convergence_ratio: float) -> float:
    """Return the density gain of a cylindrical compression.

    Parameters
    ----------
    convergence_ratio
        ``r_0 / r``; strictly greater than one.

    Returns
    -------
    float
        ``(r_0 / r)^2``: the area ratio, because a cylindrical
        compression conserves the number per unit length.

    Raises
    ------
    DeviceConfigurationError
        If the ratio is not strictly greater than one.
    """
    ratio = require_convergence_ratio(convergence_ratio)
    return ratio * ratio


def adiabatic_temperature_gain(
    convergence_ratio: float, adiabatic_index: float = MONATOMIC_GAMMA
) -> float:
    """Return the temperature gain of an adiabatic cylindrical compression.

    Parameters
    ----------
    convergence_ratio
        ``r_0 / r``; strictly greater than one.
    adiabatic_index
        ``gamma``; strictly greater than one, or the compression would
        not heat.

    Returns
    -------
    float
        ``(r_0 / r)^(2 (gamma - 1))``, through the shared library's
        deterministic power kernel. An upper bound.

    Raises
    ------
    DeviceConfigurationError
        If the ratio or the index falls outside its bound, or if the
        power leaves the kernel's admissible range; the kernel's refusal
        is re-raised under the device error type with its message.
    """
    ratio = require_convergence_ratio(convergence_ratio)
    index = require_positive("adiabatic_index", adiabatic_index)
    if index <= 1.0:
        raise DeviceConfigurationError(
            f"adiabatic_index: must be strictly greater than one, got {index!r}"
        )
    try:
        return power(ratio, 2.0 * (index - 1.0))
    except NumericsError as exc:
        raise DeviceConfigurationError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class StagnationState:
    """What one declared convergence does to the magnetised fuel.

    Parameters
    ----------
    convergence_ratio
        ``r_0 / r`` of the declared stagnation radius.
    stagnation_radius_m
        The radius the ratio corresponds to.
    adiabatic_index
        ``gamma`` used for the temperature gain.
    compressed_axial_field_t
        ``B_z0 (r_0 / r)^2``.
    density_gain
        ``(r_0 / r)^2``.
    temperature_gain
        ``(r_0 / r)^(2 (gamma - 1))``.
    """

    convergence_ratio: float
    stagnation_radius_m: float
    adiabatic_index: float
    compressed_axial_field_t: float
    density_gain: float
    temperature_gain: float

    def to_record(self) -> dict[str, Any]:
        """Project the state to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "convergence_ratio": self.convergence_ratio,
            "stagnation_radius_m": self.stagnation_radius_m,
            "adiabatic_index": self.adiabatic_index,
            "compressed_axial_field_t": self.compressed_axial_field_t,
            "density_gain": self.density_gain,
            "temperature_gain": self.temperature_gain,
        }


def stagnation_state(
    initial_field_t: float,
    bore_radius_m: float,
    convergence_ratio: float,
    adiabatic_index: float = MONATOMIC_GAMMA,
) -> StagnationState:
    """Compose the stagnation state of one declared convergence.

    Parameters
    ----------
    initial_field_t
        Axial field before the implosion; strictly positive.
    bore_radius_m
        The liner bore the fuel starts in; strictly positive.
    convergence_ratio
        ``r_0 / r``; strictly greater than one.
    adiabatic_index
        ``gamma``; strictly greater than one.

    Returns
    -------
    StagnationState
        The composed state.

    Raises
    ------
    DeviceConfigurationError
        If any argument falls outside its bound.
    """
    bore = require_positive("bore_radius_m", bore_radius_m)
    ratio = require_convergence_ratio(convergence_ratio)
    return StagnationState(
        convergence_ratio=ratio,
        stagnation_radius_m=bore / ratio,
        adiabatic_index=adiabatic_index,
        compressed_axial_field_t=compressed_axial_field_t(initial_field_t, ratio),
        density_gain=density_gain(ratio),
        temperature_gain=adiabatic_temperature_gain(ratio, adiabatic_index),
    )
