# Patch target: Danger 0 on field entry; RNG may set Danger MAX per check

**Date:** 2026-07-25  
**Confidence:** likely  
**Status:** open  
**Related:** [encounter-check-entry](2026-07-25-encounter-check-entry.md), [encounter-rng-architecture](2026-07-25-encounter-rng-architecture.md)

## Summary

Mod delta from vanilla (agreed direction):

1. **`g_danger = 0` on field map enter** (vanilla does *not* do this — Danger normally carries across fields until a battle).
2. **Each encounter check** (movement / step-fraction wrap — **not** a wall-clock timer): instead of vanilla `Danger += formula`, make an **RNG call**; with some probability set **`g_danger = MAX`** (or a high constant that always beats the threshold compare).
3. Leave the rest of the check **vanilla**: preempt roll + threshold roll via **StepID/Offset**, formation via **`g_formation`**, battle if Danger meets threshold, Danger → 0 after battle.

## Goals this serves

| Goal | How |
|------|-----|
| Sparse / “may cross several fields with no fight” | Danger stays 0 until a MAX hit; no carry between fields |
| Per-step checks, no timer | Same movement-driven `encounter_check` cadence as vanilla |
| Routable boss preempt | StepID/Offset timeline unchanged; preempt flag still set on the stock tape |
| Less gradual Danger manip | No walk/run Danger slope — only 0 vs MAX |

## Vanilla baseline (for contrast)

On each encounter check today:

1. `Danger +=` deterministic amount (scale / rate / walk vs run)  
2. `increment_step_id` → preempt flag  
3. `increment_step_id` → threshold  
4. If Danger ≥ threshold → battle → Danger = 0  

Danger is **not** cleared on field entry in vanilla.

## Critical implementation detail

The “set Danger to MAX?” roll must use **independent entropy**, **not** StepID/Offset.

**Chosen entropy:** COP0 **`Count`** via `mfc0` in our new stub (FIELD need not already use it). Scale FORCE chance by **`g_enemy_lure`**.

StepID must still **advance** every check (call `increment_step_id` twice as today) so boss preempt routing stays aligned with vanilla tables (e.g. Aps StepID 48 / Offset 26).

## Sketch inside `encounter_check`

```
// existing gates: hostile, encounters on, step fraction wrapped, etc.

// FORCE chance scales with Enemy Lure (DAT_80062f19), same knob vanilla uses
// in: roll < (Danger * lure) >> 12
// Higher lure → more likely to set MAX; Enemy Away → less likely.
if (independent_rng() < force_chance_from_lure(DAT_80062f19)):
    g_danger = DANGER_MAX   // high enough that threshold almost always passes
// else: leave g_danger as-is (0 after field enter / after battle)

// vanilla:
preempt = increment_step_id() ...
threshold_roll = increment_step_id() ...
if (threshold_roll < f(g_danger, lure))
    start_battle()  // then Danger = 0 as vanilla
```

Also hook **field enter** → `g_danger = 0`.

Tune `force_chance_from_lure` so default lure ≈ desired sparsity; Lure materia denser, Away sparser.

## Acceptance (product)

- **N trash fights before/after** a preemptable boss (Aps, etc.) are **fine**.
- Must **not** start a random battle in a way that **overlaps** a scripted boss transition (vanilla already has crash / duplicating-boss pathologies when field→battle transitions collide or when encounters are menu-skipped into scripted fights).
- Boss preempt via StepID/Offset routing must remain possible.

## Tradeoffs / watchouts

- **Boss preempt on hostile fields:** long StepID walks can still roll MAX and insert trash fights — **accepted**. Only care about avoiding **simultaneous** trash + boss battle starts.
- **Walk vs run:** no longer changes Danger slope; walking still burns more checks (and StepID) per distance — still useful for preempt routing, and also more MAX rolls per distance.
- **Formation** stays vanilla-routable unless we add a separate change later.
- **WORLD.BIN** still separate.

## Ghidra hooks

- Field enter Danger = 0: start of map-setup `LAB_800a1dc8` (`0x800A1DC8`) and/or `FUN_800ba534` (`0x800BA534`)
- `encounter_check` @ `0x800ABA70` — **in-place** replace Danger `+=` block `0x800ABB7C`–`0x800ABBD4` (**88 bytes**) with MAX-or-skip RNG; keep `jal increment_step_id`
- Keep dual `jal increment_step_id` and formation path
- Post-battle Danger = 0 already in `field_main_loop` (leave vanilla)

## Follow-ups

- [x] Field-enter: replace DAT_8009fe8c clear in field_map_init @ 0x800BA574
- [x] FORCE if `(Count&0xff) < g_enemy_lure` (tune with shift if needed)
- [x] DANGER_MAX = 0xFFFF (sticky until battle)
- [ ] Choose entropy source (not StepID/Offset)
- [ ] Verify no dual battle start if scripted boss fires while Danger was MAX / mid encounter transition
- [ ] Optional: formation entropy later
- [ ] WORLD.BIN later

## Sources

- Design reset 2026-07-25
- [Field map encounter mechanics](https://ff7speedruns.com/index.php/Field_map_encounter_mechanics)
- [Preemptive Boss Battles](https://ff7speedruns.com/index.php/Preemptive_Boss_Battles)
