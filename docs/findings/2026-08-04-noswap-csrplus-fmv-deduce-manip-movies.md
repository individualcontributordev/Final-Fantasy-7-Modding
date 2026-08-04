# Finding: Deduce CSR-only manip movies from CSR+ COTA / endgame layers

**Date:** 2026-08-04
**Status:** measured (PMVIE 0xF8 + MOVIE 0xF9 within 48 bytes; movie id via sorted MOVIE/)

## Hypothesis

CSR+ scene packs remove field FMVs that CSR base still plays. Diff those packs vs CSR
to build the CSR-alone no-disc-swap manip-movie whitelist (D2/D3 files to put on D1).

## Packs checked

| Pack | Disc | FIELD touched |
|------|------|----------------|
| csr-plus-scene-cota-fd-manip-v0.1.0 | 2 | LOSLAKE1.DAT, BLIN70_4.DAT |
| csr-plus-scene-endgame-fd-manip-v0.1.0 | 3 | LAS0_3, LAS2_1, LAS4_0, LAS4_1 |

Method: apply csr-v0.14.1 then CSR+ layer; compare PMVIE+MOVIE pairs; resolve ids on that disc;
flag files missing from D1 MOVIE/.

## COTA FD (waterfall / Bugen phone + FMV)

Changelog: leaving waterfall with Bugen — no phone call and **FMV removed** (List impact).

| Image | LOSLAKE1 D2-only PMVIE pairs |
|-------|------------------------------|
| pristine D2 | JUNSEA.STR, DUMCRUSH.MOV, **CANONON.MOV** (14.37 MB) |
| CSR base | JUNSEA.STR, DUMCRUSH.MOV — **CANONON already gone** |
| CSR + COTA | same as CSR (JUNSEA + DUMCRUSH kept) |

CSR+ COTA pair-id multiset only drops **OOB** ids vs CSR — **no additional D2-only movie
file removed**. The FMV called out in the changelog was already stripped by **CSR base**
(CANONON.MOV on LOSLAKE1).

**CSR-only movie implication from COTA pack: none** (nothing COTA removes that CSR still plays).

BLIN70_4: CSR and CSR+ both still reference PHOENIX.MOV (D2-only, kept).

## Endgame FD (disc 3)

Changelog: cliff slide from Highwind removed; green gas trimmed (List); Tifa ledge jump;
pre-FD talk removed.

### LAS0_3 — clear movie-id drops vs CSR

| Movie | Size (user) | On D1? | CSR | CSR+ endgame |
|-------|------------:|:------:|:---:|:------------:|
| LASTFLOR.MOV | 2.98 MB | no | play | **removed** |
| LAST4_3.BIN | 0.24 MB | no | play | **removed** |
| LASTMAP.BIN | 0.21 MB | no | play | **removed** |
| D_ROPEIN.MOV | 4.29 MB | yes | play | removed |
| CHANGE2.LZS | 0.11 MB | yes | play | removed |

### LAS2_1 / LAS4_0 / LAS4_1

No large D3-only stream cleanly dropped that CSR still plays. LAS4_1 scan even
*gains* an ENDING2E pair (likely false positive after script rewrite). Cliff/gas/Tifa
trims are mostly non-movie (dialog/wait/jump) or already absent on CSR for those maps.

**CSR-only candidates from endgame pack:** LASTFLOR.MOV (~3 MB) + tiny BIN stubs
(~0.7 MB). All fit easily in ~93 MB SNOVA headroom.

## Side note: Hojo FD (not requested, same method)

CANON_2: CSR+ removes **CANONHT2.MOV** (5.00 MB, D2-only) and WHITE2.BIN (0.24 MB).
That is a real CSR-alone whitelist candidate if Hojo pack is treated the same way.

## Bottom line

| Source | Adds CSR-alone D1 movie copies? |
|--------|----------------------------------|
| COTA FD layer vs CSR | **No** — FMV already cut on CSR base (CANONON) |
| Endgame FD layer vs CSR | **Yes, small** — LASTFLOR.MOV (+ tiny BIN) |
| Full CSR manip set | **Not** fully determined by these two packs alone |

Cannot build a full CSR manip-movie pack from COTA+endgame diffs only. For CSR-alone
later: start with LASTFLOR (+ optional BIN) from endgame; add other manips (and Hojo
CANONHT2 if needed) from a wider CSR play / known manip list — not "everything CSR+
touches."

## Related

- 2026-08-04-noswap-csr-manip-movies-pack-split.md (deferred pack)
- 2026-08-04-noswap-ship-csrplus-highwind-first.md
- mods/no-disc-swap/patches/field-movie-d2d3-missing-on-d1.md
