<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF MagLIF Core — Architecture summary
-->

# Architecture summary

`SCPN-MIF-MAGLIF-CORE` is the device-family owner for magnetised liner
inertial fusion systems inside the SCPN Reactor Systems Research Group. The
repository is currently `architecture_only`: it defines the device
boundary, its ecosystem contracts, and the validation tooling that enforces
both, and it implements no reactor capability.

The authoritative architecture record is
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). The ownership decision and
its consequences are fixed in
[`docs/adr/0001-repository-boundary.md`](docs/adr/0001-repository-boundary.md).

Boundary in one paragraph: this repository owns MagLIF plant and experiment
truth — configuration policy for the three-stage magneto-inertial scheme
(axial premagnetisation, laser preheat, pulsed-power liner implosion with
flux compression), pulsed lifecycle semantics with
magneto-Rayleigh–Taylor, window-failure and mistiming hazard records,
stage-spanning diagnostic and clock declarations anchored on bang time,
actuator-response boundaries limited to shot-to-shot stage programming,
safety-envelope declarations, and the device-owned CONTROL adapter
specification. Unlined Z-pinches stay with `SCPN-Z-PINCH-CORE`; plasma-jet
and mechanical/liquid liners with their own owners; the FRC-compression
workflow with `SCPN-MIF-CORE`; solver mathematics in `SCPN-FUSION-CORE`;
typed semantics in `SCPN-PHASE-ORCHESTRATOR` (review-only); admitted
control actions are formed only by `SCPN-CONTROL`; independent machine
protection keeps the final veto; portfolio presentation belongs to
`SCPN-STUDIO`, towards which this project is `not_federated`.
