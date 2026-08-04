# Audit: single-disc-clean-v0.1.1 vs pristine Clean D1

Question: Did Set next movie / Play movie (and Ask) deletes remove anything unintended?

Built: workspace/iso-extract/ff7_d1_clean_single_disc_v011_built.bin
Layer: builder/single-disc-clean-v0.1.1

## Summary verdict

**No unexpected FIELD maps outside the known Ask + movie-trim set.**

| Category | Count | OK? |
|----------|------:|-----|
| FIELD DATs changed | 18 | All accounted for |
| Ask hubs (BLACKBGB/3/E) | 3 | Expected |
| Movie-trim maps (operator list / inventory) | 15 | Expected |
| Other FIELD DATs | 0 | Good |
| BATTLE.X | 1 | Expected (SNOVA LBA) |
| SNOVA/ inject | yes | Expected |
| FIELD/FIELD.BIN | small dec diff (18 bytes) | See below — review |
| SCUS / DISKINFO | unchanged | Good |

## All 18 changed FIELD DATs

| ID | DAT | sizeΔ | F8/F9 pair-like change | Role |
|---:|-----|------:|------------------------|------|
| 67 | FSHIP_12.DAT | -14 | pairs reduced (had F9 plays) | Highwind-related map movie trim |
| 68 | FSHIP_2.DAT | -9 | mid swap 54→17 noise possible; size down | Ship map movie edit |
| 95 | BLACKBG3.DAT | -2 | Ask hub | Ask-for-disc |
| 103 | BLACKBGB.DAT | +1 | Ask hub | Ask-for-disc |
| 106 | BLACKBGE.DAT | -2 | Ask hub | Ask-for-disc |
| 269 | BLIN70_4.DAT | -1 | pairs 1→0 (mid 60 OPENMV) | Operator trim GM≥1572 |
| 347 | FR_E.DAT | -8 | pairs 2→0 (48 MKUP, 49 MONITOR) | Operator trim Diamond Weapon |
| 637 | LOSLAKE1.DAT | -2 | pairs reduced | Lake movie trim |
| 639 | LOSLAKE3.DAT | -9 | 57/58 removed (ONTRAIN/OPENING) | Known lake Bugenhagen trim |
| 643 | WHITE2.DAT | -8 | pairs 3→0 | Movie trim |
| 708 | TRNAD_53.DAT | -5 | pairs 2→0 (incl FSHIP2 class) | Tier1 / crawl |
| 763 | LAS4_0.DAT | +5 | pairs 1→0 (FSHIP2N) | N. Cave / descent |
| 765 | LAS4_2.DAT | -7 | all F9 removed (3→0) | Descent BG movie |
| 766 | LAS4_3.DAT | -12 | F8 reduced; movie-related | Descent |
| 767 | LAS4_4.DAT | -7 | F8 cleared | Descent |
| 768 | LASTMAP.DAT | -12 | pairs 2→0 | Endgame map movie |
| 777 | LAS4_42.DAT | 0 | pairs 1→0 | Descent variant |
| 779 | MD8_52.DAT | +2 | pairs 1→0 (MTNVL2 id) | Midgar-related movie |

No changed DAT is outside Ask hubs + known movie-trim story areas (ship, lake, cave/descent, Diamond Weapon, midgar trap fr_e, white2, lastmap, fship).

## FIELD.BIN (engine) anomaly

FIELD.BIN **is** in the layer and differs from pristine:

- Compressed size 85435 → 85359 (−76)
- Decompressed size same 264008
- **Only 18 bytes** differ in the decompressed engine, clustered near file offset **0x3AC04**

This is **not** a field map script. Possible causes:

1. Accidental inclusion when building the layer from a work bin that recompressed FIELD.BIN
2. Unrelated tiny patch
3. Tooling side effect

**Recommend:** For a pure "scripts + SNOVA" pack, FIELD.BIN should match pristine except if you intentionally patched the engine. Worth confirming in Makou/work bin whether FIELD.BIN was ever saved/replaced.

If unintentional: rebuild layer from a work bin after restoring pristine FIELD.BIN (keep FIELD/*.DAT edits + SNOVA + BATTLE.X only).

## What you did not delete (examples)

- 71 maps with PMVIE+MOVIE pairs still present under early ids / non-edited maps
- SCUS, DISKINFO, SYSTEM.CNF unchanged
- LBA 226545 / BISKDEAD–BOOGDEMO region untouched by layer (ImgBurn issue separate)

## Bottom line

**Map-level Set/Play (and Ask) edits look intentional and scoped.** No evidence of random maps stripped.

**One follow-up:** verify **FIELD.BIN** 18-byte engine delta is intentional; if not, strip it in 0.1.2.

## Method

Compare every FIELD/*.DAT byte-wise pristine vs built; LZS-decompress and count F8…F9 patterns; classify vs known ask/movie lists.
