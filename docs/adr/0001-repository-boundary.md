<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF MagLIF Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. The `magneto_inertial` registry
family spans four liner classes with different liner materials and
timescales (MagLIF solid liner, plasma-jet liner, mechanical/liquid liner,
and the FRC-compression scheme owned by the existing `SCPN-MIF-CORE`); a
boundary decision was needed on this partition and on MagLIF's Z-pinch and
laser edges.

## Decision

1. `SCPN-MIF-MAGLIF-CORE` owns exactly one registry configuration:
   `maglif` (magnetized cylindrical liner).
2. The repository owns device-level truth only: three-stage coupling
   configuration policy (premagnetisation, laser preheat, pulsed-power
   liner implosion, with stage timing as a first-class facet), pulsed
   lifecycle semantics with liner-instability and window-failure hazard
   records, liner/flux-compression/burn diagnostic and clock
   declarations, actuator-response model boundaries, the safety-envelope
   declaration, and the device-owned CONTROL adapter specification.
3. Unlined Z-pinch physics stays with `SCPN-Z-PINCH-CORE`; the preheat
   laser does not make this a laser-ICF device (the implosion driver is
   pulsed-power on a solid liner); plasma-jet and mechanical/liquid
   liners have their own owners on different liner physics and
   timescales; the FRC-compression MIF workflow remains with
   `SCPN-MIF-CORE`.
4. Solver mathematics remains in `SCPN-FUSION-CORE` until an exact surface
   passes the family migration gate. No solver code is copied here.
5. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
6. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **One repository for all magneto-inertial liner schemes**: rejected —
  liner material and implosion timescale drive the physics apart: a solid
  conducting liner on nanosecond pulsed power (MagLIF), merging plasma
  jets (PJMIF), and mechanical/liquid liners on much slower timescales
  share only the flux-compression idea; drivers, lifecycle, and hazard
  structure differ (surfaces 2–4).
- **Folding MagLIF into the Z-pinch repository** (shared pulsed-power
  heritage): rejected — the imploding object is a fuel-bearing magnetised
  liner with staged preheat, not a plasma column; the three-stage
  coupling contract has no Z-pinch counterpart.
- **Absorbing solver code at scaffold time**: rejected — violates the
  migration gate.

## Consequences

- Downstream consumers get one stable identity for the MagLIF
  configuration and a manifest to bind against.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future
  ADR records any such change here.
