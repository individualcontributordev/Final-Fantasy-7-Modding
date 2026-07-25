# Patch target: random encounters, routable boss preempt

**Date:** 2026-07-25  
**Confidence:** likely  
**Status:** open  
**Related:** [encounter-rng-architecture](2026-07-25-encounter-rng-architecture.md), [encounter-check-entry](2026-07-25-encounter-check-entry.md)

## Summary

Goal (updated): **normal field encounters feel random / not routable**, while **preemptive scripted boss fights stay possible and routable** (same StepID/Offset manip as vanilla). Also keep encounter *rate* feeling reasonable (separate from RNG — tune rate/scale if needed).

## How boss preempt actually works

From [Preemptive Boss Battles](https://ff7speedruns.com/index.php/Preemptive_Boss_Battles):

Some **scripted** bosses (Aps, Jenova•BIRTH, Turks, etc.) become preemptive if you start them while the **Preemptive Flag** is already set.

That flag is set by the normal `encounter_check` preempt roll (`increment_step_id` #1 → `DAT_800716d0`), which is a pure function of **StepID + Offset**. Example: Aps often on StepID 48, Offset 26.

So boss preempt routing **requires a predictable StepID/Offset timeline**. A full field-load reseed of StepID/Offset makes preempt bosses *possible by luck*, but **not routable**.

## Design constraint

| Want | Needs |
|------|--------|
| Routable boss preempt | Keep **StepID / Offset** vanilla (deterministic table) |
| Non-routable normal encounters | Break **when** fights happen and/or **which** formation — without destroying that timeline |

Naive Option A (reseed StepID+Offset on field load) **fails** the boss-preempt goal.

## Preferred approach — Option D (split RNG)

Do **not** reseed StepID/Offset.

In `encounter_check` (and formation path):

1. **Preempt roll** — leave vanilla (`increment_step_id` #1 → flag). Boss routing preserved.
2. **Danger threshold roll** — after vanilla `increment_step_id` #2 (so StepID still advances correctly), **mix entropy into the value used for the Danger compare only** (or into the compare). Timing of random battles becomes unpredictable.
3. **Formation** — mix entropy in `increment_formation` return (or reseed `g_formation` occasionally). Which enemies become unpredictable.
4. **Optional:** reset `g_danger = 0` on field load (pacing only; does not break preempt routing).

Entropy: PS1 root counter / VBlank and/or kernel PRNG (Bone Village precedent).

### Rejected / deferred for this goal

| Option | Why not (for this goal) |
|--------|-------------------------|
| A — Reseed StepID+Offset on field load | Breaks routable boss preempt |
| B — Boot-only reseed | Same issue + weak vs saves |
| C — Replace all `increment_step_id` with PRNG | Breaks preempt routing entirely |

## Ghidra hooks (implementation sketch)

- Preempt path already labeled in `encounter_check` @ `0x800ABA70`
- Danger compare uses second roll vs `g_danger` — patch site near dual `jal increment_step_id`
- Formation: `increment_formation` @ `0x800ABA34`
- Still need field-load site only if we reset Danger (optional)

## Follow-ups

- [ ] Confirm preempt flag (`DAT_800716d0`) is what scripted bosses read
- [ ] Choose exact entropy mix (XOR vs replace compare)
- [ ] Implement danger-roll mix + formation mix caves
- [ ] Playtest: Aps-style preempt still hittable by StepID route; random packs feel unplanned
- [ ] WORLD.BIN later
- [ ] Encounter frequency: separate rate/scale pass if fights feel too dense

## Sources

- Session design discussion 2026-07-25
- [Preemptive Boss Battles](https://ff7speedruns.com/index.php/Preemptive_Boss_Battles)
- [Field map encounter mechanics](https://ff7speedruns.com/index.php/Field_map_encounter_mechanics)
