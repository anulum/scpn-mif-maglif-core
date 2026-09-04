# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — device geometry tests

"""The mechanical envelope validates, serialises and round-trips."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any

import pytest
from geometry_fixtures import (
    ANCHOR_COIL_INNER_RADIUS_MM,
    ANCHOR_COIL_SEPARATION_MM,
    ANCHOR_COIL_WALL_THICKNESS_MM,
    anchor_geometry,
    reference_geometry,
)

from scpn_mif_maglif_core.errors import DeviceGeometryError
from scpn_mif_maglif_core.geometry.device import (
    GEOMETRY_FIELDS,
    DeviceGeometry,
    geometry_from_record,
)


def test_the_record_carries_every_declared_field() -> None:
    """The record is exactly the declared fields, and nothing else."""
    assert sorted(reference_geometry().to_record()) == sorted(GEOMETRY_FIELDS)


def test_the_coil_outer_radius_is_the_bore_plus_the_winding() -> None:
    """The derived radius is a sum, not a second declared number."""
    geometry = reference_geometry()
    assert geometry.coil_outer_radius_mm == (
        geometry.coil_inner_radius_mm + geometry.coil_wall_thickness_mm
    )


def test_the_helmholtz_ratio_is_reported_and_not_imposed() -> None:
    """The source says Helmholtz-*like*, so the model measures, not judges.

    The anchor fixture declares a pair at the condition, so its ratio is
    exactly one; the synthetic reference deliberately sits away from it
    and is accepted just the same.
    """
    assert anchor_geometry().helmholtz_ratio == 1.0
    assert ANCHOR_COIL_SEPARATION_MM == ANCHOR_COIL_INNER_RADIUS_MM
    assert reference_geometry().helmholtz_ratio != 1.0


def test_the_anchor_coil_outer_radius_follows_its_declared_parts() -> None:
    """The declared bore and winding give the declared outer radius."""
    assert anchor_geometry().coil_outer_radius_mm == (
        ANCHOR_COIL_INNER_RADIUS_MM + ANCHOR_COIL_WALL_THICKNESS_MM
    )


@pytest.mark.parametrize("field", GEOMETRY_FIELDS)
@pytest.mark.parametrize("value", [0.0, -1.0, math.inf, math.nan])
def test_every_field_is_refused_outside_its_domain(field: str, value: float) -> None:
    """A non-finite or non-positive value is refused, naming the field."""
    record = reference_geometry().to_record()
    record[field] = value
    with pytest.raises(DeviceGeometryError, match=field):
        geometry_from_record(record)


def test_a_record_round_trips_through_its_own_projection() -> None:
    """Projecting and rebuilding gives an equal geometry."""
    geometry = reference_geometry()
    assert geometry_from_record(geometry.to_record()) == geometry


def test_an_unknown_field_is_refused_and_named() -> None:
    """The parser is strict: an unexpected key is an error."""
    record: dict[str, Any] = dict(reference_geometry().to_record())
    record["coil_turns"] = 8
    with pytest.raises(DeviceGeometryError, match="coil_turns"):
        geometry_from_record(record)


def test_a_missing_field_is_refused_and_named() -> None:
    """Every declared field is required."""
    record = reference_geometry().to_record()
    del record["coil_length_mm"]
    with pytest.raises(DeviceGeometryError, match="coil_length_mm"):
        geometry_from_record(record)


@pytest.mark.parametrize("value", ["0.5", None, True])
def test_a_field_of_the_wrong_type_is_refused(value: Any) -> None:
    """A string, a null and a boolean are not real numbers."""
    record: dict[str, Any] = dict(reference_geometry().to_record())
    record["coil_length_mm"] = value
    with pytest.raises(DeviceGeometryError, match="coil_length_mm"):
        geometry_from_record(record)


def test_canonical_bytes_and_digest_identify_the_geometry() -> None:
    """The serialisation is canonical and the digest is of those bytes."""
    geometry = reference_geometry()
    data = geometry.canonical_bytes()
    assert data.endswith(b"\n")
    decoded = json.loads(data)
    assert decoded == geometry.to_record()
    assert list(decoded) == sorted(decoded)
    assert geometry.digest_sha256() == hashlib.sha256(data).hexdigest()
    assert geometry.digest_sha256() != anchor_geometry().digest_sha256()


def test_the_dataclass_is_reachable_directly() -> None:
    """The constructor validates the same way the parser does."""
    with pytest.raises(DeviceGeometryError, match="coil_separation_mm"):
        DeviceGeometry(0.1, 10.0, 3.0, 5.0, 0.0)
