# Ghidra: 0 xrefs to RNG table

**Date:** 2026-07-25  
**Confidence:** confirmed (expected for this binary)

## Observation

`g_field_rng_table` at `0x80040638` (file `0x40638`) has **0** Ghidra xrefs after default analysis.

## Why

MIPS often builds the address with `lui` + `addiu`/`ori` or indexes via a register. Auto-analysis frequently does **not** create a reference to the table symbol. Empty xref list does **not** mean unused data.

## Next approach

Find code via **RAM scalars** the encounter RNG uses (US):

| Scalar search | Likely hit |
|---------------|------------|
| `0x9c540` | StepID `0x8009C540` |
| `0x9ad2c` | Offset `0x8009AD2C` |
| `0x7173c` | Danger `0x8007173C` |

Or Search → Memory for instruction patterns / Search → For Scalars on low half `0x638` with high `0x8004` nearby (harder by hand).

Prefer StepID scalar first → label `increment_step_id` from that function.
