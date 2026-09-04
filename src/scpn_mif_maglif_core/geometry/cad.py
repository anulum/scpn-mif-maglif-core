# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — tier-G2 device model

"""Tier-G2 B-rep model of a MagLIF target and its surroundings.

The same five bodies as tier G1, built as exact solids through the shared
library's ``cad`` group instead of tessellated, with every body checked
fail-closed by the library's evidence kernel against its analytic closed
forms and against its tier-G1 twin, and exported as normalised STEP bytes
with a digest.

Every body is a cylinder or an annular tube, so each has a well-defined
smallest circular radius and the faceting deficit bound needs no special
case here.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.cad import (
    MANIFEST_SCHEMA,
    BodyEvidence,
    BrepAssembly,
    annular_tube_brep,
    assembly_evidence,
    backend_versions,
    cylinder_solid_brep,
    facet_assembly,
    step_bytes,
    step_sha256,
)
from scpn_reactor_kernels.errors import CadError, GeometryError
from scpn_reactor_kernels.geometry import TriangleMesh

from scpn_mif_maglif_core.configuration import DeviceConfiguration
from scpn_mif_maglif_core.errors import DeviceGeometryError
from scpn_mif_maglif_core.geometry.device import MM_PER_M, DeviceGeometry
from scpn_mif_maglif_core.geometry.model import (
    BODY_COIL_DOWNSTREAM,
    BODY_COIL_UPSTREAM,
    BODY_ENTRANCE_WINDOW,
    BODY_FUEL_COLUMN,
    BODY_LINER_SHELL,
    BODY_NAMES,
    MATERIAL_COIL_CONDUCTOR,
    MATERIAL_FUEL,
    MATERIAL_LINER_METAL,
    MATERIAL_WINDOW_FOIL,
    ROLE_COIL,
    ROLE_FUEL,
    ROLE_LINER,
    ROLE_WINDOW,
    build_device_model,
)

CAD_MODEL_SCHEMA: Final = "scpn.maglif-cad-model.v1"
CAD_MODEL_SCHEMA_VERSION: Final = "1.0.0"
CAD_MODEL_UNITS: Final = {
    "length": "metre",
    "handedness": "right",
    "axis": "z along the axis of the liner and of the coil pair",
    "origin": "z = 0 at the midplane of the liner",
}
CAD_MODEL_NON_CLAIMS: Final = (
    "exact solids of revolution of a synthetic configuration and geometry",
    (
        "the geometry is the state before the implosion; no body moves and no "
        "trajectory, deformation or instability is modelled"
    ),
    (
        "the coils are drawn as a pair of rings of declared size; no winding, "
        "no turn count, no circuit and no field map is modelled"
    ),
    (
        "determinism of the STEP bytes is claimed within one pinned back-end "
        "environment only, never across back-end versions"
    ),
    "no body is an engineering model and no fabrication tolerance is carried",
    "no value describes or validates any real machine",
)

#: Reference tessellation the B-rep bodies are checked against.
DEFAULT_REFERENCE_MESH_SEGMENTS: Final = 8
#: Mesher deflections of the faceting comparison. Finer than the liner
#: family's, because a MagLIF target is millimetres across rather than
#: centimetres and the chord bound scales with the smallest radius.
DEFAULT_LINEAR_DEFLECTION_M: Final = 1.0e-5
DEFAULT_ANGULAR_DEFLECTION_RAD: Final = 0.1


@dataclass(frozen=True, slots=True)
class DeviceModelCAD:
    """The B-rep device model of one configuration and geometry.

    Parameters
    ----------
    configuration_digest_sha256, geometry_digest_sha256
        Digests of the inputs the model was built from.
    reference_mesh_segments
        Tier-G1 reference the bodies were checked against.
    linear_deflection_m, angular_deflection_rad
        Mesher deflections of the faceting comparison.
    backend_versions
        Versions of the pinned back-ends that produced the solids.
    assembly_manifest
        The library's assembly manifest of the five bodies.
    step_sha256
        Digest of the normalised STEP bytes.
    bodies
        Checked evidence of each body, in the fixed order.
    step_data
        The normalised STEP bytes themselves.
    faceted_meshes
        The faceted meshes the evidence was computed from.

    Raises
    ------
    DeviceGeometryError
        If the manifest schema, the body count or the body order is wrong.
    """

    configuration_digest_sha256: str
    geometry_digest_sha256: str
    reference_mesh_segments: int
    linear_deflection_m: float
    angular_deflection_rad: float
    backend_versions: dict[str, str]
    assembly_manifest: dict[str, Any]
    step_sha256: str
    bodies: tuple[BodyEvidence, ...]
    step_data: bytes
    faceted_meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the manifest and the body set.

        Raises
        ------
        DeviceGeometryError
            If the manifest schema, the body count or the body order is
            wrong.
        """
        if self.assembly_manifest.get("schema") != MANIFEST_SCHEMA:
            raise DeviceGeometryError(
                f"assembly_manifest.schema: must be {MANIFEST_SCHEMA!r}"
            )
        if self.assembly_manifest.get("body_count") != len(BODY_NAMES):
            raise DeviceGeometryError(
                f"assembly_manifest.body_count: must be {len(BODY_NAMES)}, got "
                f"{self.assembly_manifest.get('body_count')!r}"
            )
        names = tuple(body.name for body in self.bodies)
        if names != BODY_NAMES:
            raise DeviceGeometryError(
                f"bodies: must be exactly {BODY_NAMES!r} in order, got {names!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with one entry per body.
        """
        return {
            "schema": CAD_MODEL_SCHEMA,
            "schema_version": CAD_MODEL_SCHEMA_VERSION,
            "units": dict(CAD_MODEL_UNITS),
            "non_claims": list(CAD_MODEL_NON_CLAIMS),
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "geometry_digest_sha256": self.geometry_digest_sha256,
            "reference_mesh_segments": self.reference_mesh_segments,
            "linear_deflection_m": self.linear_deflection_m,
            "angular_deflection_rad": self.angular_deflection_rad,
            "backend_versions": dict(self.backend_versions),
            "assembly_manifest": self.assembly_manifest,
            "step_sha256": self.step_sha256,
            "bodies": [body.to_record() for body in self.bodies],
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


def build_device_cad(
    configuration: DeviceConfiguration,
    geometry: DeviceGeometry,
    segments: int = DEFAULT_REFERENCE_MESH_SEGMENTS,
    linear_deflection_m: float = DEFAULT_LINEAR_DEFLECTION_M,
    angular_deflection_rad: float = DEFAULT_ANGULAR_DEFLECTION_RAD,
) -> DeviceModelCAD:
    """Build the B-rep device model of a validated design.

    Parameters
    ----------
    configuration
        Validated MagLIF configuration.
    geometry
        Validated mechanical envelope.
    segments
        Segment count of the tier-G1 reference mesh of the comparison.
    linear_deflection_m, angular_deflection_rad
        Mesher deflections of the faceting comparison.

    Returns
    -------
    DeviceModelCAD
        The composed, fail-closed checked model with its STEP export.

    Raises
    ------
    DeviceGeometryError
        If a count or a deflection is invalid, if the configuration and
        the geometry do not fit together, or if a body violates a declared
        evidence bound; the library's refusals are re-raised under the
        device error type with their messages.
        :class:`~scpn_reactor_kernels.errors.CadUnavailableError` if the
        optional CAD back-end is absent.
    """
    reference = build_device_model(configuration, geometry, segments)
    liner = configuration.liner
    outer = liner.outer_radius_mm * MM_PER_M
    bore = (liner.outer_radius_mm - liner.wall_thickness_mm) * MM_PER_M
    half = liner.length_mm * MM_PER_M / 2.0
    window = geometry.entrance_window_thickness_mm * MM_PER_M
    coil_inner = geometry.coil_inner_radius_mm * MM_PER_M
    coil_outer = geometry.coil_outer_radius_mm * MM_PER_M
    coil_half = geometry.coil_length_mm * MM_PER_M / 2.0
    offset = geometry.coil_separation_mm * MM_PER_M / 2.0
    try:
        assembly = BrepAssembly(
            (
                cylinder_solid_brep(
                    bore, -half, half, BODY_FUEL_COLUMN, ROLE_FUEL, MATERIAL_FUEL
                ),
                annular_tube_brep(
                    bore,
                    outer,
                    -half,
                    half,
                    BODY_LINER_SHELL,
                    ROLE_LINER,
                    MATERIAL_LINER_METAL,
                ),
                cylinder_solid_brep(
                    bore,
                    half,
                    half + window,
                    BODY_ENTRANCE_WINDOW,
                    ROLE_WINDOW,
                    MATERIAL_WINDOW_FOIL,
                ),
                annular_tube_brep(
                    coil_inner,
                    coil_outer,
                    -offset - coil_half,
                    -offset + coil_half,
                    BODY_COIL_UPSTREAM,
                    ROLE_COIL,
                    MATERIAL_COIL_CONDUCTOR,
                ),
                annular_tube_brep(
                    coil_inner,
                    coil_outer,
                    offset - coil_half,
                    offset + coil_half,
                    BODY_COIL_DOWNSTREAM,
                    ROLE_COIL,
                    MATERIAL_COIL_CONDUCTOR,
                ),
            )
        )
        faceted = facet_assembly(assembly, linear_deflection_m, angular_deflection_rad)
        smallest_radii = (bore, bore, bore, coil_inner, coil_inner)
        bodies = assembly_evidence(
            assembly.bodies,
            smallest_radii,
            faceted,
            reference.meshes,
            linear_deflection_m,
            segments,
        )
    except (CadError, GeometryError) as exc:
        raise DeviceGeometryError(str(exc)) from exc
    manifest = assembly.manifest()
    extras = {
        "schema": CAD_MODEL_SCHEMA,
        "schema_version": CAD_MODEL_SCHEMA_VERSION,
        "configuration_digest_sha256": configuration.digest_sha256(),
        "geometry_digest_sha256": geometry.digest_sha256(),
        "assembly_manifest_sha256": assembly.manifest_sha256(),
        "units": dict(CAD_MODEL_UNITS),
        "non_claims": list(CAD_MODEL_NON_CLAIMS),
        "backend_versions": backend_versions(),
    }
    step_data = step_bytes(assembly, extras)
    return DeviceModelCAD(
        configuration_digest_sha256=configuration.digest_sha256(),
        geometry_digest_sha256=geometry.digest_sha256(),
        reference_mesh_segments=segments,
        linear_deflection_m=linear_deflection_m,
        angular_deflection_rad=angular_deflection_rad,
        backend_versions=backend_versions(),
        assembly_manifest=manifest,
        step_sha256=step_sha256(step_data),
        bodies=bodies,
        step_data=step_data,
        faceted_meshes=faceted,
    )
