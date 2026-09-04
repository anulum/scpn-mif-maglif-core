# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — device geometry model

"""Validated mechanical envelope of a MagLIF target and its surroundings.

The configuration carries the liner: its outer radius, its wall and its
length. Those are read from there and not repeated. What this envelope
adds is what the filed chapter says surrounds the liner — the pair of
"Helmholtz-like coils" that apply the axial field, and the "thin plastic
foil" the laser enters through.

**"Helmholtz-like" is taken at its word.** A true Helmholtz pair has its
two coils separated by exactly one coil radius, which makes the field
maximally uniform on the axis between them. The source says *like*, not
*is*, so this model does not impose that condition. It reports how far the
declared arrangement sits from it, as a ratio that is one at the Helmholtz
condition, and leaves the caller to declare what it wants.

Validation is fail-closed, serialisation is canonical, and the SHA-256
digest identifies the exact geometry.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_mif_maglif_core.errors import DeviceGeometryError
from scpn_mif_maglif_core.parameters import require_positive

GEOMETRY_FIELDS: Final = (
    "entrance_window_thickness_mm",
    "coil_inner_radius_mm",
    "coil_wall_thickness_mm",
    "coil_length_mm",
    "coil_separation_mm",
)

#: Metres per millimetre; this family declares its hardware in millimetres.
MM_PER_M: Final = 1.0e-3


def _positive(name: str, value: float) -> float:
    """Apply the shared positivity rule under the geometry error type.

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
    DeviceGeometryError
        If the value is non-finite or not strictly positive.
    """
    try:
        return require_positive(name, value)
    except ValueError as exc:
        raise DeviceGeometryError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class DeviceGeometry:
    """Validated MagLIF mechanical envelope (millimetres in the names).

    Parameters
    ----------
    entrance_window_thickness_mm
        Axial thickness of the laser entrance foil; strictly positive.
    coil_inner_radius_mm
        Bore radius of each magnetising coil; strictly positive and
        checked against the liner when a model is built.
    coil_wall_thickness_mm
        Radial winding thickness of each coil; strictly positive.
    coil_length_mm
        Axial length of each coil; strictly positive.
    coil_separation_mm
        Centre-to-centre separation of the pair; strictly positive.

    Raises
    ------
    DeviceGeometryError
        If any value is non-finite or not strictly positive.
    """

    entrance_window_thickness_mm: float
    coil_inner_radius_mm: float
    coil_wall_thickness_mm: float
    coil_length_mm: float
    coil_separation_mm: float

    def __post_init__(self) -> None:
        """Validate every declared value.

        Raises
        ------
        DeviceGeometryError
            If any value is non-finite or not strictly positive.
        """
        for name in GEOMETRY_FIELDS:
            _positive(name, getattr(self, name))

    @property
    def coil_outer_radius_mm(self) -> float:
        """Outer radius of each coil (bore plus winding)."""
        return self.coil_inner_radius_mm + self.coil_wall_thickness_mm

    @property
    def helmholtz_ratio(self) -> float:
        """Separation over coil radius; one at the Helmholtz condition.

        Returns
        -------
        float
            ``s / R``. A true Helmholtz pair sits at exactly one. The
            filed chapter says the coils are Helmholtz-*like*, so this is
            reported and never enforced.
        """
        return self.coil_separation_mm / self.coil_inner_radius_mm

    def to_record(self) -> dict[str, float]:
        """Project the geometry to a JSON-serialisable record.

        Returns
        -------
        dict[str, float]
            Every declared parameter under its name.
        """
        return {name: getattr(self, name) for name in GEOMETRY_FIELDS}

    def canonical_bytes(self) -> bytes:
        """Serialise the geometry canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact geometry.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _number(record: dict[str, Any], field: str) -> float:
    """Return one required real-number field of a record.

    Parameters
    ----------
    record
        Decoded object.
    field
        Field name.

    Returns
    -------
    float
        The value as a float.

    Raises
    ------
    DeviceGeometryError
        If the field is absent or is not a real number.
    """
    if field not in record:
        raise DeviceGeometryError(f"{field}: required")
    value = record[field]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DeviceGeometryError(f"{field}: must be a real number, got {value!r}")
    return float(value)


def geometry_from_record(record: dict[str, Any]) -> DeviceGeometry:
    """Build a geometry from a decoded record, refusing unknown fields.

    Parameters
    ----------
    record
        Decoded object carrying exactly :data:`GEOMETRY_FIELDS`.

    Returns
    -------
    DeviceGeometry
        The validated geometry.

    Raises
    ------
    DeviceGeometryError
        If a field is missing, of the wrong type, unknown, or violates a
        model invariant.
    """
    unknown = sorted(set(record) - set(GEOMETRY_FIELDS))
    if unknown:
        raise DeviceGeometryError(f"geometry: unknown fields {unknown!r}")
    return DeviceGeometry(**{name: _number(record, name) for name in GEOMETRY_FIELDS})
