# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — tier-G1 device model

"""Tier-G1 tessellated model of a MagLIF target and its surroundings.

Five bodies in a fixed order, and the body set follows the three stages
the family is named for: the fuel column the laser preheats, the liner
that implodes onto it, the foil the laser enters through, and the pair of
coils that magnetise the fuel before either happens.

Every body is a cylinder or an annular tube about ``z``, so this tier
needs no primitive the shared library does not already have. The axis is
``z``, the origin is the midplane of the liner, and the coils sit
symmetrically about it.

The liner's outer radius, wall and length come from the configuration; the
rest of the envelope is declared. The model is the state **before** the
implosion.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.errors import GeometryError
from scpn_reactor_kernels.geometry import (
    TriangleMesh,
    annular_tube,
    cylinder_solid,
    require_segments,
)

from scpn_mif_maglif_core.configuration import DeviceConfiguration
from scpn_mif_maglif_core.errors import DeviceGeometryError
from scpn_mif_maglif_core.geometry.device import MM_PER_M, DeviceGeometry

MODEL_SCHEMA: Final = "scpn.maglif-3d-model.v1"
MODEL_SCHEMA_VERSION: Final = "1.0.0"
MODEL_UNITS: Final = {
    "length": "metre",
    "handedness": "right",
    "axis": "z along the axis of the liner and of the coil pair",
    "origin": "z = 0 at the midplane of the liner",
}
MODEL_NON_CLAIMS: Final = (
    "analytic surfaces tessellated from a synthetic configuration and geometry",
    (
        "the geometry is the state before the implosion; no body moves and no "
        "trajectory, deformation or instability is modelled"
    ),
    (
        "the coils are drawn as a pair of rings of declared size; no winding, "
        "no turn count, no circuit and no field map is modelled"
    ),
    "no body is a CAD solid or an engineering model",
    "no material property, load, field or neutronic quantity is carried",
    "no value describes or validates any real machine",
)

ROLE_FUEL: Final = "fuel"
ROLE_LINER: Final = "liner"
ROLE_WINDOW: Final = "window"
ROLE_COIL: Final = "coil"
MATERIAL_FUEL: Final = "fuel_gas"
MATERIAL_LINER_METAL: Final = "liner_metal"
MATERIAL_WINDOW_FOIL: Final = "window_foil"
MATERIAL_COIL_CONDUCTOR: Final = "coil_conductor"

BODY_FUEL_COLUMN: Final = "fuel_column"
BODY_LINER_SHELL: Final = "liner_shell"
BODY_ENTRANCE_WINDOW: Final = "laser_entrance_window"
BODY_COIL_UPSTREAM: Final = "magnetising_coil_upstream"
BODY_COIL_DOWNSTREAM: Final = "magnetising_coil_downstream"
BODY_NAMES: Final = (
    BODY_FUEL_COLUMN,
    BODY_LINER_SHELL,
    BODY_ENTRANCE_WINDOW,
    BODY_COIL_UPSTREAM,
    BODY_COIL_DOWNSTREAM,
)


@dataclass(frozen=True, slots=True)
class DeviceModel3D:
    """The tessellated device model of one configuration and geometry.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the configuration the model was built from.
    geometry_digest_sha256
        Digest of the geometry the model was built from.
    segments
        Circumferential segment count every body was tessellated at.
    meshes
        The five bodies in the fixed order of :data:`BODY_NAMES`.

    Raises
    ------
    DeviceGeometryError
        If the body names or their order differ from :data:`BODY_NAMES`.
    """

    configuration_digest_sha256: str
    geometry_digest_sha256: str
    segments: int
    meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the body set and its order.

        Raises
        ------
        DeviceGeometryError
            If the body names or their order differ from
            :data:`BODY_NAMES`.
        """
        names = tuple(mesh.name for mesh in self.meshes)
        if names != BODY_NAMES:
            raise DeviceGeometryError(
                f"meshes: bodies must be exactly {BODY_NAMES!r} in order, got {names!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with one entry per body.
        """
        return {
            "schema": MODEL_SCHEMA,
            "schema_version": MODEL_SCHEMA_VERSION,
            "units": dict(MODEL_UNITS),
            "non_claims": list(MODEL_NON_CLAIMS),
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "geometry_digest_sha256": self.geometry_digest_sha256,
            "segments": self.segments,
            "bodies": [
                {
                    "name": mesh.name,
                    "role": mesh.role,
                    "material_identifier": mesh.material_identifier,
                    "vertex_count": mesh.vertex_count,
                    "face_count": mesh.face_count,
                    "volume_m3": mesh.signed_volume_m3(),
                    "surface_area_m2": mesh.surface_area_m2(),
                }
                for mesh in self.meshes
            ],
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the model record canonically.

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
        """Identify the exact model record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _require_envelope(
    configuration: DeviceConfiguration, geometry: DeviceGeometry
) -> None:
    """Refuse a configuration and geometry that do not fit together.

    Parameters
    ----------
    configuration
        Validated device configuration.
    geometry
        Validated mechanical envelope.

    Raises
    ------
    DeviceGeometryError
        If the coils do not clear the liner, or if the coil pair overlaps
        itself at the declared separation. Each refusal names the two
        fields and their values.
    """
    outer = configuration.liner.outer_radius_mm
    if geometry.coil_inner_radius_mm <= outer:
        raise DeviceGeometryError(
            "coil_inner_radius_mm: must exceed the liner outer_radius_mm "
            f"({geometry.coil_inner_radius_mm!r} <= {outer!r})"
        )
    if geometry.coil_separation_mm <= geometry.coil_length_mm:
        raise DeviceGeometryError(
            "coil_separation_mm: must exceed coil_length_mm or the pair "
            f"overlaps itself ({geometry.coil_separation_mm!r} <= "
            f"{geometry.coil_length_mm!r})"
        )


def build_device_model(
    configuration: DeviceConfiguration, geometry: DeviceGeometry, segments: int
) -> DeviceModel3D:
    """Tessellate the five bodies of a validated design.

    Parameters
    ----------
    configuration
        Validated MagLIF configuration; its liner supplies the outer
        radius, the wall and the length.
    geometry
        Validated mechanical envelope.
    segments
        Circumferential segments for every body; at least 8, multiple
        of 8.

    Returns
    -------
    DeviceModel3D
        The composed model.

    Raises
    ------
    DeviceGeometryError
        If the segment count is invalid or the two do not fit together;
        the library's refusal is re-raised under the device error type
        with its message.
    """
    try:
        require_segments(segments)
    except GeometryError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    _require_envelope(configuration, geometry)
    liner = configuration.liner
    outer = liner.outer_radius_mm * MM_PER_M
    bore = (liner.outer_radius_mm - liner.wall_thickness_mm) * MM_PER_M
    half = liner.length_mm * MM_PER_M / 2.0
    window = geometry.entrance_window_thickness_mm * MM_PER_M
    coil_inner = geometry.coil_inner_radius_mm * MM_PER_M
    coil_outer = geometry.coil_outer_radius_mm * MM_PER_M
    coil_half = geometry.coil_length_mm * MM_PER_M / 2.0
    offset = geometry.coil_separation_mm * MM_PER_M / 2.0
    bodies = (
        (
            BODY_FUEL_COLUMN,
            ROLE_FUEL,
            MATERIAL_FUEL,
            cylinder_solid(bore, -half, half, segments),
        ),
        (
            BODY_LINER_SHELL,
            ROLE_LINER,
            MATERIAL_LINER_METAL,
            annular_tube(bore, outer, -half, half, segments),
        ),
        (
            BODY_ENTRANCE_WINDOW,
            ROLE_WINDOW,
            MATERIAL_WINDOW_FOIL,
            cylinder_solid(bore, half, half + window, segments),
        ),
        (
            BODY_COIL_UPSTREAM,
            ROLE_COIL,
            MATERIAL_COIL_CONDUCTOR,
            annular_tube(
                coil_inner,
                coil_outer,
                -offset - coil_half,
                -offset + coil_half,
                segments,
            ),
        ),
        (
            BODY_COIL_DOWNSTREAM,
            ROLE_COIL,
            MATERIAL_COIL_CONDUCTOR,
            annular_tube(
                coil_inner,
                coil_outer,
                offset - coil_half,
                offset + coil_half,
                segments,
            ),
        ),
    )
    meshes = tuple(
        TriangleMesh(
            name=name,
            role=role,
            material_identifier=material,
            vertices=vertices,
            faces=faces,
        )
        for name, role, material, (vertices, faces) in bodies
    )
    return DeviceModel3D(
        configuration_digest_sha256=configuration.digest_sha256(),
        geometry_digest_sha256=geometry.digest_sha256(),
        segments=segments,
        meshes=meshes,
    )
