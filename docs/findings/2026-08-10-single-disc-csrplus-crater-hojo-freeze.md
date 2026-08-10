# Finding: Single-disc CSR+ freeze entering crater (before Hojo)

**Date:** 2026-08-10
**Status:** inconclusive — freeze cleared after DuckStation restart; not confirmed pack bug
**Stack (operator):** Disc 1 — CSR + CSR+ + Single-disc + Fanfare off + Field encounters Light 25%

## Report

Freeze when entering the crater before the Hojo fight.
Prior solid playtests were single-disc + CSR (no CSR+). CSR+ stacking on single-disc was not fully walked.

## Structural gap (important)

CSR+ scene packs are per retail disc:

| Pack | Disc layer | FIELD files |
|------|------------|-------------|
| aerith-house | 1 | (D1) |
| hojo-fd-manip | 2 only | BLIN66_6, CANON_2, FSHIP_24 |
| cota-fd-manip | 2 only | … |
| endgame-fd-manip | 3 only | … |

A single-disc Disc 1 build only applies layers that have a disc1 URL. So on D1:

- Aerith CSR+ can apply
- Hojo / COTA / endgame CSR+ do not apply (no disc1 layer)

Single-disc core does merge many CSR D2/D3 FIELD maps onto D1 (including CRATER_1/2, BLIN66_6, CANON_2, FSHIP_*), from csr-d2d3-field-merge-on-d1.md. Note there: maps that CSR D2/D3 changed may undo earlier Clean-style freeze trims; playtest.

So crater/Hojo corridor may be CSR D2 field scripts on D1 movie/layout without the CSR+ Makou trims that multi-disc CSR+ would apply on D2.

## Likely freeze classes

1. Field script / movie softlock on CRATER_* or next map (missing D2 FMV, bad Play/jump after merge)
2. Expecting CSR+ trim that never landed on D1 (Hojo pack is D2-only)
3. Less likely: encounter 25% or fanfare (fanfare is battle-end only; fanfare was off)

## Bisect order (DuckStation)

Same save / crater approach each time when possible.

| # | Stack | Expect |
|---|--------|--------|
| A | CSR + Single-disc only (no CSR+, default encounters) | If OK then CSR+ or rate involved |
| B | CSR + Single-disc + CSR+ (default enc) | If freeze then CSR+ / missing D2 packs on D1 |
| C | Full failing stack | Confirm |

Note exact field name at freeze (CRATER_1, CRATER_2, BLIN*, CANON_2, …).

## Fix directions (after bisect)

- Ship disc1 copies of CSR+ D2/D3 packs for single-disc, and/or
- Fold required CSR+ crater/Hojo trims into single-disc-on-csr, and/or
- Re-apply movie/Ask freeze trims on merged CRATER_* / Hojo maps on D1

## Refs

- mods/single-disc/README.md
- mods/single-disc/patches/csr-d2d3-field-merge-on-d1.md
- CSR pack csr-plus-scene-hojo-fd-manip-v0.1.0 (disc 2 only)

## Operator follow-up (same session)

Retest: **both** single-disc CSR and single-disc CSR+ froze on crater entry once,
then after **restarting DuckStation** both stacks **worked**.

No standing issue to fix right now. Treat first freezes as possible emulator/session
state (stale RAM, bad load, long session) unless it returns after a clean boot.

Still want a deliberate late-game CSR+ single-disc smoke later (not emergency).

Structural note (Hojo CSR+ pack is D2-only on D1 single-disc) remains true for
future RE, but is **not** proven to cause this freeze after the restart clears it.

