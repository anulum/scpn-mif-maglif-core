# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — device capability package

"""Device capability models of the SCPN MagLIF device family.

Public surface of the ``device_configuration_model`` and
``diagnostic_clock_semantics`` capabilities at
``computational_prototype`` maturity: validated parameter objects,
synthetic diagnostic and clock declarations aligned with the pinned SPO
observability catalogue, documented consistency estimates, canonical
serialisation with SHA-256 digests, and data-only pins to the SPO
registries. No claim about any real machine or diagnostic is made
anywhere in this package.
"""

from __future__ import annotations

from typing import Final

from scpn_mif_maglif_core.configuration import (
    LINER_ASPECT_RATIO_WINDOW,
    OWNED_CONFIGURATIONS,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_mif_maglif_core.errors import (
    DeviceConfigurationError,
    DeviceGeometryError,
    DiagnosticPlanError,
)
from scpn_mif_maglif_core.geometry import (
    BODY_NAMES,
    DeviceGeometry,
    DeviceModel3D,
    DeviceModelCAD,
    build_device_cad,
    build_device_model,
    geometry_from_record,
)
from scpn_mif_maglif_core.observability import (
    APPLICABLE_CANDIDATES,
    CATALOGUE_BINDING,
    CandidateProfile,
    ClockKind,
    ClockModel,
    ClockRelation,
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    FrameKind,
    ObservabilityBinding,
    ObservabilityClass,
    ReferenceFrame,
    SemanticCarrier,
    plan_from_bytes,
    plan_from_record,
)
from scpn_mif_maglif_core.parameters import Liner, ThreeStageDrive
from scpn_mif_maglif_core.physics import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    DriveInputs,
    DriveState,
    Level0Physics,
    StagnationState,
    drive_state,
    level0_physics,
    stagnation_state,
)
from scpn_mif_maglif_core.plan_envelope import (
    PlanEnvelope,
    envelope_for_plan,
    envelope_from_bytes,
    envelope_from_record,
    verify_envelope,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "APPLICABLE_CANDIDATES",
    "BODY_NAMES",
    "CATALOGUE_BINDING",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "LINER_ASPECT_RATIO_WINDOW",
    "OWNED_CONFIGURATIONS",
    "CandidateProfile",
    "ClockKind",
    "ClockModel",
    "ClockRelation",
    "ConsistencyFinding",
    "DeferredCandidate",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "DeviceGeometry",
    "DeviceGeometryError",
    "DeviceModel3D",
    "DeviceModelCAD",
    "DiagnosticChannelPlan",
    "DiagnosticPlan",
    "DiagnosticPlanError",
    "DriveInputs",
    "DriveState",
    "FrameKind",
    "Level0Physics",
    "Liner",
    "ObservabilityBinding",
    "ObservabilityClass",
    "PlanEnvelope",
    "ReferenceFrame",
    "RegistryBinding",
    "SemanticCarrier",
    "StagnationState",
    "ThreeStageDrive",
    "__version__",
    "build_device_cad",
    "build_device_model",
    "configuration_from_bytes",
    "configuration_from_record",
    "drive_state",
    "envelope_for_plan",
    "envelope_from_bytes",
    "envelope_from_record",
    "geometry_from_record",
    "level0_physics",
    "plan_from_bytes",
    "plan_from_record",
    "stagnation_state",
    "verify_envelope",
]
