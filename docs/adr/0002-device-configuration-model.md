<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF MagLIF Core — ADR 0002: device configuration model
-->

# ADR 0002 — Device configuration model and evidence-maturity semantics

**Status:** accepted (2026-08-31)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The repository was established architecture-only (ADR 0001). The first
capability lane is the device configuration model for the single
registry configuration this repository owns (`maglif`). The claim
boundary and repository-level `evidence_maturity` semantics follow the
family pilot.

## Decision

1. The package `scpn_mif_maglif_core` implements the device
   configuration model as frozen, strictly typed value objects: the
   metal liner (outer radius, wall thickness, length) and the
   three-stage drive (peak current, axial premagnetisation field,
   laser-preheat energy).
2. Claim boundary — identical to the family pilot: internal-consistency
   validation, cited textbook estimates with documented bounds,
   canonical serialisation with SHA-256 digest, and the data-only SPO
   registry pin. No claim about any real machine; every exercised
   parameter set is a synthetic test fixture.
3. Hard invariants: the wall thickness is strictly smaller than the
   outer radius, and both the axial premagnetisation field and the
   laser-preheat energy are strictly positive — premagnetisation and
   preheat are the two stages that define magnetised liner inertial
   fusion (S. A. Slutz et al., Phys. Plasmas 17 (2010) 056303).
4. Derived quantity: the liner aspect ratio ``AR = R / dR``. Advisory
   finding, reported by `consistency_report()` and never clamped: an
   aspect ratio outside the documented ``[3, 9]`` window around the
   baseline design point (Slutz et al. 2010, baseline AR = 6).
5. Repository-level `evidence_maturity` = the highest state claimed by
   any capability entry; per-capability states are the authoritative
   claim surface.
6. Everything else is unchanged: review-only/non-actionable SPO
   profile, no adapter implementation, empty solver seams,
   `not_federated` Studio state, independent machine-protection veto,
   all non-claims.

## Consequences

- The Studio descriptor's `capabilities` array carries its first item
  (schema 1.1.0 data change only).
- The reactor-domain validator gains the populated-capabilities branch
  with the ceiling rule.
- Later lanes (stage/liner/burn diagnostic semantics with the bang-time
  anchor, safety envelope) build on these types; maturity advances per
  capability only with the evidence the family standard requires.
