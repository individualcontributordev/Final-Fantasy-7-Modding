## TASK: create a manual-edit bin in Makou Reactor, then dump + compare

### Step 1 — build a base bin with everything EXCEPT the automated DSKCG removal

This matches the real pipeline (rework merge + safe-field merge + FIELD.BIN
table fix + SNOVA inject) but skips the automated DSKCG step, so you can
manually delete the opcode yourself and get an apples-to-apples comparison:

```
python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/manual-edit-base.bin --skip-dskcg-removal
```

### Step 2 — open it in Makou Reactor and manually remove the DSKCG opcode

1. Open `workspace/iso-extract/manual-edit-base.bin` in Makou Reactor.
2. Open field `BLACKBGB`, script `init`, slot `0`.
3. Find the `DSKCG` (Ask for disc) opcode inside the branch gated by
   `if var[3][136] bitON 4` (the one you previously confirmed is on the
   D1→D2 path) and delete just that one opcode.
4. Save the field in Makou Reactor, then save/export the .bin (however you
   normally do it — e.g. File > Save, or export to a new .bin path). Note
   the exact output path.
5. Test that this manually-edited bin actually shows the "want to save?"
   prompt when going D1→D2, to confirm it's a known-good reference.

### Step 3 — dump and compare

Run the dump script against your manually-edited bin and paste the full
output back here:

```
python3 mods/single-disc/scripts/dump_blackbgb_debug.py path/to/your-manual-edit.bin
```

Also run it against the latest auto-built bin for comparison:

```
python3 mods/single-disc/scripts/dump_blackbgb_debug.py workspace/iso-extract/single-disc-dskcg-tablefix-test.bin
```

Paste both full outputs (or the exact file paths used) so the two
"init slot 0" script dumps can be diffed byte-for-byte.

---

python3 mods/single-disc/scripts/dump_blackbgb_debug.py workspace/iso-extract/manual-edit-base.bin 
BLACKBGB.DAT: lba=58550 size=13013
FIELD.BIN table: 1864 entries, looking for rel_lba=3550
  (no matching table entry found by rel_lba scan)
--- manual-edit-base.bin: init slot 0 (794 bytes) ---
   0 UC           3301
   2 MENU2        4a01
   4 RET          00
   5 IFUB         1430880709f2
  11 MUSIC        f000
  13 AKAO         f2000000c1017f00000000000000
  27 AKAO         f200000028400000000000000000
  41 AKAO         f200000029400000000000000000
  55 AKAO         f20000002a400000000000000000
  69 AKAO         f20000002b400000000000000000
  83 AKAO         f2000000a07f0000000000000000
  97 AKAO         f2000000a17f0000000000000000
 111 AKAO         f2000000a27f0000000000000000
 125 AKAO         f2000000a37f0000000000000000
 139 AKAO         f2000000b0000000000000000000
 153 AKAO         f2000000b1000000000000000000
 167 AKAO         f2000000b2000000000000000000
 181 AKAO         f2000000b3000000000000000000
 195 BMUSC        f601
 197 BITOFF       83308807
 201 MENU         49031500
 205 BATTLE       7000d401
 209 MAPJUMP      60e20025fbdeff320000
 219 AKAO         f2000000c1ff0000000000000000
 233 WAIT         245000
 236 MUSIC        f000
 238 AKAO         f2000000c1007f00000000000000
 252 IFUB         14d05b020930
 258 BITON        82308807
 262 BITOFF       83d05b02
 266 MHMMX        3e
 267 WMODE        52000101
 271 WMODE        52010001
 275 WMODE        52020001
 279 WMODE        52030201
 283 WAIT         240100
 286 REQ          0106c3
 289 REQ          0107c3
 292 WINDOW       5000100008001f013900
 302 MESSAGE      400003
 305 IFUB         143088050919
 311 BITOFF       83308805
 315 WAIT         240400
 318 MUSIC        f002
 320 WAIT         240800
 323 MAPJUMP      60e802f9ff6bfcf300e4
 333 JMPF         10c8
 335 IFUB         14d05206094a
 341 BITOFF       83d05206
 345 REQ          0105c4
 348 WAIT         241000
 351 WINDOW       500146007d00b4004900
 361 ASK          48050101020300
 368 MHMMX        3e
 369 IFUB         145000020010
 375 WAIT         240400
 378 BITON        82308805
 382 SETBYTE      80d00003
 386 MENU         49000e00
 390 BITOFF       83308805
 394 WAIT         240400
 397 MUSIC        f002
 399 WAIT         240800
 402 MAPJUMP      60e802f9ff6bfcf300e4
 412 JMPF         1079
 414 IFUB         143086020920
 420 BITOFF       83308602
 424 WAIT         240400
 427 WAIT         240800
 430 BITON        82308901
 434 MAPJUMP      607a02fdfeb213710000
 444 MUSIC        f003
 446 WAIT         240800
 449 JMPF         1054
 451 IFUB         14308804094e
 457 BITOFF       83308804
 461 REQ          0105c3
 464 WAIT         241000
 467 WINDOW       500146007d00b4004900
 477 ASK          48050101020300
 484 IFUB         145000020010
 490 WAIT         240400
 493 BITON        82308602
 497 SETBYTE      80d00002
 501 MENU         49000e00
 505 BITOFF       83308602
 509 WAIT         240400
 512 WAIT         240800
 515 BITON        82308901
 519 WAIT         240800
 522 MAPJUMP      607a02fdfeb213710000
 532 MUSIC        f003
 534 IFUB         1430830209c1
 540 UC           3301
 542 MENU2        4a01
 544 NFADE        250000000000000000
 553 AKAO         f2000000a4100000000000000000
 567 AKAO         f2000000a5100000000000000000
 581 AKAO         f2000000a3100000000000000000
 595 AKAO         f2000000c1100000000000000000
 609 WAIT         240600
 612 AKAO         f200000028400000000000000000
 626 AKAO         f200000029400000000000000000
 640 AKAO         f20000002a400000000000000000
 654 AKAO         f2000000a4017f00000000000000
 668 AKAO         f2000000a5017f00000000000000
 682 AKAO         f2000000a3017f00000000000000
 696 MUSIC        f000
 698 AKAO         f2000000c1017f00000000000000
 712 PMVIE        f82d
 714 MOVIE        f9
 715 WAIT         240300
 718 MULCK        f501
 720 MAPJUMP      602e02d7ff99015500f0
 730 JMPF         103e
 732 IFSW         162000007e020036
 740 AKAO         f2000000c1600000000000000000
 754 WAIT         243000
 757 MUSIC        f000
 759 AKAO         f2000000c1010000000000000000
 773 WAIT         240400
 776 MMBud        cd0003
 779 MENU         49001103
 783 MAPJUMP      600a0289fff0002200ff
 793 RET          00
total len 794






python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-dskcg-tablefix-test.bin
Loading CSR D1/D2 reference images...
Base: CSR D1 (747,435,024 bytes)

Applying 8-field rework merge (verdict table)...
  [slot-splice] BUGIN1A: 1 slots spliced, new size 12195 bytes
  [slot-splice] NIVGATE: 13 slots spliced, new size 7213 bytes
  [slot-splice] RCKTIN2: 1 slots spliced, new size 17822 bytes

Applying bulk safe-field merge (non-collision D2/D3 edits)...
  Applied 67/67 safe field merges

Removing DSKCG (ask-for-disc) ops via live splicer for ['BLACKBGB'] (only occurrence(s) [3])...
    init slot 0: Removed 1 DSKCG
  BLACKBGB: removed 1 DSKCG (12929 bytes)
  Total fields modified: 1

Patching FIELD.BIN/WORLD.BIN embedded (location,size) tables...
  FIELD/FIELD.BIN table: BLACKBGB.DAT @58550 size 13013 -> 12929
  FIELD/FIELD.BIN table: BLIN66_6.DAT @72265 size 13316 -> 13340
  FIELD/FIELD.BIN table: BLIN70_4.DAT @73653 size 9579 -> 9595
  FIELD/FIELD.BIN table: BUGIN1A.DAT @100193 size 12117 -> 12195
  FIELD/FIELD.BIN table: CANON_2.DAT @121844 size 24844 -> 24698
  FIELD/FIELD.BIN table: CONDOR2.DAT @81722 size 7211 -> 7217
  FIELD/FIELD.BIN table: CONVIL_1.DAT @81793 size 24285 -> 24306
  FIELD/FIELD.BIN table: CONVIL_2.DAT @81936 size 21290 -> 21156
  FIELD/FIELD.BIN table: CRATER_1.DAT @117071 size 12314 -> 12320
  FIELD/FIELD.BIN table: CRATER_2.DAT @117223 size 18114 -> 18129
  FIELD/FIELD.BIN table: FR_E.DAT @80996 size 16368 -> 16376
  FIELD/FIELD.BIN table: FSHIP_1.DAT @55277 size 4926 -> 4911
  FIELD/FIELD.BIN table: FSHIP_22.DAT @55605 size 12093 -> 12097
  FIELD/FIELD.BIN table: FSHIP_23.DAT @55782 size 21390 -> 21387
  FIELD/FIELD.BIN table: FSHIP_24.DAT @55957 size 15572 -> 15617
  FIELD/FIELD.BIN table: FSHIP_25.DAT @56136 size 29850 -> 29800
  FIELD/FIELD.BIN table: FSHIP_3.DAT @56317 size 12071 -> 12074
  FIELD/FIELD.BIN table: FSHIP_4.DAT @56425 size 17328 -> 17293
  FIELD/FIELD.BIN table: GAIA_32.DAT @116589 size 5535 -> 5536
  FIELD/FIELD.BIN table: GAIIN_6.DAT @116885 size 9541 -> 9542
  FIELD/FIELD.BIN table: HYOU7.DAT @114422 size 15007 -> 15059
  FIELD/FIELD.BIN table: ITHOS.DAT @119756 size 16171 -> 16187
  FIELD/FIELD.BIN table: ITOWN1A.DAT @118600 size 22854 -> 22856
  FIELD/FIELD.BIN table: ITOWN2.DAT @119255 size 8658 -> 8627
  FIELD/FIELD.BIN table: ITOWN_W.DAT @119465 size 12027 -> 12000
  FIELD/FIELD.BIN table: JUNAIR.DAT @84555 size 26248 -> 26279
  FIELD/FIELD.BIN table: JUNBIN22.DAT @85651 size 12917 -> 12923
  FIELD/FIELD.BIN table: JUNBIN3.DAT @85725 size 11491 -> 11506
  FIELD/FIELD.BIN table: JUNBIN4.DAT @85785 size 18015 -> 17963
  FIELD/FIELD.BIN table: JUNBIN5.DAT @85889 size 17912 -> 17894
  FIELD/FIELD.BIN table: JUNIN2.DAT @84980 size 17990 -> 17997
  FIELD/FIELD.BIN table: JUNONE2.DAT @86715 size 11095 -> 11094
  FIELD/FIELD.BIN table: JUNONE22.DAT @125702 size 5921 -> 5929
  FIELD/FIELD.BIN table: JUNONE7.DAT @87142 size 12269 -> 12210
  FIELD/FIELD.BIN table: LAS4_0.DAT @124908 size 15377 -> 15395
  FIELD/FIELD.BIN table: LAS4_2.DAT @125223 size 6879 -> 6880
  FIELD/FIELD.BIN table: LAS4_4.DAT @125283 size 6325 -> 6334
  FIELD/FIELD.BIN table: LASTMAP.DAT @125347 size 23302 -> 23326
  FIELD/FIELD.BIN table: LOSLAKE1.DAT @109793 size 21195 -> 21207
  FIELD/FIELD.BIN table: LOST2.DAT @109345 size 16974 -> 17032
  FIELD/FIELD.BIN table: MD8BRDG2.DAT @121560 size 17846 -> 17695
  FIELD/FIELD.BIN table: MD8_6.DAT @121053 size 19843 -> 19695
  FIELD/FIELD.BIN table: MTCRL_2.DAT @92237 size 23601 -> 23436
  FIELD/FIELD.BIN table: NIVGATE.DAT @74319 size 7378 -> 7213
  FIELD/FIELD.BIN table: NIVGATE2.DAT @74381 size 7308 -> 7280
  FIELD/FIELD.BIN table: NIVL_B22.DAT @75913 size 16492 -> 16400
  FIELD/FIELD.BIN table: RCKTBAS1.DAT @102419 size 26218 -> 26193
  FIELD/FIELD.BIN table: RCKTBAS2.DAT @102591 size 24129 -> 24100
  FIELD/FIELD.BIN table: RCKTIN2.DAT @102803 size 17713 -> 17822
  FIELD/FIELD.BIN table: RCKTIN3.DAT @102897 size 13328 -> 13335
  FIELD/FIELD.BIN table: RCKTIN5.DAT @103028 size 20893 -> 20923
  FIELD/FIELD.BIN table: RCKTIN6.DAT @103111 size 16186 -> 16172
  FIELD/FIELD.BIN table: RCKTIN7.DAT @103210 size 13186 -> 13202
  FIELD/FIELD.BIN table: SEMKIN_4.DAT @87948 size 22539 -> 22373
  FIELD/FIELD.BIN table: SEMKIN_5.DAT @88116 size 22225 -> 22069
  FIELD/FIELD.BIN table: SUBIN_1B.DAT @86260 size 19932 -> 19963
  FIELD/FIELD.BIN table: TRNAD_1.DAT @117324 size 15788 -> 15796
  FIELD/FIELD.BIN table: TRNAD_2.DAT @117485 size 13054 -> 13069
  FIELD/FIELD.BIN table: TRNAD_4.DAT @117727 size 19219 -> 19195
  FIELD/FIELD.BIN table: TRNAD_51.DAT @117880 size 15250 -> 15248
  FIELD/FIELD.BIN table: TRNAD_52.DAT @118054 size 6374 -> 6425
  FIELD/FIELD.BIN table: TUNNEL_6.DAT @126016 size 23251 -> 23082
  FIELD/FIELD.BIN table: WHITE1.DAT @110379 size 11459 -> 11472
  FIELD/FIELD.BIN table: WHITE2.DAT @110479 size 9395 -> 9381
  FIELD/FIELD.BIN table: ZCOAL_1.DAT @120619 size 16023 -> 15851
  FIELD/FIELD.BIN table: ZCOAL_3.DAT @120814 size 15161 -> 14989
  FIELD/FIELD.BIN table: ZMIND1.DAT @120288 size 9323 -> 9246
  FIELD/FIELD.BIN table: ZMIND2.DAT @120402 size 9266 -> 9285
  FIELD/FIELD.BIN table: ZMIND3.DAT @120498 size 12123 -> 12163
Source (dec):     C:\Users\David\AppData\Local\Temp\tmpq_gcd5na\bin.dec (264008 bytes)
Original (bin):   C:\Users\David\AppData\Local\Temp\tmpq_gcd5na\bin.orig (85346 bytes)
Output:           C:\Users\David\AppData\Local\Temp\tmpq_gcd5na\bin.new (81162 bytes)
Method:           zopfli
Size delta:       -4184 bytes
Shorter than original — CDmage 'pad with zeros?' → Yes.
  Total table entries patched: 69

Wrote workspace\iso-extract\single-disc-dskcg-tablefix-test.bin (747,435,024 bytes) [pre-SNOVA]

Injecting SNOVA D3 -> D1...
D3 SNOVA raw block LBA 127100+570 files=17
grow sectors 317787 -> 318357 (delta LBA 190687)
patch BATTLE.X hardcoded SNOVA LBAs (delta 190687)
  BATTLE.X LBA 0x48D78: 127254 -> 317941
  BATTLE.X LBA 0x48D80: 127293 -> 317980
  BATTLE.X LBA 0x48D88: 127320 -> 318007
  BATTLE.X LBA 0x48D90: 127354 -> 318041
  BATTLE.X LBA 0x48D98: 127373 -> 318060
  BATTLE.X LBA 0x48DA0: 127394 -> 318081
  BATTLE.X LBA 0x48DA8: 127430 -> 318117
  BATTLE.X LBA 0x48DB0: 127442 -> 318129
  BATTLE.X LBA 0x48DB8: 127464 -> 318151
  BATTLE.X LBA 0x48DC0: 127503 -> 318190
  BATTLE.X LBA 0x48DC8: 127544 -> 318231
  BATTLE.X LBA 0x48DD0: 127555 -> 318242
  BATTLE.X LBA 0x48DD8: 127562 -> 318249
  BATTLE.X LBA 0x48DE0: 127571 -> 318258
  BATTLE.X LBA 0x48DE8: 127618 -> 318305
  BATTLE.X LBA 0x48DF0: 127649 -> 318336
  BATTLE.X LBA 0x4F5A8: 127101 -> 317788
Source (dec):     C:\Users\David\AppData\Local\Temp\tmp6h2ghzjc\BATTLE.X.dec (342188 bytes)
Original (bin):   C:\Users\David\AppData\Local\Temp\tmp6h2ghzjc\BATTLE.X.orig (130322 bytes)
Output:           C:\Users\David\AppData\Local\Temp\tmp6h2ghzjc\BATTLE.X.new (123557 bytes)
Method:           zopfli
Size delta:       -6765 bytes
Shorter than original — CDmage 'pad with zeros?' → Yes.
  BATTLE.X recompress 130322 -> 123557 (pad 6765)
wrote workspace\iso-extract\single-disc-dskcg-tablefix-test.bin (raw-copy + BATTLE.X LBA patch v3)
verify: BATTLE.X 17 LBA entries remapped
verify: all SNOVA files match D3

Done. Final work bin: workspace\iso-extract\single-disc-dskcg-tablefix-test.bin
➜  Final-Fantasy-7-Modding git:(main) ✗ python3 mods/single-disc/scripts/dump_blackbgb_debug.py workspace/iso-extract/single-disc-dskcg-tablefix-test.bin

BLACKBGB.DAT: lba=58550 size=12929
FIELD.BIN table: 1864 entries, looking for rel_lba=3550
  (no matching table entry found by rel_lba scan)
--- single-disc-dskcg-tablefix-test.bin: init slot 0 (800 bytes) ---
   0 UC           3301
   2 MENU2        4a01
   4 RET          00
   5 IFUB         1430880709f2
  11 MUSIC        f000
  13 AKAO         f2000000c1017f00000000000000
  27 AKAO         f200000028400000000000000000
  41 AKAO         f200000029400000000000000000
  55 AKAO         f20000002a400000000000000000
  69 AKAO         f20000002b400000000000000000
  83 AKAO         f2000000a07f0000000000000000
  97 AKAO         f2000000a17f0000000000000000
 111 AKAO         f2000000a27f0000000000000000
 125 AKAO         f2000000a37f0000000000000000
 139 AKAO         f2000000b0000000000000000000
 153 AKAO         f2000000b1000000000000000000
 167 AKAO         f2000000b2000000000000000000
 181 AKAO         f2000000b3000000000000000000
 195 BMUSC        f601
 197 BITOFF       83308807
 201 MENU         49031500
 205 BATTLE       7000d401
 209 MAPJUMP      60e20025fbdeff320000
 219 AKAO         f2000000c1ff0000000000000000
 233 WAIT         245000
 236 MUSIC        f000
 238 AKAO         f2000000c1007f00000000000000
 252 IFUB         14d05b020930
 258 BITON        82308807
 262 BITOFF       83d05b02
 266 MHMMX        3e
 267 WMODE        52000101
 271 WMODE        52010001
 275 WMODE        52020001
 279 WMODE        52030201
 283 WAIT         240100
 286 REQ          0106c3
 289 REQ          0107c3
 292 WINDOW       5000100008001f013900
 302 MESSAGE      400003
 305 IFUB         14308805091b
 311 BITOFF       83308805
 315 WAIT         240400
 318 DSKCG        0e03
 320 MUSIC        f002
 322 WAIT         240800
 325 MAPJUMP      60e802f9ff6bfcf300e4
 335 JMPF         10cc
 337 IFUB         14d05206094c
 343 BITOFF       83d05206
 347 REQ          0105c4
 350 WAIT         241000
 353 WINDOW       500146007d00b4004900
 363 ASK          48050101020300
 370 MHMMX        3e
 371 IFUB         145000020010
 377 WAIT         240400
 380 BITON        82308805
 384 SETBYTE      80d00003
 388 MENU         49000e00
 392 BITOFF       83308805
 396 WAIT         240400
 399 DSKCG        0e03
 401 MUSIC        f002
 403 WAIT         240800
 406 MAPJUMP      60e802f9ff6bfcf300e4
 416 JMPF         107b
 418 IFUB         143086020922
 424 BITOFF       83308602
 428 WAIT         240400
 431 DSKCG        0e02
 433 WAIT         240800
 436 BITON        82308901
 440 MAPJUMP      607a02fdfeb213710000
 450 MUSIC        f003
 452 WAIT         240800
 455 JMPF         1054
 457 IFUB         14308804094e
 463 BITOFF       83308804
 467 REQ          0105c3
 470 WAIT         241000
 473 WINDOW       500146007d00b4004900
 483 ASK          48050101020300
 490 IFUB         145000020010
 496 WAIT         240400
 499 BITON        82308602
 503 SETBYTE      80d00002
 507 MENU         49000e00
 511 BITOFF       83308602
 515 WAIT         240400
 518 WAIT         240800
 521 BITON        82308901
 525 WAIT         240800
 528 MAPJUMP      607a02fdfeb213710000
 538 MUSIC        f003
 540 IFUB         1430830209c1
 546 UC           3301
 548 MENU2        4a01
 550 NFADE        250000000000000000
 559 AKAO         f2000000a4100000000000000000
 573 AKAO         f2000000a5100000000000000000
 587 AKAO         f2000000a3100000000000000000
 601 AKAO         f2000000c1100000000000000000
 615 WAIT         240600
 618 AKAO         f200000028400000000000000000
 632 AKAO         f200000029400000000000000000
 646 AKAO         f20000002a400000000000000000
 660 AKAO         f2000000a4017f00000000000000
 674 AKAO         f2000000a5017f00000000000000
 688 AKAO         f2000000a3017f00000000000000
 702 MUSIC        f000
 704 AKAO         f2000000c1017f00000000000000
 718 PMVIE        f82d
 720 MOVIE        f9
 721 WAIT         240300
 724 MULCK        f501
 726 MAPJUMP      602e02d7ff99015500f0
 736 JMPF         103e
 738 IFSW         162000007e020036
 746 AKAO         f2000000c1600000000000000000
 760 WAIT         243000
 763 MUSIC        f000
 765 AKAO         f2000000c1010000000000000000
 779 WAIT         240400
 782 MMBud        cd0003
 785 MENU         49001103
 789 MAPJUMP      600a0289fff0002200ff
 799 RET          00
total len 800