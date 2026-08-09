# Fanfare Skip vs train + post–Carry Armor / sub fields

**Date:** 2026-08-09  
**Mod:** fanfare-skip v0.1.3  
**Method:** pristine Disc 1/2 field script scan + BATTLE.X site review (not console)

## Mod behaviour (v0.1.3)

1. Force battle-mode **bit 0x20** (no victory music) wherever BATTLE.X tests it.
2. At file **0x2A08**, always take the existing "already done" branch so the
   victory anim + fanfare-id queue does not run.
3. Does **not** force: timed (0x02), no-escape (0x08), no-reward-UI (0x80),
   BTMD2 no-pose (0x100).

## Train fields (Midgar defense)

| Field | BTLMD | Bits | Notes |
|-------|-------|------|--------|
| NMKIN_1..5 | 0x0022 | noMusic + **timed** | Classic train win |
| SMKIN_4 | 0x0022 | noMusic + timed | |
| SMKIN_5 | (battle 324) | music set only | scripted fight |
| TRNAD_4 | 0x0008 | **noEscape** | discver battle 743 |

### Interaction

- **noMusic already on** for NMKIN/SMKIN_4 — forcing 0x20 is a no-op (safe).
- **timed (0x02) untouched** — timer / train exit logic still in BATTLE.X
  at the 0x02 check (e.g. around 0x3E6B0); our sites only OR 0x20.
- **0x2A08 skip** matches the stock path when the actor "already queued"
  flag is set — train fights that already skip the ceremony take that
  path; we force it for every fight. Should not re-enable fanfare/poses.
- **TRNAD_4 noEscape** — independent bit; still works.

**Verdict:** Train battles should stay train-like (or cleaner). Low risk of
regressing Midgar train sequencing.

## Underwater reactor / sub boarding (Carry Armor neighbourhood)

Scripted battle modes found on pristine:

| Field | Mode / battle | Bits |
|-------|----------------|------|
| UJUNON2 | BTLMD 0x0008, BATTLE 480 | noEscape |
| JUNONE2 | BTLMD 0x0020 | noMusic only |
| SUBIN_1A | BATTLE 786 | (no BTLMD) |
| SUBIN_1B | BATTLE 786 | |
| SUBIN_2A | BATTLE 784 | |
| SUBIN_2B | BATTLE 785 | |

Carry Armor itself is often an encounter-table boss on the underwater path
rather than a unique field opcode pattern; the fields above are the
story/map neighbourhood after that stretch through boarding the sub.

### Interaction

- **UJUNON2 noEscape** — only 0x08; our global 0x20 + pose-queue skip apply
  on top. Boss should still be no-escape; win should be silent/no poses.
- **JUNONE2** already noMusic — redundant with our force.
- **SUBIN_*** scripted fights have **no special win flags** — they get the
  full mod (music off + pose queue skipped). Expected for "normal" wins
  after boarding.

**Verdict:** No field flag conflicts with the mod. Sub interiors do not rely
on timed-exit win like the train.

## Residual risks (need hardware / DuckStation)

1. If Carry Armor or a sub fight uses a **unique end sequence** that does
   not go through 0x2A08 / bit 0x20 checks, poses could remain there only.
2. Timed train: if anything still waits, it is more likely the **field
   timer / multi-battle chain**, not fanfare — report if stuck.
3. v0.1.1–0.1.2 **0x100** force is gone in 0.1.3 (UI glitches); verify
   confirm / context bar feel normal on these fights.

## Playtest checklist

- [ ] Midgar train fights: still auto-cut after win; no stuck timer weirdness
- [ ] Underwater reactor / Carry Armor: no escape still; win has no fanfare/poses
- [ ] First fights after boarding sub (SUBIN_*): clean exit, rewards OK
- [ ] Confirm button / battle context menu not auto-firing after win
