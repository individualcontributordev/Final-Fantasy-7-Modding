# Scalar 0x4000 miss for world encounter (sll 14 likely)

**Date:** 2026-07-28  
**Confidence:** likely  
**Related:** [worldrand](2026-07-28-worldrand.md)

## Evidence

Scalar search `0x4000` → many hits, almost all **not** lure×16384:

- `mtc2` / `ctc2` … `0x4000` (GTE)
- `andi` / `ori` bit flags
- User: **no `jal WorldRand`** among those hits

Wiki `× 16384` is a power of two → PS1 code often uses **`sll …, 14`**, not a `0x4000` immediate.

`FUN_800a21b4` appears in both the noisy `0x4000` list and WorldRand’s single-call xrefs — still worth opening, but for the **`jal WorldRand`**, not the `andi 0x4000`s.

## Next

Walk WorldRand xrefs (start: `0x800ABB24`, `0x800A21B4`, `0x800B0250`). At each `jal WorldRand`, read decompiler for Danger += / `sll 14` / compare vs `>>8`.
