# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF MagLIF Core — report diagnostic tests

"""The review report and the ranges it flags.

The report advises; it does not refuse. Each flag names the quantity, the
range it fell outside, and the channel it came from.

All plans in this module are synthetic fixtures; none describes any real
diagnostic, measurement, or facility.
"""

from __future__ import annotations

from observability_fixtures import (
    CLOCK_RELATIONS,
    CLOCK_TOPOLOGY,
    EVENT_BINDINGS,
    NONCYCLIC_BINDINGS,
    REFERENCE_FRAMES,
    REFERENCE_TRANSFORMATIONS,
    SIGNALS_CH_COMPRESSION_TRAJECTORY_SET,
    SIGNALS_CH_LINER_ARRIVAL_TRAIN,
    SIGNALS_CH_LINER_ASYMMETRY_SET,
    channel_derived,
    channel_event_train,
    channel_noncyclic_one,
    channel_oscillator,
    clock_facility,
    clock_shot,
    clock_simulation,
    derived_channel,
    plan_with,
    synthetic_plan,
)
from scpn_mif_maglif_core.observability import (
    CATALOGUE_BINDING,
    ClockKind,
    ClockModel,
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    SemanticCarrier,
    SignalRole,
)


def test_report_flags_cyclic_array_without_amplitude_signal() -> None:
    """A multi-element cyclic array without an amplitude signal draws the advisory."""
    channel = derived_channel(
        signals=tuple(
            signal
            for signal in SIGNALS_CH_LINER_ASYMMETRY_SET
            if signal.role is not SignalRole.AMPLITUDE
        )
    )
    plan = plan_with(
        channels=tuple(
            channel if entry.identifier == channel.identifier else entry
            for entry in synthetic_plan().channels
        )
    )
    findings = plan.consistency_report()
    assert len(findings) == 1
    assert "amplitude" in findings[0].message


def test_report_flags_mhd_band_outside_typical_range() -> None:
    """A band outside the device-typical scale draws the advisory."""
    channel = derived_channel(sample_rate_hz=1.0e11, max_signal_frequency_hz=5.0e10)
    plan = DiagnosticPlan(
        identifier="maglif_reference_plan",
        binding=CATALOGUE_BINDING,
        clocks=(clock_facility(), clock_shot(), clock_simulation()),
        frames=REFERENCE_FRAMES,
        clock_relations=CLOCK_RELATIONS,
        frame_transformations=REFERENCE_TRANSFORMATIONS,
        clock_topology=CLOCK_TOPOLOGY,
        channels=(
            channel_noncyclic_one(),
            channel_event_train(),
            channel,
            channel_oscillator(),
        ),
        deferrals=(),
    )
    findings = plan.consistency_report()
    assert len(findings) == 1
    assert "Slutz" in findings[0].message


def test_report_flags_coarse_transient_timing() -> None:
    """A timing bound above the device ceiling draws the advisory."""
    channel = DiagnosticChannelPlan(
        identifier="ch_liner_arrival_train",
        candidate_id="magneto_inertial.driver_arrival",
        carrier=SemanticCarrier.EVENT_CYCLE,
        clock_identifier="clk_shot",
        sample_rate_hz=1.0e09,
        max_signal_frequency_hz=0.0,
        timing_uncertainty_s=1.0e-03,
        acquisition_start_s=0.0,
        acquisition_duration_s=2e-07,
        element_count=1,
        evidence_bindings=dict(EVENT_BINDINGS),
        signals=SIGNALS_CH_LINER_ARRIVAL_TRAIN,
        synthetic=True,
    )
    plan = DiagnosticPlan(
        identifier="maglif_reference_plan",
        binding=CATALOGUE_BINDING,
        clocks=(clock_facility(), clock_shot(), clock_simulation()),
        frames=REFERENCE_FRAMES,
        clock_relations=CLOCK_RELATIONS,
        frame_transformations=REFERENCE_TRANSFORMATIONS,
        clock_topology=CLOCK_TOPOLOGY,
        channels=(
            channel_noncyclic_one(),
            channel,
            channel_derived(),
            channel_oscillator(),
        ),
        deferrals=(),
    )
    findings = plan.consistency_report()
    assert len(findings) == 1
    assert "Slutz" in findings[0].message


def test_report_flags_clock_coarser_than_sampling() -> None:
    """A clock that cannot separate samples draws the advisory."""
    clock = ClockModel(
        identifier="clk_shot",
        kind=ClockKind.SHOT_EVENT_EPOCH,
        epoch="pulsed-power store trigger t0",
        resolution_s=1.0e-2,
        uncertainty_s=1.0e-6,
    )
    channel = DiagnosticChannelPlan(
        identifier="ch_compression_trajectory_set",
        candidate_id="magneto_inertial.translation_and_compression",
        carrier=SemanticCarrier.BOUNDED_FEATURE,
        clock_identifier="clk_shot",
        sample_rate_hz=1.0e08,
        max_signal_frequency_hz=0.0,
        timing_uncertainty_s=None,
        acquisition_start_s=0.0,
        acquisition_duration_s=2e-07,
        element_count=1,
        evidence_bindings=dict(NONCYCLIC_BINDINGS),
        signals=SIGNALS_CH_COMPRESSION_TRAJECTORY_SET,
        synthetic=True,
    )
    plan = DiagnosticPlan(
        identifier="maglif_partial_plan",
        binding=CATALOGUE_BINDING,
        clocks=(clock_facility(), clock, clock_simulation()),
        frames=REFERENCE_FRAMES,
        clock_relations=CLOCK_RELATIONS,
        frame_transformations=REFERENCE_TRANSFORMATIONS,
        clock_topology=CLOCK_TOPOLOGY,
        channels=(
            channel,
            channel_derived(),
            channel_oscillator(),
        ),
        deferrals=(
            DeferredCandidate(
                candidate_id="magneto_inertial.driver_arrival",
                reason="arrival train deferred pending event fixtures",
            ),
        ),
    )
    findings = plan.consistency_report()
    assert len(findings) == 1
    assert "cannot distinguish" in findings[0].message


def test_report_flags_window_beyond_device_ceiling() -> None:
    """An acquisition window beyond the device scale draws the advisory."""
    channel = derived_channel(acquisition_duration_s=9.999999999999999e-06)
    plan = synthetic_plan()
    plan = DiagnosticPlan(
        identifier=plan.identifier,
        binding=plan.binding,
        clocks=plan.clocks,
        frames=plan.frames,
        clock_relations=plan.clock_relations,
        frame_transformations=REFERENCE_TRANSFORMATIONS,
        clock_topology=CLOCK_TOPOLOGY,
        channels=tuple(
            channel if entry.identifier == channel.identifier else entry
            for entry in plan.channels
        ),
        deferrals=plan.deferrals,
    )
    findings = plan.consistency_report()
    assert len(findings) == 1
    assert "acquisition window" in findings[0].message


def test_report_flags_array_size_outside_common_range() -> None:
    """A two-element array below the common range draws the advisory."""
    channel = derived_channel(element_count=2)
    plan = synthetic_plan()
    plan = DiagnosticPlan(
        identifier=plan.identifier,
        binding=plan.binding,
        clocks=plan.clocks,
        frames=plan.frames,
        clock_relations=plan.clock_relations,
        frame_transformations=REFERENCE_TRANSFORMATIONS,
        clock_topology=CLOCK_TOPOLOGY,
        channels=tuple(
            channel if entry.identifier == channel.identifier else entry
            for entry in plan.channels
        ),
        deferrals=plan.deferrals,
    )
    findings = plan.consistency_report()
    assert len(findings) == 1
    assert "array size" in findings[0].message
