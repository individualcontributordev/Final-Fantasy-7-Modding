# Patch log: FORCE encounter stub (in-place Danger+=)

**Date:** 2026-07-25  
**File:** `FIELD.BIN.dec`  
**VA base:** `0x800A0000`

## Change

Replace vanilla Danger `+=` at `0x800ABB7C`–`0x800ABBD3` (88 bytes) with lure-scaled FORCE stub using COP0 Count. Keep dual `jal increment_step_id`.

| VA | File offset | Notes |
|----|-------------|-------|
| `0x800ABB7C` | `0xBB7C` | stub start |
| `0x800ABBD4` | `0xBBD4` | `jal increment_step_id` (must remain) |

## New bytes @ `0xBB7C` (88 bytes LE)

```
00 48 02 40 06 80 01 3c 19 2f 23 90 ff 00 42 30
2b 10 43 00 23 10 02 00 07 80 01 3c 3c 17 22 a4
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00
```

## Behavior

`g_danger = ((Count & 0xff) < g_enemy_lure) ? 0xFFFF : 0` each encounter check.
