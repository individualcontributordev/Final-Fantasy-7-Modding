# D1 FIELD movie scan — crawl/missing-FMV candidates

Pristine NTSC-U. Method: LZS DAT → script section → PMVIE(0xF8)+MOVIE(0xF9) within 48 bytes.
D1 movie name = sorted MOVIE/ index (Makou NoN).

User already fixing: crawl sites + final descent BG movie (Makou delete Set+Play).
loslake3 / LOSLAKE3.DAT ids 57+58 confirmed (ONTRAIN.MOV + OPENING.BIN).

## How to use

1. Makou Find All "Play movie" / "Set next movie" on work bin to confirm (scan has false positives).
2. Prefer delete Set next movie + Play movie; keep waits/jumps/executes.
3. Do not engine-stub MOVIE.

## Tier 1 — priority (D1 id resolves to non-stream file)

These are the best automated matches for crawl / blank stare / broken BG movie.

| DAT | Map name | IDs → D1 file |
|-----|----------|---------------|
| COS_BTM2.DAT | cos_btm | 24=FSHIP2.BIN |
| LAS3_1.DAT | las3_1 | 55=NULL1MIN.DAT |
| LAS4_0.DAT | las4_0 | 25=FSHIP2N.BIN |
| LOSLAKE1.DAT | loslake | 25=FSHIP2N.BIN |
| LOSLAKE3.DAT | loslake | 58=OPENING.BIN |
| NMKIN_4.DAT | nmkin_4 | 69=STAFF2.BIN |
| ROOTMAP.DAT | rootmap | 24=FSHIP2.BIN |
| TRNAD_53.DAT | trnad_5 | 24=FSHIP2.BIN |
| ZMIND3.DAT | zmind3 | 68=STAFF.BIN |

### Notable among Tier 1

- LOSLAKE3.DAT: 58=OPENING.BIN (with 57=ONTRAIN nearby) — Bugenhagen lake FMV
- LAS3_1.DAT: 55=NULL1MIN.DAT — possible empty/min dummy
- LAS4_0.DAT: 25=FSHIP2N.BIN — Northern Cave / descent-adjacent assets often BIN placeholders on D1
- *STAFF*.BIN / FSHIP2*.BIN maps: credits/airship meta on wrong disc column
- CHANGE*.LZS / DISK*.LZS hits may be disc-change UI mixed into scan — verify in Makou before bulk-delete

## Tier 2 — OOB ids only (verify; many false positives)

Ids ≥72 on D1 file table. Confirm in Makou; do not mass-delete from this list alone.

| DAT | Map | OOB ids |
|-----|-----|---------|
| BLIN66_2.DAT | blin66_ | 89 |
| BUGIN2.DAT | bugin2�� | 234 |
| COLNE_5.DAT | colne_5 | 255 |
| COREL3.DAT | corel3 | 113 |
| COSIN2.DAT | cosin2 | 168 |
| FSHIP_1.DAT | fship_1 | 148 |
| GAMES_2.DAT | games_2 | 77,105 |
| JUNBIN1.DAT | junbin1 | 169 |
| JUNONE3.DAT | junone3 | 169 |
| JUNONE4.DAT | junone4 | 169 |
| JUNONE6.DAT | junone6 | 169 |
| JUNONR1.DAT | junonr1 | 136 |
| KURO_3.DAT | kuro_3 | 255 |
| LAS2_3.DAT | las2_3 | 255 |
| LIFE2.DAT | life2 | 255 |
| NIV_TI2.DAT | iv_ti2 | 101 |
| SANGO1.DAT | sango1 | 169 |
| SEMKIN_6.DAT | semkin_ | 254 |
| SNOW.DAT | snow | 224,254 |
| TRNAD_2.DAT | trnad_2 | 255 |
| UTTMPIN1.DAT | uttmpin | 156 |

## Tier 3 — stream OK on D1 (wrong clip possible, usually not crawl)

Count: 47 maps. Wrong D2/D3 FMV may play; optional polish only if annoying.

## Makou checklist (manual Find All)

Also search:

- Set next movie (triplet disc1/disc2/disc3)
- Play movie
- Background movie / continuous play variants if Makou labels them

Priority story areas if crawl remains after Tier 1 pass:

- Rocket / Fort Condor / Great Glacier / City of the Ancients
- Midgar raid / Sister Ray / Diamond Weapon (D2 movies)
- Northern Cave / sealed pillar / final descent (user in progress)
- Ending paths (D3 movies) if reachable without disc ask

## Related

- field-movie-trims.md
- docs/findings/2026-08-03-noswap-ioslake3-missing-fmv.md
