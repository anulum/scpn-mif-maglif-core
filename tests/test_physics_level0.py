# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — level-0 record tests

"""The composed level-0 record: identity, canonicity and its non-claims."""

from __future__ import annotations

import hashlib
import json

import pytest
from physics_fixtures import (
    ANCHOR_AXIAL_FIELD_T,
    ANCHOR_PEAK_CURRENT_MA,
    anchor_configuration,
    anchor_inputs,
    reference_configuration,
    reference_inputs,
)

from scpn_mif_maglif_core.errors import DeviceConfigurationError
from scpn_mif_maglif_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    Level0Physics,
    level0_physics,
)


def reference_record() -> Level0Physics:
    """Build the synthetic reference level-0 record."""
    return level0_physics(reference_configuration(), reference_inputs(), 30.0)


def test_the_record_is_schema_tagged_and_states_its_non_claims() -> None:
    """The record names its schema and carries the non-claims verbatim."""
    record = reference_record().to_record()
    assert record["schema"] == LEVEL0_SCHEMA
    assert record["schema_version"] == LEVEL0_SCHEMA_VERSION
    assert record["non_claims"] == list(LEVEL0_NON_CLAIMS)
    assert list(record) == [
        "schema",
        "schema_version",
        "configuration_digest_sha256",
        "inputs",
        "drive",
        "stagnation",
        "non_claims",
    ]


def test_the_non_claims_name_both_ideal_limits_and_the_vacuum_field() -> None:
    """Three things a reader could over-read are refused in the record."""
    joined = " ".join(LEVEL0_NON_CLAIMS)
    assert "upper bounds" in joined
    assert "perfect-conductor" in joined
    assert "vacuum field" in joined


def test_the_record_carries_the_declared_inputs() -> None:
    """The two declared inputs reach the record under their own names."""
    assert reference_record().to_record()["inputs"] == {
        "liner_density_kg_m3": 1850.0,
        "implosion_velocity_km_s": 80.0,
    }


def test_the_record_binds_the_configuration_it_was_built_from() -> None:
    """The record carries the digest of its own configuration."""
    configuration = reference_configuration()
    record = level0_physics(configuration, reference_inputs(), 30.0)
    assert record.configuration_digest_sha256 == configuration.digest_sha256()


def test_the_stagnation_compresses_the_bore_the_drive_reports() -> None:
    """The two halves of the record agree on the radius they start from."""
    record = reference_record()
    assert record.stagnation.stagnation_radius_m == (
        record.drive.liner_bore_radius_m / record.stagnation.convergence_ratio
    )


def test_canonical_bytes_are_already_in_canonical_form() -> None:
    """Re-canonicalising the bytes is a no-op, and they round-trip."""
    record = reference_record()
    data = record.canonical_bytes()
    assert data.endswith(b"\n")
    decoded = json.loads(data)
    assert decoded == record.to_record()
    assert list(decoded) == sorted(decoded)
    again = json.dumps(decoded, sort_keys=True, separators=(",", ":"))
    assert data == (again + "\n").encode("utf-8")
    assert record.digest_sha256() == hashlib.sha256(data).hexdigest()


def test_the_digest_is_stable_and_moves_with_the_convergence() -> None:
    """The same inputs give the same bytes; a different ratio does not."""
    assert reference_record().digest_sha256() == reference_record().digest_sha256()
    other = level0_physics(reference_configuration(), reference_inputs(), 35.0)
    assert other.digest_sha256() != reference_record().digest_sha256()


def test_a_convergence_that_does_not_compress_is_refused() -> None:
    """The composed record applies the ratio contract before building."""
    with pytest.raises(DeviceConfigurationError, match="convergence_ratio"):
        level0_physics(reference_configuration(), reference_inputs(), 1.0)


def test_the_anchor_record_carries_the_printed_drive() -> None:
    """The printed current and field are recoverable from the record."""
    record = level0_physics(anchor_configuration(), anchor_inputs(), 30.0).to_record()
    assert record["drive"]["peak_current_a"] == ANCHOR_PEAK_CURRENT_MA * 1.0e6
    assert record["drive"]["axial_field_t"] == ANCHOR_AXIAL_FIELD_T
    assert record["drive"]["aspect_ratio"] == 5.0
    assert record["stagnation"]["compressed_axial_field_t"] == (
        ANCHOR_AXIAL_FIELD_T * 900.0
    )
