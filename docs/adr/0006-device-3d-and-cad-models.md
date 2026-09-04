<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF MagLIF Core — ADR 0006
-->

# ADR 0006 — Device 3D and CAD models, one body per stage

Status: accepted (2026-09-04). Adds the fourth and fifth implemented
capabilities, `device_3d_model` and `device_cad_model`, at
`computational_prototype`.

## Context

The repository had a configuration model, diagnostic semantics and level-0
physics, and no geometry. The filed chapter dimensions the target
completely and names, without dimensioning, what surrounds it:
"Helmholtz-like coils" apply the axial field and "a thin plastic foil" is
what the laser enters through.

## Decision

1. **Five bodies, and the set follows the three stages.** The fuel column
   the laser preheats, the liner that implodes onto it, the foil the laser
   enters through, and the pair of coils that magnetise the fuel before
   either happens. A MagLIF model with only a liner would draw the
   implosion stage and omit the two that make the family what it is.

2. **No library increment.** Every body is a cylinder or an annular tube
   about `z`.

3. **"Helmholtz-like" is taken at its word.** A true Helmholtz pair is
   separated by exactly one coil radius. The source says *like*, not *is*,
   so the model **reports** the ratio — one at the condition — and never
   imposes it. The anchor fixture declares a pair at the condition and a
   test asserts the ratio is exactly one; the synthetic reference sits
   away from it deliberately and is accepted just the same. Turning a
   qualified word in a source into a hard invariant would be inventing a
   constraint the source did not state.

4. **The deflection is set from the scale, not copied.** A MagLIF bore is
   two millimetres where the liner family's is two hundred, and the
   faceting deficit bound is `2 d / r`. Keeping the liner family's
   `1e-4` would make the guarantee ten per cent on a body this small, so
   the default here is `1e-5` and the record says why.

   The cost of that choice was measured rather than assumed: one build
   takes about ten seconds against about five at the coarser deflection.
   The test module therefore builds the reference **once** and caches it,
   which is where the real cost was — building per test cost minutes for
   no added evidence.

5. **Two things a coil pair in a static model could be over-read as** are
   refused in the record's own non-claims: the geometry is the state
   before the implosion, and the coils are rings of declared size with no
   winding, turn count, circuit or field map behind them.

6. **The envelope refuses two collisions**, each naming both fields: a
   coil bore that does not clear the liner, and a pair whose coils are
   longer than their separation and would overlap.

7. **Anchoring.** The liner's outer radius, wall and length are the
   printed ones and are proven recoverable from the built bodies. The
   window and the coils are declared, because the chapter names them
   without dimensioning them, and they are said to be declared.

   The cross-capability test the liner family introduced is carried here
   too: the tier-G1 liner volume divided by the physics capability's liner
   mass over its density is exactly the inscribed-polygon ratio of the
   segment count.

## Consequences

The family has a device model at both tiers whose body set is the three
stages it is named for. Nothing here is an engineering model or a
statement about a real machine.
