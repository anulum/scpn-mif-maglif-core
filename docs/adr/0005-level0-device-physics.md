<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF MagLIF Core — ADR 0005
-->

# ADR 0005 — Level-0 device physics: the three stages, and what stagnation does

Status: accepted (2026-09-04). Adds the third implemented capability,
`level0_device_physics`, at `computational_prototype`, and pins the shared
kernel library for the first time in this repository.

## Context

The repository carried a configuration model and diagnostic semantics and
no physics. The cited source — S. A. Slutz et al., Phys. Plasmas 17 (2010)
056303 — is behind a subscription and is not on file; the ledger says so.
What is on file is a RELATED public chapter, SAND2021-3239B, with Slutz a
co-author.

Reading it settled the question the ledger could not. That chapter prints
a complete MagLIF target — "a 10-mm tall, 5-mm outer diameter, 0.5-mm wall
thickness metal cylinder" — and the operating point of the first
integrated experiment: "a 10 T axial field, 0.5 kJ laser preheat energy
deposited, and 18 MA peak load current". **Every field of both
configuration objects of this repository is among those numbers**, which
is not true of any other family landed so far.

## Decision

1. **Two closed forms, organised by what the family actually is.** MagLIF
   is defined by driving one target three ways in sequence, so the first
   module says what each stage means mechanically: the azimuthal field the
   axial current puts at the liner surface, `mu0 I / 2 pi r`, and its
   pressure; the liner's mass and implosion energy; and the preheat energy
   density in the bore. The second says what the convergence does to the
   magnetised fuel, by axial flux conservation and adiabatic compression.

2. **The liner is measured from the outside in**, because that is how this
   family's configuration declares it — an outer radius and a wall, not a
   bore and a thickness. A wall at or beyond the outer radius leaves no
   bore and is refused.

3. **Three things a reader could over-read are refused in the record's own
   non-claims.** The compressed field is the perfect-conductor limit and
   the compressed temperature the loss-free limit, both upper bounds; and
   the drive field is the vacuum field of an axial current at the liner
   surface, with no circuit, no current distribution and no instability
   modelled.

4. **Why the compression relations are not library kernels.** The shared
   library declares `shared_physics_kernels` as an owned domain and that
   domain is empty, and this is the second family to need the same two
   conservation laws, so the question was asked rather than skipped.

   The answer is that the content is two multiplications and one call into
   a kernel that is already shared. `B_0 r^2` and `r^2` are exact in IEEE
   arithmetic on every platform, so the bit-exactness argument that
   justifies every kernel the library does own does not apply to them —
   and the library's kernel contract would demand a native mirror, parity
   by bit pattern and a benchmark row for two multiplications. That is
   ceremony larger than the content. The part that genuinely needs
   determinism, the non-integer power, already goes through the library's
   transcendental kernel, which is why the library is pinned here at all.

5. **Anchoring.** Every one of the six configuration fields is a printed
   value, and the aspect ratio the two printed liner numbers give is
   **exactly 5.0**: the outer radius is half the printed 5-mm diameter and
   the wall is the printed 0.5 mm, both exactly representable in binary
   and so is their quotient. The anchor test asserts equality, not
   closeness.

   The implosion velocity is printed as a **range**, 70 to 100 kilometres
   per second, so a value is declared from inside it and a separate test
   asserts it is inside. The liner material density is not printed at all
   and is declared.

   The fixture, `VALIDATION.md` and this record all say that the anchor
   reproduces what the **related chapter** prints. Nothing implies the
   2010 paper was read.

## Consequences

The family has a physics capability bounded to two closed forms, on an
operating point every number of which the filed source prints.

Nothing here claims yield, gain, confinement or performance, and no value
describes a real machine. Reproducing a printed number is an anchor on the
arithmetic and nothing further.
