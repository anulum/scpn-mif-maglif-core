<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF MagLIF Core — device model contract
-->

# Device model contract

What a consumer of this repository's device models may rely on, written
from the code rather than from a template. Design record:
`docs/adr/0006-device-3d-and-cad-models.md`.

## The two tiers

| Tier | Record | Schema | Built from |
|---|---|---|---|
| G1, tessellated | `DeviceModel3D` | `scpn.maglif-3d-model.v1` 1.0.0 | the library's `geometry` group |
| G2, B-rep | `DeviceModelCAD` | `scpn.maglif-cad-model.v1` 1.0.0 | the library's `cad` group |

Both are built from the same validated `DeviceConfiguration` and
`DeviceGeometry` and describe the same five bodies. Tier G2 is optional:
it needs the `cad` extra, and every other capability of this package works
without a B-rep back-end.

## Units and frame

| Quantity | Value |
|---|---|
| length | metre |
| handedness | right |
| axis | `z` along the axis of the liner and of the coil pair |
| origin | `z = 0` at the midplane of the liner |

The **records** are in metres. The **declarations** are in millimetres,
because that is the scale this family's hardware is specified at, and the
field names carry the unit.

## The bodies, in this order

| Name | Role | Material token |
|---|---|---|
| `fuel_column` | `fuel` | `fuel_gas` |
| `liner_shell` | `liner` | `liner_metal` |
| `laser_entrance_window` | `window` | `window_foil` |
| `magnetising_coil_upstream` | `coil` | `coil_conductor` |
| `magnetising_coil_downstream` | `coil` | `coil_conductor` |

The body set follows the three stages the family is named for: the fuel
the laser preheats, the liner that implodes onto it, the foil the laser
enters through, and the coils that magnetise the fuel before either
happens. The order is fixed and checked at construction on both tiers.

## Where each dimension comes from

The configuration owns the liner's outer radius, wall thickness and
length, and the drive's peak current, axial field and preheat energy. The
geometry owns the entrance window's thickness and the coil pair's bore,
winding thickness, length and separation.

Two relations between them are checked before any body is built:

- the coil bore must exceed the liner's outer radius, or the coils do not
  clear the liner;
- the coil separation must exceed the coil length, or the pair overlaps
  itself.

Each is refused in the direction it is wrong, naming both fields and their
values. Nothing is clamped.

## The Helmholtz ratio

The filed chapter calls the pair "Helmholtz-**like**". A true Helmholtz
pair is separated by exactly one coil radius. The geometry reports
`helmholtz_ratio = s / R`, which is one at that condition, and **never
enforces it**. Turning a qualified word in a source into a hard invariant
would be inventing a constraint the source did not state.

## Exports and identity

Both records serialise canonically (sorted keys, minimal separators, a
trailing newline, NaN and infinity refused) and carry a SHA-256 digest of
those bytes. Each binds the digests of the configuration and the geometry
it was built from. Tier G2 additionally carries normalised STEP bytes with
their own digest and the versions of the pinned back-ends.

## Declared limits

- **STEP determinism is claimed inside one pinned back-end environment
  only**, never across back-end versions. The record carries the versions.
- The faceting comparison runs at a linear deflection of `1e-5 m` and an
  angular deflection of `0.1 rad`, against an 8-segment tier-G1 reference.
  **That deflection is set from this family's scale and not copied**: a
  MagLIF bore is millimetres where the liner family's is centimetres, and
  the deficit bound is `2 d / r`, so the coarser `1e-4` would make the
  guarantee ten per cent on a body this small. A test asserts every body's
  bound stays under two per cent.
- The evidence kernel **refuses** a body that misses its bound, naming the
  body.

## Non-claims

- The geometry is the state **before** the implosion. No body moves; no
  trajectory, deformation or instability is modelled.
- The coils are a pair of rings of declared size. No winding, turn count,
  circuit or field map is modelled — a pair of rings in a static model is
  not a magnet.
- No body is an engineering model; no material property, load, field,
  neutronic quantity or fabrication tolerance is carried.
- No value describes or validates any real machine. Where a record
  reproduces a dimension a filed source prints, that is an anchor on the
  geometry and nothing further.
