---
title: Remaking field encounters
date: 2026-07-26
summary: How vanilla Danger and StepID work on PS1 Final Fantasy VII, why Makou alone cannot fix the feel, and how an 88-byte RCnt2 FORCE stub in FIELD.BIN restores sparse, lure-scaled battles.
order: 2
---

# Remaking field encounters

Walk Midgar long enough and the field starts to feel like a metronome: Danger climbs on a schedule, StepID ticks a fixed tape, and “random” battles stop surprising anyone who has watched the counters. Speedrunners already map that tape. This mod aims at something quieter — field encounters that feel like chance again, without throwing away preempt routing or Enemy Lure / Away.

What follows is the public account of that work: how the vanilla loop is wired, where we patched it, which dead ends taught us something, and how the change becomes a disc image other people can apply.

## The vanilla loop (what we are rewriting)

On a hostile field with encounters enabled, the field engine does not roll a battle every frame. Roughly every eight movement frames it advances a **step fraction** by 32. When that byte wraps:

1. **Danger** grows by a formula involving field scale, walk vs run, and the map’s encounter rate (lower rate bytes mean *more* battles — inverse intuition left over from the designers).
2. The engine calls **`increment_step_id`** twice — first for the preempt roll, then for the danger-threshold roll.
3. If Danger clears the lure-scaled threshold, a battle starts, Danger resets, and a separate **formation** counter picks the enemy set.

`increment_step_id` is a tiny tape machine: StepID increments; on wrap, Offset gains 13; the return value is `RNG_TABLE[stepid] - offset` (byte arithmetic). Formation has its own counter into the same 256-byte table. That table sits in the field module; the first bytes match the well-known sequence from the speedrun wiki (`B1 CA EE 6C…`).

Important RAM (PS1, US field context):

| Name | Address | Role |
|------|---------|------|
| Danger | `0x8007173C` | 16-bit accumulator toward a fight |
| Formation | `0x80071C20` | which enemy set comes next |
| StepID / Offset | `0x8009C540` / `0x8009AD2C` | encounter RNG tape |
| Step fraction | `0x8009C6D8` | wraps to trigger a check |
| Enemy lure byte | `0x80062F19` | scales the threshold (`(Danger * lure) >> 12`) |

Makou can edit per-map encounter *tables* and rates inside `.DAT` files. It cannot change the engine’s Danger `+=` block. That is why a “make encounters feel random” goal ends in **`FIELD.BIN`**, not in a map editor alone.

## Finding the right code

`FIELD.BIN` on disc is GZIPPS-compressed. Searching the compressed blob for known addresses is a reliable way to get zero hits and a false sense that the wiki is wrong. Decompress first (`scripts/decompress_field_bin.py`): stock US disc 1 goes roughly **85435 → 264008** bytes. The RNG table lands at file offset `0x40638`, which is VA **`0x800E0638`** once the module is loaded at **`0x800A0000`** — the base we aligned between Ghidra and DuckStation.

With that base, the functions rename themselves through xrefs:

- **`increment_step_id`** @ `0x800AB9C8`
- **`increment_formation`** @ `0x800ABA34`
- **`encounter_check`** @ `0x800ABA70` (easy to mis-split; do not treat the mid-function `jal` at `0x800ABBD4` as an entry point)

Inside `encounter_check`, Danger accumulation occupies a tight window: roughly **`0x800ABB7C`–`0x800ABBD0`**, then the first `jal increment_step_id` at **`0x800ABBD4`**. That 88-byte window is the entire patch surface. No code cave required — and the tempting “empty” region near `0x800E0700` is not empty; it is the tail of the RNG table.

Downstream, the threshold path still reads **`g_enemy_lure`** and multiplies it with Danger. Writers for that byte live elsewhere in the game; FIELD only consumes it. That detail mattered: if we FORCE Danger to `0xFFFF` on a check, lure still decides whether the roll fires, and Away / Lure materia keep a job.

## What we almost shipped (and why it failed)

### COP0 Count is not entropy on PS1

The first stub used `mfc0` from **Count**. On R4000 that register is a timer. On the PlayStation’s R3000A, COP0 register 9 is **BDAM**, typically zero. `(0 < g_enemy_lure)` is almost always true → every check FORCEs Danger to `65535` → a fight on every StepID pair. Boots fine; Midgar becomes a hallway of battles. Playtest made the bug obvious in under a minute.

### Always-FORCE is the wrong fantasy

Even with real entropy, “Danger = MAX every check” removes the texture of sparse checks. We wanted *some* checks to leave Danger at zero so the tape still advances without a fight — sparse samples, Offset still wrapping 0→13 after StepID overflow, preempt flag still flicking **4↔0** at `0x800716D0`.

### Entropy that actually moves: RCnt2

System root counter **RCnt2** at **`0x1F801120`** changes while the field runs. The stub loads it, keeps the low byte, compares against a lure-derived threshold, and stores either `0` or `0xFFFF` into Danger — branchless, in place, twelve nops padding out to the surviving `jal`.

Shipped behavior (after a density pass):

```
thresh  = (g_enemy_lure * 3) / 4
g_danger = ((RCnt2 & 0xff) < thresh) ? 0xFFFF : 0
```

Raw `lure/256` worked in RAM pokes (`1` ≈ none, `16` ≈ normal, `64` ≈ a lot) but felt dense at default lure; scaling by three-quarters eased that without abandoning lure. Dual `jal increment_step_id` stays intact — once we learned the hard way that overrunning the selection by four bytes turns the first `jal` into a `nop` and breaks the tape.

## Building the disc image

Authors use the shared packaging path documented in the repo (`docs/06-packaging-combined-ppf.md` for the full checklist):

1. Start from a pristine NTSC-U disc (or a Makou-saved disc if map edits are part of the release).
2. Extract **`FIELD/FIELD.BIN`** from *that* image.
3. `python scripts/build_field_encounter_patch.py …` — decompress, apply the RCnt2 stub at file offset **`0xBB7C`**, recompress to `FIELD.BIN.new`.
4. Import over **`FIELD/FIELD.BIN`** in CDmage (or equivalent). Pad if shorter; **never** accept truncate.
5. Smoke in DuckStation: title → field → walk → fights feel sparse; optional memory watch on Danger, StepID, preempt.
6. Diff pristine vs final with `scripts/make_ppf.py` into a single Disc 1 `.ppf`.

Players only see step 6’s output in the [Encounter patcher](../encounter/) once the `.ppf` is dropped into `site/encounter/patches/` and wired into `PATCHES`. Until that file exists, the page is an empty scaffold on purpose — the research is ahead of the published blob.

## What this mod does *not* change

- Per-map battle IDs and weights in `.DAT` (still vanilla unless a future release pairs Makou edits).
- World-map encounters in **`WORLD.BIN`** (explicit follow-up).
- Field *script* RNG (Makou’s `RANDOM` opcode family) — different counters entirely.
- The preempt mechanism itself; we only insist the StepID calls still run so story bosses that lean on that routing keep a chance to behave.

## Status

| Item | State |
|------|--------|
| RCnt2 FORCE stub in `FIELD.BIN` | Playtested (sparse checks, lure poke scaling, preempt flag) |
| Combined Makou + stub packaging docs | Written |
| Public Disc 1 `.ppf` on the site | Not dropped in yet — scaffold waits |
| Boss preempt confirmation in-story | Open |
| `WORLD.BIN` parity | Later |

The publishing article describes how the next mods will reuse this path. This one is the proof that an 88-byte window, the wrong COP0 register, and a truncate dialog can still become something worth walking Midgar for again.
