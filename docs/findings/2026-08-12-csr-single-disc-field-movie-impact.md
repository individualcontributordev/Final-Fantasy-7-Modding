# CSR + Single-disc impact vs pristine D1/D2/D3

Stack (offline, same as builder):

1. CSR D1 cache `csr-v0.14.1`
2. `single-disc-on-csr-v0.1.20`
3. `single-disc-csr-manip-movies-v0.1.4`

FIELD compare = SHA-256 prefix of ISO user payload. Field **Id** = MAPLIST index. Movie **Id** = sorted MOVIE/ name (PMVIE).

## Summary

| Metric | Count |
|--------|------:|
| FIELD files on built D1 | 787 |
| Same as pristine D1 (not listed) | 536 |
| Diff vs pristine D1 (interesting) | 252 |
| **Single-disc touched** (diff vs CSR-D1) | **89** |
| CSR-base field deltas left as-is | 163 |
| MOVIE slots content and/or MOVIE_ID meta != P1 | 9 |
| LBA 250450 == pristine D2 CANONON sec0 | True |

### Single-disc-touched — content match buckets

| Built bytes match | Count |
|-------------------|------:|
| CSR-D2 | 67 |
| modified | 20 |
| pristine-D1+pristine-D2+pristine-D3+CSR-D2+CSR-D3 | 1 |
| CSR-D3 | 1 |

## Prefer-list overrides

| Field | Id | Prefer | Built matches | vs CSR-D1 |
|-------|---:|--------|---------------|-----------|
| BLACKBGB.DAT | 103 | d1 | modified | diff |
| BUGIN1A.DAT | 541 | review | CSR-D2 | diff |
| CANON_2.DAT | 741 | d2 | CSR-D2 | diff |
| COS_BTM.DAT | 525 | review | CSR-D2 | diff |
| COS_BTM2.DAT | 526 | review | CSR-D2 | diff |
| DEL1.DAT | 441 | d1 | CSR-D1 | same |
| JUNAIR2.DAT | 385 | review | CSR-D2 | diff |
| LOSIN2.DAT | 632 | d1 | CSR-D1 | same |
| LOST2.DAT | 634 | d2 | CSR-D2 | diff |
| NIVGATE.DAT | 279 | review | CSR-D2 | diff |
| RCKTIN2.DAT | 564 | review | CSR-D2 | diff |
| RCKTIN7.DAT | 569 | review | CSR-D2 | diff |

## A. Fields single-disc changed vs CSR D1

Primary single-disc FIELD surface (movies pack does not rewrite FIELD).

| Id | Field | Bytes match | vs P1 | vs P2 | vs P3 | Prefer |
|---:|-------|-------------|------|------|------|--------|
| 66 | FSHIP_1.DAT | CSR-D2 | diff | diff | diff | — |
| 67 | FSHIP_12.DAT | modified | diff | diff | diff | — |
| 68 | FSHIP_2.DAT | CSR-D2 | diff | diff | diff | — |
| 69 | FSHIP_22.DAT | CSR-D2 | diff | diff | diff | — |
| 70 | FSHIP_23.DAT | CSR-D2 | diff | diff | diff | — |
| 71 | FSHIP_24.DAT | CSR-D2 | diff | diff | diff | — |
| 72 | FSHIP_25.DAT | CSR-D2 | diff | diff | diff | — |
| 73 | FSHIP_3.DAT | CSR-D2 | diff | diff | diff | — |
| 74 | FSHIP_4.DAT | CSR-D2 | diff | diff | diff | — |
| 95 | BLACKBG3.DAT | modified | diff | diff | diff | — |
| 103 | BLACKBGB.DAT | modified | diff | diff | diff | d1 |
| 106 | BLACKBGE.DAT | modified | diff | diff | diff | — |
| 115 | WHITEBG3.DAT | modified | diff | diff | diff | — |
| 178 | MDS5_W.DAT | modified | diff | diff | diff | — |
| 255 | BLIN66_6.DAT | CSR-D2 | diff | diff | diff | — |
| 269 | BLIN70_4.DAT | CSR-D2 | diff | diff | diff | — |
| 279 | NIVGATE.DAT | CSR-D2 | diff | diff | diff | review |
| 280 | NIVGATE2.DAT | CSR-D2 | diff | diff | diff | — |
| 293 | NIVL_B22.DAT | CSR-D2 | diff | diff | diff | — |
| 345 | FRCYO.DAT | modified | diff | diff | diff | — |
| 347 | FR_E.DAT | CSR-D2 | diff | diff | diff | — |
| 354 | CONDOR2.DAT | CSR-D2 | diff | diff | diff | — |
| 355 | CONVIL_1.DAT | CSR-D2 | diff | diff | diff | — |
| 356 | CONVIL_2.DAT | CSR-D2 | diff | diff | diff | — |
| 384 | JUNAIR.DAT | CSR-D2 | diff | diff | diff | — |
| 385 | JUNAIR2.DAT | CSR-D2 | diff | diff | diff | review |
| 388 | JUNELE1.DAT | CSR-D2 | diff | diff | diff | — |
| 389 | JUNIN2.DAT | CSR-D2 | diff | diff | diff | — |
| 399 | JUNBIN22.DAT | CSR-D2 | diff | diff | diff | — |
| 400 | JUNBIN3.DAT | CSR-D2 | diff | diff | diff | — |
| 401 | JUNBIN4.DAT | CSR-D2 | diff | diff | diff | — |
| 402 | JUNBIN5.DAT | CSR-D2 | diff | diff | diff | — |
| 406 | SUBIN_1B.DAT | modified | diff | diff | diff | — |
| 411 | JUNONE2.DAT | CSR-D2 | diff | diff | diff | — |
| 416 | JUNONE7.DAT | CSR-D2 | diff | diff | diff | — |
| 424 | SEMKIN_4.DAT | CSR-D2 | diff | diff | diff | — |
| 425 | SEMKIN_5.DAT | CSR-D2 | diff | diff | diff | — |
| 440 | SHPIN_3.DAT | modified | diff | diff | diff | — |
| 460 | MTCRL_2.DAT | CSR-D2 | diff | diff | diff | — |
| 525 | COS_BTM.DAT | CSR-D2 | diff | diff | diff | review |
| 526 | COS_BTM2.DAT | CSR-D2 | diff | diff | diff | review |
| 535 | COSMIN2.DAT | modified | diff | diff | diff | — |
| 541 | BUGIN1A.DAT | CSR-D2 | diff | diff | diff | review |
| 561 | RCKTBAS1.DAT | CSR-D2 | diff | diff | diff | — |
| 562 | RCKTBAS2.DAT | CSR-D2 | diff | diff | diff | — |
| 564 | RCKTIN2.DAT | CSR-D2 | diff | diff | diff | review |
| 565 | RCKTIN3.DAT | CSR-D2 | diff | diff | diff | — |
| 567 | RCKTIN5.DAT | CSR-D2 | diff | diff | diff | — |
| 568 | RCKTIN6.DAT | CSR-D2 | diff | diff | diff | — |
| 569 | RCKTIN7.DAT | CSR-D2 | diff | diff | diff | review |
| 634 | LOST2.DAT | CSR-D2 | diff | diff | diff | d2 |
| 637 | LOSLAKE1.DAT | CSR-D2 | diff | diff | diff | — |
| 639 | LOSLAKE3.DAT | modified | diff | diff | diff | — |
| 641 | BLUE_2.DAT | pristine-D1+pristine-D2+pristine-D3+CSR-D2+CSR-D3 | same | same | same | — |
| 642 | WHITE1.DAT | CSR-D2 | diff | diff | diff | — |
| 643 | WHITE2.DAT | modified | diff | diff | diff | — |
| 676 | HYOU7.DAT | CSR-D2 | diff | diff | diff | — |
| 681 | HYOU11.DAT | modified | diff | diff | diff | — |
| 695 | GAIA_32.DAT | CSR-D2 | diff | diff | diff | — |
| 698 | GAIIN_6.DAT | CSR-D2 | diff | diff | diff | — |
| 700 | CRATER_1.DAT | CSR-D2 | diff | diff | diff | — |
| 701 | CRATER_2.DAT | CSR-D2 | diff | diff | diff | — |
| 702 | TRNAD_1.DAT | CSR-D2 | diff | diff | diff | — |
| 703 | TRNAD_2.DAT | CSR-D2 | diff | diff | diff | — |
| 705 | TRNAD_4.DAT | CSR-D2 | diff | diff | diff | — |
| 706 | TRNAD_51.DAT | CSR-D2 | diff | diff | diff | — |
| 707 | TRNAD_52.DAT | CSR-D2 | diff | diff | diff | — |
| 708 | TRNAD_53.DAT | modified | diff | diff | diff | — |
| 712 | ITOWN1A.DAT | CSR-D2 | diff | diff | diff | — |
| 715 | ITOWN2.DAT | CSR-D2 | diff | diff | diff | — |
| 717 | ITOWN_W.DAT | CSR-D2 | diff | diff | diff | — |
| 720 | ITHOS.DAT | CSR-D2 | diff | diff | diff | — |
| 725 | ZMIND1.DAT | CSR-D2 | diff | diff | diff | — |
| 726 | ZMIND2.DAT | CSR-D2 | diff | diff | diff | — |
| 727 | ZMIND3.DAT | CSR-D2 | diff | diff | diff | — |
| 728 | ZCOAL_1.DAT | CSR-D2 | diff | diff | diff | — |
| 730 | ZCOAL_3.DAT | CSR-D2 | diff | diff | diff | — |
| 732 | MD8_6.DAT | CSR-D2 | diff | diff | diff | — |
| 738 | MD8BRDG2.DAT | CSR-D2 | diff | diff | diff | — |
| 741 | CANON_2.DAT | CSR-D2 | diff | diff | diff | d2 |
| 763 | LAS4_0.DAT | CSR-D3 | diff | diff | diff | — |
| 765 | LAS4_2.DAT | modified | diff | diff | diff | — |
| 766 | LAS4_3.DAT | modified | diff | diff | diff | — |
| 767 | LAS4_4.DAT | modified | diff | diff | diff | — |
| 768 | LASTMAP.DAT | modified | diff | diff | diff | — |
| 773 | JUNONE22.DAT | CSR-D2 | diff | diff | diff | — |
| 777 | LAS4_42.DAT | modified | diff | diff | diff | — |
| 778 | TUNNEL_6.DAT | CSR-D2 | diff | diff | diff | — |
| 779 | MD8_52.DAT | modified | diff | diff | diff | — |

## B. Notable transitions

| Id | Field | Why |
|---:|-------|-----|
| 632 | LOSIN2.DAT | End D1 / disc-2 break arm — keep CSR D1 so GM 0xa455 for LOST2/COS. Built: `CSR-D1`. |
| 634 | LOST2.DAT | Disc 1->2 break scene body — CSR D2 on single-disc. Built: `CSR-D2`. |
| 741 | CANON_2.DAT | Hojo lab — pure CSR D2 (never raw-strip 0e03 in AKAO). Built: `CSR-D2`. |
| 103 | BLACKBGB.DAT | Post-Hojo / disc-3 gate — SD Ask/DSKCG stripped keep. Built: `modified`. |
| 526 | COS_BTM2.DAT | Cosmo / break IFUW disc-id path. Built: `CSR-D2`. |
| 643 | WHITE2.DAT | Cosmo Canyon graphical hybrid history. Built: `modified`. |
| 441 | DEL1.DAT | Forced keep CSR D1 core. Built: `CSR-D1`. |

## C. CSR-base field deltas (single-disc did not overwrite)

163 maps differ from pristine D1 because CSR changed them.

| Id | Field | Matches |
|---:|-------|---------|
| 86 | SEA.DAT | CSR-D1 |
| 87 | SKY.DAT | CSR-D1 |
| 101 | BLACKBG9.DAT | CSR-D1 |
| 104 | BLACKBGC.DAT | CSR-D1 |
| 116 | MD1STIN.DAT | CSR-D1 |
| 117 | MD1_1.DAT | CSR-D1 |
| 119 | NRTHMK.DAT | CSR-D1 |
| 120 | NMKIN_1.DAT | CSR-D1 |
| 125 | NMKIN_5.DAT | CSR-D1 |
| 126 | SOUTHMK1.DAT | CSR-D1 |
| 127 | SOUTHMK2.DAT | CSR-D1 |
| 129 | SMKIN_2.DAT | CSR-D1 |
| 132 | SMKIN_5.DAT | CSR-D1 |
| 133 | MD8_1.DAT | CSR-D1 |
| 137 | MD8BRDG.DAT | CSR-D1 |
| 138 | CARGOIN.DAT | CSR-D1 |
| 139 | TIN_1.DAT | CSR-D1 |
| 140 | TIN_2.DAT | CSR-D1 |
| 144 | MDS7ST1.DAT | CSR-D1 |
| 146 | MDS7ST3.DAT | CSR-D1 |
| 151 | MDS7.DAT | CSR-D1 |
| 154 | MDS7PB_1.DAT | CSR-D1 |
| 155 | MDS7PB_2.DAT | CSR-D1 |
| 156 | MDS7PLR1.DAT | CSR-D1 |
| 157 | MDS7PLR2.DAT | CSR-D1 |
| 159 | PILLAR_2.DAT | CSR-D1 |
| 160 | PILLAR_3.DAT | CSR-D1 |
| 161 | TUNNEL_1.DAT | CSR-D1 |
| 171 | MDS5_4.DAT | CSR-D1 |
| 173 | MDS5_2.DAT | CSR-D1 |
| 183 | CHRIN_1B.DAT | CSR-D1 |
| 184 | CHRIN_2.DAT | CSR-D1 |
| 186 | CHRIN_3B.DAT | CSR-D1 |
| 188 | EALIN_1.DAT | CSR-D1 |
| 189 | EALIN_12.DAT | CSR-D1 |
| 190 | EALIN_2.DAT | CSR-D1 |
| 191 | MDS6_1.DAT | CSR-D1 |
| 193 | MDS6_22.DAT | CSR-D1 |
| 195 | MRKT2.DAT | CSR-D1 |
| 196 | MKT_W.DAT | CSR-D1 |
| 197 | MKT_MENS.DAT | CSR-D1 |
| 199 | MKTINN.DAT | CSR-D1 |
| 200 | MKT_M.DAT | CSR-D1 |
| 201 | MKT_S1.DAT | CSR-D1 |
| 202 | MKT_S2.DAT | CSR-D1 |
| 206 | COLNE_1.DAT | CSR-D1 |
| 207 | COLNE_2.DAT | CSR-D1 |
| 209 | COLNE_4.DAT | CSR-D1 |
| 210 | COLNE_5.DAT | CSR-D1 |
| 211 | COLNE_6.DAT | CSR-D1 |
| 212 | COLNE_B1.DAT | CSR-D1 |
| 214 | MRKT3.DAT | CSR-D1 |
| 222 | MRKT4.DAT | CSR-D1 |
| 225 | MD0.DAT | CSR-D1 |
| 226 | ROADEND.DAT | CSR-D1 |
| 227 | SINBIL_1.DAT | CSR-D1 |
| 230 | BLINST_2.DAT | CSR-D1 |
| 233 | ELEOUT.DAT | CSR-D1 |
| 234 | BLIN1.DAT | CSR-D1 |
| 238 | BLIN59.DAT | CSR-D1 |
| 241 | BLIN61.DAT | CSR-D1 |
| 242 | BLIN62_1.DAT | CSR-D1 |
| 250 | BLIN66_1.DAT | CSR-D1 |
| 252 | BLIN66_3.DAT | CSR-D1 |
| 253 | BLIN66_4.DAT | CSR-D1 |
| 254 | BLIN66_5.DAT | CSR-D1 |
| 256 | BLIN67_1.DAT | CSR-D1 |
| 258 | BLIN67_2.DAT | CSR-D1 |
| 259 | BLIN67_3.DAT | CSR-D1 |
| 262 | BLIN68_1.DAT | CSR-D1 |
| 263 | BLIN68_2.DAT | CSR-D1 |
| 264 | BLIN69_1.DAT | CSR-D1 |
| 266 | BLIN70_1.DAT | CSR-D1 |
| 267 | BLIN70_2.DAT | CSR-D1 |
| 268 | BLIN70_3.DAT | CSR-D1 |
| 274 | NIVINN_2.DAT | CSR-D1 |
| 277 | TRACKIN.DAT | CSR-D1 |
| 282 | NIVL.DAT | CSR-D1 |
| 284 | NIVL_3.DAT | CSR-D1 |
| 290 | NIVL_B1.DAT | CSR-D1 |
| 292 | NIVL_B2.DAT | CSR-D1 |
| 294 | NIVL_E1.DAT | CSR-D1 |
| 299 | SININ2_1.DAT | CSR-D1 |
| 304 | SININB31.DAT | CSR-D1 |
| 307 | SININB41.DAT | CSR-D1 |
| 309 | SININB51.DAT | CSR-D1 |
| 311 | MTNVL2.DAT | CSR-D1 |
| 312 | MTNVL3.DAT | CSR-D1 |
| 315 | MTNVL6.DAT | CSR-D1 |
| 316 | MTNVL6B.DAT | CSR-D1 |
| 318 | NVDUN2.DAT | CSR-D1 |
| 319 | NVDUN3.DAT | CSR-D1 |
| 320 | NVDUN31.DAT | CSR-D1 |
| 322 | NVMKIN1.DAT | CSR-D1 |
| 323 | NVMKIN21.DAT | CSR-D1 |
| 326 | NVMKIN31.DAT | CSR-D1 |
| 327 | NVMKIN32.DAT | CSR-D1 |
| 331 | ELMINN_1.DAT | CSR-D1 |
| 332 | ELMINN_2.DAT | CSR-D1 |
| 335 | ELM.DAT | CSR-D1 |
| 349 | PSDUN_1.DAT | CSR-D1 |
| 360 | JUNONR1.DAT | CSR-D1 |
| 363 | JUNONR4.DAT | CSR-D1 |
| 382 | JUNDOC1A.DAT | CSR-D1 |
| 386 | JUNIN1.DAT | CSR-D1 |
| 387 | JUNIN1A.DAT | CSR-D1 |
| 428 | UJUNON1.DAT | CSR-D1 |
| 429 | UJUNON2.DAT | CSR-D1 |
| 433 | JUMIN.DAT | CSR-D1 |
| 434 | UJUNON4.DAT | CSR-D1 |
| 436 | SHIP_1.DAT | CSR-D1 |
| 437 | SHIP_2.DAT | CSR-D1 |
| 441 | DEL1.DAT | CSR-D1 |
| 450 | NCOREL.DAT | CSR-D1 |
| 457 | ROPEST.DAT | CSR-D1 |
| 461 | MTCRL_3.DAT | CSR-D1 |
| 471 | JAIL1.DAT | CSR-D1 |
| 475 | JAILIN2.DAT | CSR-D1 |
| 480 | DYNE.DAT | CSR-D1 |
| 484 | ASTAGE_A.DAT | CSR-D1 |
| 485 | ASTAGE_B.DAT | CSR-D1 |
| 488 | BIGWHEEL.DAT | CSR-D1 |
| 489 | BWHLIN.DAT | CSR-D1 |
| 493 | GHOTIN_4.DAT | CSR-D1 |
| 494 | GHOTIN_2.DAT | CSR-D1 |
| 496 | GLDST.DAT | CSR-D1 |
| 497 | GLDGATE.DAT | CSR-D1 |
| 499 | COLOSS.DAT | CSR-D1 |
| 502 | CLSIN2_1.DAT | CSR-D1 |
| 503 | CLSIN2_2.DAT | CSR-D1 |
| 505 | GAMES.DAT | CSR-D1 |
| 510 | CHORACE2.DAT | CSR-D1 |
| 512 | CRCIN_2.DAT | CSR-D1 |
| 518 | GONGAGA.DAT | CSR-D1 |
| 522 | GNINN.DAT | CSR-D1 |
| 531 | COSIN2.DAT | CSR-D1 |
| 544 | BUGIN2.DAT | CSR-D1 |
| 546 | GIDUN_1.DAT | CSR-D1 |
| 547 | GIDUN_2.DAT | CSR-D1 |
| 548 | GIDUN_4.DAT | CSR-D1 |
| 549 | GIDUN_3.DAT | CSR-D1 |
| 550 | SETO1.DAT | CSR-D1 |
| 552 | RCKT3.DAT | CSR-D1 |
| 557 | RCKT.DAT | CSR-D1 |
| 558 | RKTSID.DAT | CSR-D1 |
| 600 | JTEMPL.DAT | CSR-D1 |
| 601 | JTEMPLB.DAT | CSR-D1 |
| 602 | JTMPIN1.DAT | CSR-D1 |
| 603 | JTMPIN2.DAT | CSR-D1 |
| 604 | KURO_1.DAT | CSR-D1 |
| 606 | KURO_3.DAT | CSR-D1 |
| 610 | KURO_7.DAT | CSR-D1 |
| 611 | KURO_8.DAT | CSR-D1 |
| 612 | KURO_82.DAT | CSR-D1 |
| 613 | KURO_9.DAT | CSR-D1 |
| 616 | KURO_12.DAT | CSR-D1 |
| 618 | SLFRST_1.DAT | CSR-D1 |
| 632 | LOSIN2.DAT | CSR-D1 |
| 647 | ANCNT2.DAT | CSR-D1 |
| 648 | ANCNT3.DAT | CSR-D1 |
| 649 | ANCNT4.DAT | CSR-D1 |
| 774 | RCKT32.DAT | CSR-D1 |
| 775 | JTEMPLC.DAT | CSR-D1 |

## D. Movies / MOVIE_ID (manip-movies pack)

| Id | D1 slot | ISO size | Content | Meta!=P1 | eng LBA | eng size |
|---:|---------|---------:|---------|----------|--------:|---------:|
| 7 | CAR_1209.STR | 5240832 | pristine-D2:CANONHT2.MOV | False | 138823 | 4482784 |
| 34 | GOLD7_2.MOV | 249972 | pristine-D3:LAST4_3.BIN | False | 194789 | 8313824 |
| 36 | JAIROFAL.MOV | 15071232 | pristine-D2:CANONON.MOV | False | 202339 | 16744448 |
| 37 | JAIROFLY.MOV | 223000 | pristine-D3:LASTMAP.BIN | False | 209507 | 9871360 |
| 46 | MAINPLR.MOV | 4831232 | pristine-D1 | True | 325716 | 223000 |
| 47 | MK8.STR | 1064960 | pristine-D1 | True | 318357 | 17190624 |
| 49 | MONITOR.STR | 2314240 | pristine-D1 | True | 264311 | 287328 |
| 52 | MTNVL2.STR | 3543040 | pristine-D1 | True | 284833 | 5977824 |
| 64 | RCKTFAIL.MOV | 13154304 | ? | False | None | None |

### Absolute seeks

| LBA | Purpose | Status |
|----:|---------|--------|
| 250450 | LOSLAKE1 -> D2 CANONON (waterfall) | sec0 match D2: **True** (clobbers RCKTFAIL tail; may relocate JAIROFLY) |

## E. Playtest coverage vs residual risk

| Area | Your tests | Residual |
|------|------------|----------|
| Hojo CANON_2 + FMV | yes | — |
| LOSLAKE1 waterfall | yes | RCKTFAIL destroyed (tradeoff) |
| Disc1->2 break | yes | — |
| Final descent / battles | yes | — |
| Ending credits | planned | Full D3 credits need endings pack; manip is partial |
| Cosmo WHITE2 / COS_BTM* | history | Revisit if graphics/break odd |
| Rare D2/D3-only maps | no | See section A CSR-D2/D3 rows |
| Stock D1 movies at inject ids | side effect | CAR_1209/GOLD7_2/JAIRO* etc. |

## Method

- Offline ic-layer-v1 apply onto CSR D1 cache.
- No builder EDC step here (FMV Form2 bytes compared pre-EDC; alias is raw).

