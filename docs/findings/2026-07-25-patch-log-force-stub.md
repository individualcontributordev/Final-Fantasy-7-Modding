# Patch log: FORCE encounter stub (in-place Danger+=)

**Date:** 2026-07-25  
**File:** `FIELD.BIN.dec`  
**VA base:** `0x800A0000`  
**Package:** [mods/field-random-encounters/patches/](../../mods/field-random-encounters/patches/)  
**Ship:** [builder/WINDOWS-INSTRUCTIONS.md](../../builder/WINDOWS-INSTRUCTIONS.md)

## Change

Replace vanilla Danger `+=` at `0x800ABB7C`–`0x800ABBD3` (88 bytes) with lure-scaled FORCE stub using **RCnt2** (`0x1F801120`). Keep dual `jal increment_step_id`.

| VA | File offset | Notes |
|----|-------------|-------|
| `0x800ABB7C` | `0xBB7C` | stub start |
| `0x800ABBD4` | `0xBBD4` | `jal increment_step_id` (must remain) |

## Behavior (shipped)

`thresh = g_enemy_lure / 2`  
`g_danger = ((RCnt2 & 0xff) < thresh) ? 0xFFFF : 0`  

**P(FORCE) ≈ lure/512** (~3.13% at default lure 16 = **50%** of raw `lure/256`).

## New bytes @ `0xBB7C` (88 bytes LE)

See `mods/field-random-encounters/patches/stub-bb7c.hex`.

## Revs

1. Initial `mfc0 Count` — invalid on PSX; always FORCE  
2. RCnt2 + raw `lure/256` — worked; default ~6.25%/check felt dense  
3. RCnt2 + `(lure*3)/4` — ~4.69%/check (75% of raw)  
4. RCnt2 + `lure/2` — **shipped** ~3.13%/check (50% of raw)  

## Acceptance (FIELD.BIN stub)

- [x] Sparse FORCE (RCnt2)
- [x] Lure poke scales density
- [x] Preempt flag 4↔0
- [x] Rate cut to `/2` after `*3/4` still felt dense
- [ ] Boss preempt when story allows
- [ ] WORLD.BIN later
