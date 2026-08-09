# Finding: Fanfare Skip 0.1.5 still plays fanfare + poses

**Date:** 2026-08-09
**Status:** confirmed (smoke) / fix open
**Module:** BATTLE.X + BATRES victory phase

## Smoke (0.1.5 clean D1)

| Symptom | Result |
|---------|--------|
| Held tone freeze | **no** (quiet FAN2 removed) |
| Fanfare music | **yes** still heard |
| Win poses | **yes** still shown |
| Loot / exp | OK |

## What 0.1.5 actually does

Only patches victory-queue at file+**0x2974** (`800A2974`) to immediate `jr ra`.
Single static caller: **`jal 800A2974` @ 800ABE4C**.

Stock FAN2.SND left alone (required — zero-body FAN2 freezes SPU).

## Implication

Ceremony audio + poses are **not exclusively** driven by `800A2974`. Need live
post-kill hits for:

1. Whether **800ABE4C** still runs (stub reached vs bypassed)
2. First **music engine** entry (`80015248` AKAO helper and/or `800DCF94` with a0≠-1)
3. Timing vs known BATRES path (`801B0000` → … → `801B0558` clear)

Abandoned approaches (do not revive without new evidence):

- Quiet FAN2.SND body → freeze
- Global force battle-mode bit 0x20 / 0x100 → auto-confirm / wrong end UI

## Next

DuckStation BP pass on official 0.1.5 image (see `docs/INSTRUCTIONS.md`).
