# CSR multi-disc fields: prefer D1 vs D2

**Date:** 2026-08-06
**Status:** heuristic review of 10 D1+D2 CSR-divergent FIELD DATs
**Stack:** pristine NTSC-U + csr-v0.14.1 per disc

Companion: 2026-08-06-csr-multi-disc-field-edits.md
Policy file: mods/single-disc/patches/csr-field-disc-prefer.txt

## Method

- Compare FIELD DAT: pristine vs CSR D1 vs CSR D2
- MAPJUMP-like: byte 0x60 + u16 field id in 1..900
- PMVIE+MOVIE: 0xF8 then 0xF9 within 16 bytes
- Ask-like: 0x0E with arg 1/2/3
- Not a full Makou decompile; triage only

## Policy table (single-disc D1 image)

| Field | # | Phase | Prefer | Core now | Why |
|-------|--:|-------|--------|----------|-----|
| BLACKBGB.DAT | 103 | hub/blackbg (mid-late routing) | **prefer-D1** | OTHER/MIXED | D1 hub/routing; Ask/gates must stay D1; do not overwrite with D2 |
| BUGIN1A.DAT | 541 | Bugenhagen path (mid) | **review** | CSR-D2 | jump targets differ d1_only=[542] d2_only=[543] |
| COS_BTM.DAT | 525 | Cosmo bottom (mid) | **review** | CSR-D2 | jump targets differ d1_only=[32, 123, 266, 426, 500, 767] d2_only=[51, 65, 192, 393, 460] |
| COS_BTM2.DAT | 526 | Cosmo bottom2 (mid) | **review** | CSR-D2 | jump targets differ d1_only=[42, 130, 176, 192, 575, 632, 810] d2_only=[35, 38, 47, 112, 126, 525, 569, 612, 802] |
| DEL1.DAT | 441 | Costa DEL1 (mid) | **prefer-D1** | CSR-D1 | D1 removes MAPJUMP target 442; D2 keeps it (confirmed) |
| JUNAIR2.DAT | 385 | Junon airport (mid) | **review** | CSR-D2 | jump targets differ d1_only=[7, 9, 14, 433, 779] d2_only=[3] |
| LOST2.DAT | 634 | Lost forest / COTA path (late D2) | **prefer-D2** | CSR-D2 | single-disc already uses CSR D2 LOST2 break; verify if D1 path needs D1 version |
| NIVGATE.DAT | 279 | Nibelheim gate (early-mid / flashback) | **review** | CSR-D2 | jump targets differ d1_only=[264, 273, 711] d2_only=[146, 271, 769, 840] |
| RCKTIN2.DAT | 564 | Rocket town interior (mid-late) | **review** | CSR-D2 | jump targets differ d1_only=[636] d2_only=[434, 450, 635] |
| RCKTIN7.DAT | 569 | Rocket town interior (mid-late) | **review** | CSR-D2 | jump targets differ d1_only=[15, 19, 104, 119, 187, 226, 248, 262, 285, 577, 814, 824] d2_only=[6, 23, 46, 103, 155, 171, 224, 272, 288, 304, 317, 320, 529, 786, 846, 856] |

## Detail

### BLACKBGB.DAT (#103) — prefer-D1

- Phase: hub/blackbg (mid-late routing)
- Sizes base/D1/D2: (13008, 13013, 13013) (dD1=5, dD2=5)
- MAPJUMP-like count base/D1/D2: (15, 13, 13)
- MAPJUMP removed vs pristine — D1: [5, 20, 128, 298, 752] D2: [5, 20, 128, 298, 752]
- MAPJUMP only D1: [] only D2: []
- PMVIE+MOVIE pairs base/D1/D2: (3, 3, 3)
- PMVIE removed — D1: [] D2: []
- DSKCG-like count base/D1/D2: (1, 1, 1)
- Recommendation: **prefer-D1** — D1 hub/routing; Ask/gates must stay D1; do not overwrite with D2

### BUGIN1A.DAT (#541) — review

- Phase: Bugenhagen path (mid)
- Sizes base/D1/D2: (12092, 12117, 12097) (dD1=25, dD2=5)
- MAPJUMP-like count base/D1/D2: (10, 8, 8)
- MAPJUMP removed vs pristine — D1: [42, 64, 128, 227, 611, 613] D2: [42, 64, 128, 227, 611, 613]
- MAPJUMP only D1: [542] only D2: [543]
- PMVIE+MOVIE pairs base/D1/D2: (2, 0, 1)
- PMVIE removed — D1: [31, 253] D2: [31, 253]
- DSKCG-like count base/D1/D2: (4, 3, 4)
- Recommendation: **review** — jump targets differ d1_only=[542] d2_only=[543]

### COS_BTM.DAT (#525) — review

- Phase: Cosmo bottom (mid)
- Sizes base/D1/D2: (23228, 23141, 23143) (dD1=-87, dD2=-85)
- MAPJUMP-like count base/D1/D2: (16, 17, 17)
- MAPJUMP removed vs pristine — D1: [41, 52, 169, 187, 192, 271, 273, 275, 288, 295, 480, 599, 653] D2: [41, 52, 169, 187, 271, 273, 275, 288, 295, 480, 599, 653, 767]
- MAPJUMP only D1: [32, 123, 266, 426, 500, 767] only D2: [51, 65, 192, 393, 460]
- PMVIE+MOVIE pairs base/D1/D2: (29, 27, 29)
- PMVIE removed — D1: [4, 37, 48, 105, 156, 157, 159, 174, 177, 178, 190] D2: [37, 62, 68, 105, 156, 157, 159, 174, 177, 178, 190, 201]
- DSKCG-like count base/D1/D2: (2, 3, 3)
- Recommendation: **review** — jump targets differ d1_only=[32, 123, 266, 426, 500, 767] d2_only=[51, 65, 192, 393, 460]

### COS_BTM2.DAT (#526) — review

- Phase: Cosmo bottom2 (mid)
- Sizes base/D1/D2: (17167, 17572, 17558) (dD1=405, dD2=391)
- MAPJUMP-like count base/D1/D2: (17, 17, 19)
- MAPJUMP removed vs pristine — D1: [32, 112, 125, 128, 144, 187, 253, 303, 417, 420, 525, 592, 848, 897] D2: [32, 125, 128, 144, 187, 253, 303, 417, 420, 592, 848, 897]
- MAPJUMP only D1: [42, 130, 176, 192, 575, 632, 810] only D2: [35, 38, 47, 112, 126, 525, 569, 612, 802]
- PMVIE+MOVIE pairs base/D1/D2: (4, 4, 5)
- PMVIE removed — D1: [10, 88] D2: [10, 88, 255]
- DSKCG-like count base/D1/D2: (1, 1, 1)
- Recommendation: **review** — jump targets differ d1_only=[42, 130, 176, 192, 575, 632, 810] d2_only=[35, 38, 47, 112, 126, 525, 569, 612, 802]

### DEL1.DAT (#441) — prefer-D1

- Phase: Costa DEL1 (mid)
- Sizes base/D1/D2: (21700, 21432, 21456) (dD1=-268, dD2=-244)
- MAPJUMP-like count base/D1/D2: (19, 19, 17)
- MAPJUMP removed vs pristine — D1: [24, 29, 57, 93, 96, 98, 145, 157, 203, 221, 449, 497, 514, 666] D2: [29, 57, 93, 98, 145, 157, 203, 221, 296, 449, 497, 514, 666]
- MAPJUMP only D1: [20, 23, 64, 86, 89, 112, 170, 241, 296, 443, 511, 601] only D2: [24, 96, 165, 225, 271, 279, 287, 290, 295, 327]
- PMVIE+MOVIE pairs base/D1/D2: (6, 3, 3)
- PMVIE removed — D1: [49, 65, 183, 213] D2: [183, 213]
- DSKCG-like count base/D1/D2: (3, 3, 3)
- u16 442 present base/D1/D2: (True, False, True)
- Recommendation: **prefer-D1** — D1 removes MAPJUMP target 442; D2 keeps it (confirmed)

### JUNAIR2.DAT (#385) — review

- Phase: Junon airport (mid)
- Sizes base/D1/D2: (16729, 16720, 16720) (dD1=-9, dD2=-9)
- MAPJUMP-like count base/D1/D2: (5, 7, 3)
- MAPJUMP removed vs pristine — D1: [63, 408, 607] D2: [9, 63, 408, 607]
- MAPJUMP only D1: [7, 9, 14, 433, 779] only D2: [3]
- PMVIE+MOVIE pairs base/D1/D2: (4, 2, 2)
- PMVIE removed — D1: [78, 218, 219] D2: [78, 218, 219]
- DSKCG-like count base/D1/D2: (3, 3, 4)
- Recommendation: **review** — jump targets differ d1_only=[7, 9, 14, 433, 779] d2_only=[3]

### LOST2.DAT (#634) — prefer-D2

- Phase: Lost forest / COTA path (late D2)
- Sizes base/D1/D2: (16974, 17007, 17090) (dD1=33, dD2=116)
- MAPJUMP-like count base/D1/D2: (13, 17, 24)
- MAPJUMP removed vs pristine — D1: [1, 67, 193, 208, 209, 630, 747, 810, 844, 850] D2: [1, 67, 103, 193, 208, 209, 747, 810, 844, 850]
- MAPJUMP only D1: [99, 103, 144, 151, 178, 227, 240, 256, 447, 821] only D2: [2, 13, 15, 79, 110, 115, 126, 143, 164, 168, 207, 250, 336, 360, 455, 630, 655, 768]
- PMVIE+MOVIE pairs base/D1/D2: (1, 2, 4)
- PMVIE removed — D1: [] D2: []
- DSKCG-like count base/D1/D2: (0, 2, 1)
- Recommendation: **prefer-D2** — single-disc already uses CSR D2 LOST2 break; verify if D1 path needs D1 version

### NIVGATE.DAT (#279) — review

- Phase: Nibelheim gate (early-mid / flashback)
- Sizes base/D1/D2: (7366, 7378, 7358) (dD1=12, dD2=-8)
- MAPJUMP-like count base/D1/D2: (9, 5, 6)
- MAPJUMP removed vs pristine — D1: [800, 832, 864, 872, 880] D2: [264, 711, 800, 832, 864, 872, 880]
- MAPJUMP only D1: [264, 273, 711] only D2: [146, 271, 769, 840]
- PMVIE+MOVIE pairs base/D1/D2: (1, 1, 1)
- PMVIE removed — D1: [254] D2: [254]
- DSKCG-like count base/D1/D2: (0, 2, 2)
- Recommendation: **review** — jump targets differ d1_only=[264, 273, 711] d2_only=[146, 271, 769, 840]

### RCKTIN2.DAT (#564) — review

- Phase: Rocket town interior (mid-late)
- Sizes base/D1/D2: (17723, 17713, 17709) (dD1=-10, dD2=-14)
- MAPJUMP-like count base/D1/D2: (12, 13, 15)
- MAPJUMP removed vs pristine — D1: [8, 96, 126, 316, 432, 735, 848] D2: [8, 96, 126, 316, 432, 735, 848]
- MAPJUMP only D1: [636] only D2: [434, 450, 635]
- PMVIE+MOVIE pairs base/D1/D2: (3, 5, 5)
- PMVIE removed — D1: [123, 148] D2: [123, 148]
- DSKCG-like count base/D1/D2: (2, 2, 3)
- Recommendation: **review** — jump targets differ d1_only=[636] d2_only=[434, 450, 635]

### RCKTIN7.DAT (#569) — review

- Phase: Rocket town interior (mid-late)
- Sizes base/D1/D2: (13199, 13186, 13202) (dD1=-13, dD2=3)
- MAPJUMP-like count base/D1/D2: (15, 13, 18)
- MAPJUMP removed vs pristine — D1: [6, 27, 107, 175, 297, 321, 533, 613, 790, 850, 860] D2: [15, 19, 27, 107, 175, 297, 321, 533, 613, 790, 850, 860]
- MAPJUMP only D1: [15, 19, 104, 119, 187, 226, 248, 262, 285, 577, 814, 824] only D2: [6, 23, 46, 103, 155, 171, 224, 272, 288, 304, 317, 320, 529, 786, 846, 856]
- PMVIE+MOVIE pairs base/D1/D2: (0, 0, 1)
- PMVIE removed — D1: [] D2: []
- DSKCG-like count base/D1/D2: (4, 2, 0)
- Recommendation: **review** — jump targets differ d1_only=[15, 19, 104, 119, 187, 226, 248, 262, 285, 577, 814, 824] d2_only=[6, 23, 46, 103, 155, 171, 224, 272, 288, 304, 317, 320, 529, 786, 846, 856]

## Next actions

1. DEL1 already forced to CSR D1
2. For every prefer-D1 where core is not CSR-D1: restore CSR D1 DAT
3. LOST2 prefer-D2 is intentional exception if break scene stays
4. review rows: open CSR D1 and D2 in Makou before merging
5. Wire csr-field-disc-prefer.txt into future D2/D3 field merge script

## Core status after DEL1 fix

| Field | Prefer | Core blob | Action |
|-------|--------|-----------|--------|
| DEL1.DAT | d1 | CSR-D1 | done |
| BLACKBGB.DAT | d1 | OTHER/MIXED | OK if Makou Ask-on-D1; never replace with CSR D2 |
| LOST2.DAT | d2 | CSR-D2 | OK if break scene still wanted |
| BUGIN1A.DAT | review | CSR-D2 | Makou compare D1 vs D2 |
| COS_BTM.DAT | review | CSR-D2 | Makou compare |
| COS_BTM2.DAT | review | CSR-D2 | Makou compare |
| JUNAIR2.DAT | review | CSR-D2 | Makou compare |
| NIVGATE.DAT | review | CSR-D2 | Makou compare |
| RCKTIN2.DAT | review | CSR-D2 | Makou compare |
| RCKTIN7.DAT | review | CSR-D2 | Makou compare |

## Confidence notes

- DEL1 high confidence (u16 field-id 442 presence/absence).
- BLACKBGB / LOST2 from single-disc design notes.
- review rows: raw 0x60 MAPJUMP scan has false positives; decide in Makou.
- Size deltas still prove CSR D1 and CSR D2 are different authentic edits.

## Structured verification (2026-08-06)

Tool: python3 scripts/compare_field_dat.py --batch-collisions

Reports: field-collisions-2026-08-06/README.md

| Stem | CSR D1 vs D2 class | script slot diffs | pad-only? |
|------|--------------------|------------------:|-----------|
| BLACKBGB | scripts | 1 | no |
| BUGIN1A | scripts | 3 | no |
| COS_BTM | scripts | 3 | no |
| COS_BTM2 | mixed | 14 (+1 text) | no |
| DEL1 | scripts | 5 | no (D2 alone vs pris was pad-only; D1 vs D2 is real) |
| JUNAIR2 | scripts | 1 | no |
| LOST2 | scripts | 22 | no |
| NIVGATE | scripts | 18 | no |
| RCKTIN2 | scripts | 2 | no |
| RCKTIN7 | scripts | 1 | no |

None of the 10 multi-disc collisions are padding-only. Prefer-D1 / prefer-D2 / review policy still required for each stem.

