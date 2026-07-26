# Patch log: FORCE encounter stub (in-place Danger+=)

**Date:** 2026-07-25  
**File:** `FIELD.BIN.dec`  
**VA base:** `0x800A0000`  
**Package:** [workspace/patches/2026-07-25-force-stub-rcnt2/](../../workspace/patches/2026-07-25-force-stub-rcnt2/)  
**Packaging:** [docs/06-packaging-combined-ppf.md](../06-packaging-combined-ppf.md)

## Change

Replace vanilla Danger `+=` at `0x800ABB7C`–`0x800ABBD3` (88 bytes) with lure-scaled FORCE stub using **RCnt2** (`0x1F801120`). Keep dual `jal increment_step_id`.

| VA | File offset | Notes |
|----|-------------|-------|
| `0x800ABB7C` | `0xBB7C` | stub start |
| `0x800ABBD4` | `0xBBD4` | `jal increment_step_id` (must remain) |

## Behavior

`thresh = (g_enemy_lure * 3) / 4`  
`g_danger = ((RCnt2 & 0xff) < thresh) ? 0xFFFF : 0`

## New bytes @ `0xBB7C` (88 bytes LE)

See `workspace/patches/2026-07-25-force-stub-rcnt2/stub-bb7c.hex`.

## Revs

1. Initial `mfc0 Count` — invalid on PSX; always FORCE  
2. RCnt2 + raw `lure/256` — worked; default felt dense  
3. RCnt2 + `(lure*3)/4` — slightly fewer encounters  

## Acceptance (FIELD.BIN stub)

- [x] Sparse FORCE (RCnt2)
- [x] Lure poke scales density
- [x] Preempt flag 4↔0
- [ ] Confirm `*3/4` density in play
- [ ] Boss preempt when story allows
- [ ] WORLD.BIN later
