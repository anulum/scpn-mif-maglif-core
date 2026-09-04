# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — tier-G2 device model tests

"""The B-rep bodies agree with their closed forms and with tier G1."""

from __future__ import annotations

import functools
import hashlib
import json
import math

import pytest
from geometry_fixtures import (
    anchor_configuration,
    anchor_geometry,
    reference_configuration,
    reference_geometry,
)
from physics_fixtures import ANCHOR_LENGTH_MM, ANCHOR_OUTER_RADIUS_MM
from scpn_reactor_kernels.cad import MANIFEST_SCHEMA, MEASURE_TOLERANCE

from scpn_mif_maglif_core.errors import DeviceGeometryError
from scpn_mif_maglif_core.geometry.cad import (
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    DEFAULT_ANGULAR_DEFLECTION_RAD,
    DEFAULT_LINEAR_DEFLECTION_M,
    DEFAULT_REFERENCE_MESH_SEGMENTS,
    DeviceModelCAD,
    build_device_cad,
)
from scpn_mif_maglif_core.geometry.device import DeviceGeometry
from scpn_mif_maglif_core.geometry.model import BODY_NAMES

#: Digest of the reference CAD model record in the pinned back-end
#: environment (cadquery 2.8.0, OCP 7.9.3.1); a back-end bump re-pins it
#: as a governed data change.
REFERENCE_CAD_MODEL_SHA256 = (
    "e235817825ef39298c34c7fb42bbc2dab943416272c890ccdcd2a3a28bad2b82"
)


@functools.cache
def model() -> DeviceModelCAD:
    """Build the reference B-rep model of these tests, once.

    Cached deliberately. A MagLIF target is millimetres across and the
    deflection this tier declares is correspondingly fine, so one build
    costs seconds; building it per test costs minutes for no added
    evidence. The record is frozen and every refusal test constructs a new
    one from its fields rather than mutating it, so sharing is safe.
    """
    return build_device_cad(reference_configuration(), reference_geometry())


def test_the_bodies_are_the_five_in_order() -> None:
    """The B-rep body set matches the tier-G1 set exactly."""
    assert tuple(body.name for body in model().bodies) == BODY_NAMES


def test_every_body_agrees_with_its_analytic_closed_form() -> None:
    """Volume and area sit inside the library's measure tolerance."""
    for body in model().bodies:
        assert body.volume_relative_error <= MEASURE_TOLERANCE
        assert body.surface_area_relative_error <= MEASURE_TOLERANCE


def test_every_body_is_inside_its_faceting_deficit_bound() -> None:
    """The faceted volume is below the exact one, within the chord bound."""
    for body in model().bodies:
        assert body.faceted_volume_relative_deficit >= 0.0
        assert body.faceted_volume_relative_deficit <= body.faceted_volume_deficit_bound


def test_every_body_agrees_with_its_tier_g1_twin() -> None:
    """The two tiers describe one target, not two similar ones."""
    for body in model().bodies:
        assert abs(body.mesh_volume_relative_difference) <= (
            body.mesh_volume_difference_bound
        )


def test_the_deflection_is_finer_than_a_centimetre_scale_family_needs() -> None:
    """A millimetre-scale target needs a finer chord than a liner does.

    The chord bound scales with the smallest radius, and a MagLIF bore is
    two millimetres where the liner family's is two hundred. The default
    is set from that, not copied.
    """
    assert DEFAULT_LINEAR_DEFLECTION_M == 1.0e-5
    for body in model().bodies:
        assert body.faceted_volume_deficit_bound < 0.02


def test_the_record_is_schema_tagged_and_states_its_non_claims() -> None:
    """The record names its schema and carries the non-claims verbatim."""
    record = model().to_record()
    assert record["schema"] == CAD_MODEL_SCHEMA
    assert record["schema_version"] == CAD_MODEL_SCHEMA_VERSION
    assert record["non_claims"] == list(CAD_MODEL_NON_CLAIMS)
    assert record["reference_mesh_segments"] == DEFAULT_REFERENCE_MESH_SEGMENTS
    assert record["linear_deflection_m"] == DEFAULT_LINEAR_DEFLECTION_M
    assert record["angular_deflection_rad"] == DEFAULT_ANGULAR_DEFLECTION_RAD
    assert record["assembly_manifest"]["schema"] == MANIFEST_SCHEMA
    assert [body["name"] for body in record["bodies"]] == list(BODY_NAMES)


def test_the_back_ends_are_recorded_and_present() -> None:
    """The record names the environment its determinism is claimed in."""
    versions = model().backend_versions
    assert versions["cadquery"] != "unavailable"
    assert versions["ocp"] != "unavailable"


def test_the_record_is_canonical_and_its_digest_is_pinned() -> None:
    """The bytes are canonical and reproduce the pinned digest."""
    built = model()
    data = built.canonical_bytes()
    assert data.endswith(b"\n")
    assert json.loads(data) == built.to_record()
    assert built.digest_sha256() == hashlib.sha256(data).hexdigest()
    assert built.digest_sha256() == REFERENCE_CAD_MODEL_SHA256


def test_two_builds_of_the_same_design_agree() -> None:
    """The record is deterministic inside the pinned environment."""
    assert model().digest_sha256() == model().digest_sha256()


def test_the_step_export_is_the_digested_bytes() -> None:
    """The exported file is exactly the bytes the record digests."""
    built = model()
    assert built.step_sha256 == hashlib.sha256(built.step_data).hexdigest()
    assert built.step_data.startswith(b"ISO-10303-21;")


def _rebuild(built: DeviceModelCAD, **changes: object) -> DeviceModelCAD:
    """Rebuild a record with one field replaced, for the refusal tests."""
    fields: dict[str, object] = {
        "configuration_digest_sha256": built.configuration_digest_sha256,
        "geometry_digest_sha256": built.geometry_digest_sha256,
        "reference_mesh_segments": built.reference_mesh_segments,
        "linear_deflection_m": built.linear_deflection_m,
        "angular_deflection_rad": built.angular_deflection_rad,
        "backend_versions": built.backend_versions,
        "assembly_manifest": built.assembly_manifest,
        "step_sha256": built.step_sha256,
        "bodies": built.bodies,
        "step_data": built.step_data,
        "faceted_meshes": built.faceted_meshes,
    }
    fields.update(changes)
    return DeviceModelCAD(**fields)  # type: ignore[arg-type]


def test_a_manifest_with_the_wrong_body_count_is_refused() -> None:
    """The record checks the manifest it was handed."""
    built = model()
    broken = dict(built.assembly_manifest)
    broken["body_count"] = 4
    with pytest.raises(DeviceGeometryError, match="body_count"):
        _rebuild(built, assembly_manifest=broken)


def test_a_manifest_of_the_wrong_schema_is_refused() -> None:
    """A foreign manifest is not accepted silently."""
    built = model()
    broken = dict(built.assembly_manifest)
    broken["schema"] = "something.else.v1"
    with pytest.raises(DeviceGeometryError, match=r"assembly_manifest\.schema"):
        _rebuild(built, assembly_manifest=broken)


def test_bodies_out_of_order_are_refused() -> None:
    """The fixed body order is enforced on the B-rep record too."""
    built = model()
    with pytest.raises(DeviceGeometryError, match="must be exactly"):
        _rebuild(built, bodies=(built.bodies[1], built.bodies[0], *built.bodies[2:]))


def test_an_invalid_deflection_is_refused_by_the_builder() -> None:
    """The library's deflection contract governs the faceting."""
    with pytest.raises(DeviceGeometryError, match="deflection"):
        build_device_cad(reference_configuration(), reference_geometry(), 8, 0.0, 0.1)


def test_an_envelope_that_does_not_fit_is_refused_before_any_solid() -> None:
    """The tier-G1 envelope check runs first and refuses the same way."""
    tight = DeviceGeometry(0.1, 2.0, 3.0, 5.0, 12.0)
    with pytest.raises(DeviceGeometryError, match="coil_inner_radius_mm"):
        build_device_cad(anchor_configuration(), tight)


def test_the_anchor_bodies_carry_the_printed_liner_dimensions() -> None:
    """The printed values survive into the measured B-rep bodies."""
    record = build_device_cad(anchor_configuration(), anchor_geometry()).to_record()
    bodies = {body["name"]: body for body in record["assembly_manifest"]["bodies"]}
    liner = bodies["liner_shell"]
    assert math.isclose(
        liner["bounding_box_max_m"][0],
        ANCHOR_OUTER_RADIUS_MM * 1.0e-3,
        rel_tol=1.0e-12,
    )
    assert math.isclose(
        liner["bounding_box_max_m"][2] - liner["bounding_box_min_m"][2],
        ANCHOR_LENGTH_MM * 1.0e-3,
        rel_tol=1.0e-12,
    )
