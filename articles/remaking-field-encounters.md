---
title: Remaking field encounters
date: 2026-07-26
summary: Vanilla Danger / StepID behavior, and the RCnt2 FORCE stub that replaces Danger growth in FIELD.BIN.
order: 2
---

# Remaking field encounters

This mod changes how field encounters trigger on NTSC-U Final Fantasy VII. Per-map battle tables can stay vanilla; the change is in the field engine’s Danger accumulation inside `FIELD.BIN`. Preempt routing and Enemy Lure / Away still apply.

## Vanilla behavior

On a hostile field, roughly every eight movement frames the engine adds 32 to **step fraction**. On wrap:

1. **Danger** increases from field scale, walk/run, and map encounter rate (lower rate → more battles).
2. **`increment_step_id`** runs twice — preempt roll, then danger-threshold roll.
3. If Danger clears the lure-scaled threshold, a battle starts, Danger resets, and **formation** picks the enemy set.

`increment_step_id`: StepID += 1; on wrap, Offset += 13; return `RNG_TABLE[stepid] - offset` (byte math). Formation uses the same 256-byte table with its own counter.

| Name | Address | Role |
|------|---------|------|
| Danger | `0x8007173C` | 16-bit battle accumulator |
| Formation | `0x80071C20` | enemy set index |
| StepID / Offset | `0x8009C540` / `0x8009AD2C` | encounter RNG state |
| Step fraction | `0x8009C6D8` | triggers a check on wrap |
| Enemy lure | `0x80062F19` | threshold scale (`(Danger * lure) >> 12`) |

## Locating the code

`FIELD.BIN` on disc is GZIPPS-compressed; search the decompressed image. US disc 1 ≈ **85435 → 264008** bytes. Module load base: **`0x800A0000`**. RNG table at file `0x40638` → VA **`0x800E0638`**.

| Symbol | VA |
|--------|-----|
| `increment_step_id` | `0x800AB9C8` |
| `increment_formation` | `0x800ABA34` |
| `encounter_check` | `0x800ABA70` |

Danger accumulation is **`0x800ABB7C`–`0x800ABBD0`** (88 bytes), then `jal increment_step_id` at **`0x800ABBD4`**. The stub replaces that window in place and must not overwrite the `jal`. `0x800E0700` is RNG table data, not free space.

`g_enemy_lure` is read in FIELD; other modules write it. FORCE still multiplies against lure on the threshold path.

## The stub

### COP0 Count (rejected)

An early version used `mfc0` Count. On PS1 R3000A, COP0 r9 is **BDAM**, usually 0, so every check FORCEd Danger to `0xFFFF`.

### RCnt2 (shipped logic)

Entropy from root counter **RCnt2** (`0x1F801120`). Compare the low byte to a lure-derived threshold; store `0` or `0xFFFF` to Danger. Both `jal increment_step_id` calls remain.

```
thresh   = (g_enemy_lure * 3) / 4
g_danger = ((RCnt2 & 0xff) < thresh) ? 0xFFFF : 0
```

Raw `lure/256` was dense at default lure; `* 3/4` eases that. Observed with lure poked in RAM: `1` ≈ none, `16` ≈ normal, `64` ≈ high. Checks are sparse; Offset still advances when StepID wraps; preempt flag `0x800716D0` still moves 4↔0.

Stub file offset in decompressed `FIELD.BIN`: **`0xBB7C`**.

## Disc packaging

Extract `FIELD/FIELD.BIN` from the working image (after any Makou pass), decompress, apply the stub, recompress, reimport over the same path, then diff pristine vs final into one Disc 1 PPF. See [Publishing Final Fantasy VII PlayStation mods](./publishing-psx-mods.html).

## Unchanged

- Per-map battle IDs / weights (unless a separate Makou edit)
- `WORLD.BIN` encounters
- Field script RNG (separate from encounter RNG)
- Preempt logic itself (StepID calls still run)
