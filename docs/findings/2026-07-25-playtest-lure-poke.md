# Playtest: g_enemy_lure poke scales FORCE density

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [playtest-rcnt2-sparse](2026-07-25-playtest-rcnt2-sparse.md), [g-enemy-lure](2026-07-25-g-enemy-lure.md)

## Method

Poke byte `g_enemy_lure` @ `0x80062F19` in DuckStation (no materia).

## Result

| Poke | Feel |
|------|------|
| 1 | none |
| 16 | normal |
| 64 | a lot |

Matches stub: `P(FORCE) ≈ lure/256` per encounter check.
