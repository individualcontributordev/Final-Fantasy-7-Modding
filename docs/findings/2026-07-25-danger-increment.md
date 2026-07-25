# Danger increment found above dual RNG jals

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [encounter-check](2026-07-25-encounter-check.md), [g-danger-rename](2026-07-25-g-danger-rename.md)

## Summary

Danger **growth** (`g_danger += …`) is immediately above the first `jal increment_step_id`, still outside Ghidra’s current `encounter_check` (which wrongly starts at `0x800ABBD4`).

## Discovery

Listing (user paste):

| Address | Instruction | Role |
|---------|-------------|------|
| `0x800ABB7C` | `lui at,0x8007` + `addiu …,0x4f14` | table/base for dividend |
| `0x800ABB90` | `div v1,v0` | scale/rate division |
| `0x800ABBB8` | `mflo v1` | quotient |
| `0x800ABBC0` | `lhu v0,offset g_danger(v0)` | load Danger |
| `0x800ABBC8` | `addu v0,v0,v1` | **Danger += quotient** |
| `0x800ABBD0` | `sh v0,offset g_danger(at)` | store Danger |
| `0x800ABBD4` | `jal increment_step_id` | preempt roll (current wrong fn entry) |

Matches wiki: Danger grows, then two RNG rolls.

## Follow-ups

- [ ] True function start is **above** `0x800ABB7C` — recreate `encounter_check` to include Danger add + dual jals
