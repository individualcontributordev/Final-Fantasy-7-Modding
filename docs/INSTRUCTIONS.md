# Task: Retest Hojo field (CANON_2) on single-disc-on-csr v0.1.20

## Closed earlier

v0.1.9: Jenova, end disc 1 trims, disc1-to-disc2, break scene OK.

## What was wrong on Hojo

CANON_2 (#741) glitched as soon as the field loaded (CSR + Single-disc, no CSR+).
v0.1.5 raw DSKCG strip rewrote `0e 03` bytes inside **AKAO music data** (not real
disc-change ops). CSR D2 CANON_2 has zero DSKCG/ASK opcodes.

## Fix

single-disc-on-csr-v0.1.20 restores pure CSR Disc 2 CANON_2.DAT.

## What you do

1. Hard-refresh the builder
2. Base: CSR
3. Mods: Single-disc only (CSR+ off)
4. Confirm APPLIED has single-disc-on-csr-v0.1.20
5. Build Disc 1
6. Quit DuckStation fully; no CE
7. Load save-state a field or two before Hojo (e.g. BLIN66_6 / FSHIP_24), play in
8. Check CANON_2 on load, fight, post-fight toward BLACKBGD / disc3 if possible

Expect: Hojo field looks like multi-disc CSR (not fully glitched on entry).

## Evidence (paste)

```
APPLIED single-disc id:
movies pack auto?: YES/NO
CSR+: OFF
CANON_2 on load: OK / GLITCH / FREEZE
Hojo fight: OK / GLITCH / FREEZE / NOT REACHED
Post-Hojo / BLACKBGD: OK / GLITCH / FREEZE / NOT REACHED
Toward disc3 / LAS0_1: OK / GLITCH / FREEZE / NOT REACHED
Load method: in-game save / save-state (field or two before)
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.

Commit example: ops: retest Hojo CANON_2 after single-disc 0.1.20
