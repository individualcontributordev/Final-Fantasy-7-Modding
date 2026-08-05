# CSR single-disc — manip movie whitelist (working)

**Pack (later):** single-disc-csr-manip-movies-v*
**Stack:** CSR base + single-disc-on-csr + this pack (no CSR+ scenes)
**Budget:** keep include total well under ~93 MB raw free after SNOVA (~80 MB target)

Status values: seed | candidate | include | exclude-* | deferred

User MB = ISO file size / 1024^2. Raw on disc is about user x 1.15.

## Seed (from repo analysis)

| Movie file | Disc | User MB | Why seeded | Field / scene (if known) | Status | Notes |
|------------|:----:|--------:|------------|--------------------------|--------|-------|
| LASTFLOR.MOV | D3 | 2.98 | CSR+ endgame removes; CSR LAS0_3 still has Play | LAS0_3 | include | Playtest seed v0.1.0 — D1 id 36 (JAIROFAL.MOV) |
| LAST4_3.BIN | D3 | 0.24 | same endgame diff | LAS0_3 | include | Playtest seed — D1 id 34 (GOLD7_2.MOV) |
| LASTMAP.BIN | D3 | 0.21 | same endgame diff | LAS0_3 | include | Playtest seed — D1 id 37 (JAIROFLY.MOV) |
| CANONHT2.MOV | D2 | 5.00 | CSR+ Hojo removes; CSR CANON_2 still has Play | CANON_2 | include | Playtest seed — D1 id 7 (CAR_1209.STR) |
| JUNSEA.STR | D2 | 1.21 | LOSLAKE1 (#637) Costa lake / manip | include | Playtest — D1 id 47 (MK8.STR); grew ISO slot |

**Not seeded:** CANONON.MOV — CSR base already removed from LOSLAKE1 (COTA FMV).
**Never include:** ENDING2E.MOV (~156 MB), other full endings — will not fit.

## Candidates (fill from CSR multi-disc play + Makou)

| Movie file | Disc | User MB | Field / map | Manip / reason | Status | Notes |
|------------|:----:|--------:|-------------|----------------|--------|-------|
| | | | | | | |

## Decisions — include (ship in movie pack)

| Movie file | Disc | User MB | Field / map | Confirmed by |
|------------|:----:|--------:|-------------|--------------|
| | | | | |

## Decisions — exclude

| Movie file | Status | Reason |
|------------|--------|--------|
| | | |

## Running total

Update after edits:

    python3 mods/single-disc/scripts/list_d2d3_only_movies.py --sum-whitelist

| Metric | Value |
|--------|------:|
| include count | |
| include user MB | |
| include approx raw MB | |
| headroom 80-min after SNOVA | ~93 MB raw |

## Session log

| Date | What checked | Result |
|------|--------------|--------|
| | | |


## Playtest pack (v0.1.0)

- Pack: single-disc-csr-manip-movies-v0.1.0
- Stack: csr-v0.14.1 + single-disc-on-csr-v0.1.1 + this pack (no CSR+ scenes)
- Method: overwrite D1 MOVIE id (sorted name index), shrink ISO size to source length
- Work bin: workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin
- Re-inject: python3 mods/single-disc/scripts/inject_movies_by_disc_id.py --d1 WORK.bin --manifest mods/single-disc/patches/csr-manip-movie-seed.txt --in-place

Side effect: D1 ids 7/34/36/37 no longer play original D1 clips (CAR_1209, GOLD7_2, JAIROFAL, JAIROFLY).

After playtest: add more include rows and re-run inject + rebuild layer.
