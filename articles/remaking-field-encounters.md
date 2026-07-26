---
title: Remaking field encounters
date: 2026-07-26
summary: Vanilla Danger / StepID behavior, and the RCnt2 FORCE stub that replaces Danger growth in FIELD.BIN.
order: 2
---

# Remaking field encounters

Goal: field encounters that feel less deterministic, while keeping preempt routing and Enemy Lure / Away.

Makou can edit per-map encounter tables in `.DAT`. Danger growth is in `FIELD.BIN`. That is what this mod patches.

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

## Locating the patch

`FIELD.BIN` on disc is GZIPPS-compressed. Decompress before searching (`scripts/decompress_field_bin.py`). US disc 1 ≈ **85435 → 264008** bytes. Module load base: **`0x800A0000`** (Ghidra / DuckStation aligned). RNG table at file `0x40638` → VA **`0x800E0638`**.

| Symbol | VA |
|--------|-----|
| `increment_step_id` | `0x800AB9C8` |
| `increment_formation` | `0x800ABA34` |
| `encounter_check` | `0x800ABA70` |

Danger accumulation is **`0x800ABB7C`–`0x800ABBD0`** (88 bytes), then `jal increment_step_id` at **`0x800ABBD4`**. Patch in place; do not overwrite that `jal`. `0x800E0700` is RNG table data, not a code cave.

`g_enemy_lure` is read in FIELD; writers live elsewhere. FORCE + lure still interact with Away / Lure.

## Stub design

### Failed: COP0 Count

First stub used `mfc0` Count. PS1 R3000A COP0 r9 is **BDAM**, usually 0 → every check FORCEd Danger to `0xFFFF`. Unusable.

### Shipped: RCnt2

Entropy from root counter **RCnt2** (`0x1F801120`). Low byte vs lure-derived threshold; store `0` or `0xFFFF` to Danger. Keep both `jal increment_step_id` calls.

```
thresh   = (g_enemy_lure * 3) / 4
g_danger = ((RCnt2 & 0xff) < thresh) ? 0xFFFF : 0
```

`* 3/4` after raw `lure/256` felt too dense at default lure. RAM pokes: lure `1` ≈ none, `16` ≈ normal, `64` ≈ high. Playtests: sparse checks, Offset still advances on StepID wrap, preempt flag `0x800716D0` still 4↔0.

File offset for the stub: **`0xBB7C`**.

## Packaging

1. Pristine NTSC-U disc (or Makou-saved disc if map edits are included).
2. Extract `FIELD/FIELD.BIN` from that image.
3. `python scripts/build_field_encounter_patch.py …` → `FIELD.BIN.new`.
4. Import over `FIELD/FIELD.BIN` (pad if shorter; never truncate).
5. DuckStation smoke test.
6. `scripts/make_ppf.py` pristine → final.

Drop the `.ppf` into `site/encounter/patches/` and wire `PATCHES`. Until then the patcher page is an empty scaffold. Full author steps: `docs/06-packaging-combined-ppf.md`.

## Out of scope

- Per-map battle IDs / weights (unless a later Makou pass)
- `WORLD.BIN` encounters
- Field script RNG (separate from encounter RNG)
- Changing preempt logic (StepID calls must still run)

## Status

| Item | State |
|------|--------|
| RCnt2 FORCE stub | Playtested |
| Packaging docs | Written |
| Public Disc 1 `.ppf` | Not published yet |
| In-story boss preempt check | Open |
| `WORLD.BIN` | Later |
