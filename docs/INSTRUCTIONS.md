# Task: Isolate disc-2 Hojo glitch (then disc-3 transition)

## Closed (success)

single-disc-on-csr-v0.1.9 — Jenova, end-of-disc-1 trims, disc1-to-disc2
transition, and break scene: working as expected.

## Open report

Disc-2 Hojo fight / post-fight is glitched. After Hojo comes the
disc-3 swap path (BLACKBGD to BLACKBGB to LAS0_1).

## What we know in bytes (v0.1.9)

Path after Hojo fight (CSR D2 / SD same for these ops):

1. CANON_2 (#741) hojyo/31: BATTLE then set GM 0x644 then MAPJUMP BLACKBGD (#105)
2. BLACKBGD dir/31: MAPJUMP BLACKBGB (#103)
3. BLACKBGB: SETBYTE disc=3, MAPJUMP LAS0_1 (#744) (DSKCG stripped on SD)

CANON_2 on SD:

- Script slots match CSR D2 (including hojyo fight/exit)
- Texts match CSR D2
- AKAO block same size but bytes differ (possible audio glitch source)
- Compressed DAT is OTHER vs pure D2 (Ask-strip era / merge residue)

Movies:

- CSR D2 has CANONHT2.MOV / CANONON.MOV as real files
- Single-disc D1 has no those filenames; manip-movies seeds CANONHT2 into a
  D1 slot (CAR_1209) and CANONON into JAIROFAL / LBA alias
- CSR+ Hojo pack removes CANONHT2 play on multi-disc CSR+; plain CSR keeps it

So glitch is likely one of: wrong/missing Hojo FMV stream, AKAO/audio mismatch,
or CSR+ Hojo D1 layer fighting single-disc (if CSR+ was on).

## What you do (isolation)

Always: hard-refresh builder; quit DuckStation fully between builds; no CE;
save-state only a field or two before Hojo / Sister Ray corridor.

### Build H1 — CSR + Single-disc only (CSR+ off)

APPLIED must have single-disc-on-csr-v0.1.9 and movies pack auto.
No csr-plus-scene-* packs.

Play to Hojo fight through post-fight toward disc-3 hub.

### Build H2 — H1 + CSR+ Hojo only

Also enable CSR+ Hojo lab trim (has disc1 layer). Prefer no other CSR+ packs.

## Evidence (paste)

```
APPLIED single-disc id:
APPLIED movies: YES/NO id:
APPLIED CSR+ Hojo: YES/NO
Build: H1 / H2 / other

Pre-Hojo corridor: OK / GLITCH / FREEZE
Hojo fight: OK / GLITCH / FREEZE
Post-Hojo field (CANON_2 after battle): OK / GLITCH / FREEZE
BLACKBGD / BLACKBGB: OK / GLITCH / ASK / FREEZE
Toward LAS0_1 / disc3: OK / GLITCH / FREEZE / OTHER

What glitch looks like (graphics / audio / wrong scene / softlock):
Load method: in-game save / save-state (field or two before)
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.

Commit example: ops: isolate single-disc Hojo glitch after D1-D2 OK
