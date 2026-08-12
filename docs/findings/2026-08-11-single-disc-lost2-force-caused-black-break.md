# Finding: Forced LOST2 to cos_btm2 caused black break (v0.1.6/0.1.7)

**Date:** 2026-08-11
**Status:** fixed in single-disc-on-csr-v0.1.8
**Stack:** CSR + Single-disc (no CSR+) — Build C still black after 0.1.7

## Symptom

Disc1 to disc2: black screen, disc-2-ish music, no CSR break menu / scene.

CSR multi-disc (swap D2) break remains OK.

## Wrong theory (0.1.6 / 0.1.7)

Assumed break needs LOST2 IFUW 55 a4 true then MAPJUMP cos_btm2, and that
0xa455 was disc id 2. Forced:

1. LOST2 else-jump on that IFUW so always MAPJUMP cos_btm2
2. COS_BTM2 large IFUW else-jumps to 0 (v0.1.7)

## Correct opcode read

IFUW/IFSW layout (FFRTT): op | B1B2 | A u16 | V u16 | C | E

- Bank byte 0x20 = bank 2 addr 0 = GameMoment, not disc id.
- Disc id is bank 13 (SETBYTE 80 d0 00 02 on BLACKBGB).
- Value 0xa455 is a CSR sentinel GameMoment that is never written by any
  FIELD script on Disc 2 (full DAT scan). So the LOST2 to cos_btm2 MAPJUMP is
  dead on multi-disc too.

## Why force black-screens

On forced landing in COS_BTM2 with normal end-of-D1 GameMoment (>= 0x0202):

- IFSW GM >= 0x0202 goes to SETBYTE then RET (skips break block)
- IFUW GM == 0xa455 break ASK / music is never reached after RET

Music from the early MUSIC f002 / AKAO path still runs = black + music.

Multi-disc CSR instead stays on CSR D2 LOST2 after BLACKBGB (post-swap),
with DSKCG + SETBYTE disc=2. Break choreography lives in that LOST2 / D2
open path, not the forced cos_btm2 init.

## Fix (v0.1.8)

Restore byte-identical CSR Disc 2 FIELD/LOST2.DAT and FIELD/COS_BTM2.DAT
on the single-disc image. Keep BLACKBGB DSKCG stripped + disc SETBYTE and
0.1.5 Ask strips.

## Evidence checks

| Check | 0.1.7 | 0.1.8 |
|-------|-------|-------|
| LOST2 == CSR D2 | no (force) | yes |
| COS_BTM2 == CSR D2 | no (force) | yes |
| LOST2 MAPJUMP IFUW else | 0x00 | 0x0B |
| COS break IFUW else | 0x00 | 0xCF |
| BLACKBGB DSKCG | 0 | 0 |

## Follow-up if break still missing

If playtest still lacks break after 0.1.8, investigate LOST2 non-init
scripts / version entity / movies pack streams — not another cos_btm2 IFUW force.
