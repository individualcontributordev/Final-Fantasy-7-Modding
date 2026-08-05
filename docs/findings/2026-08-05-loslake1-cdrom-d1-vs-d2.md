# LOSLAKE1 FMV: single-disc D1 vs real D2 CD-ROM logs

**Date:** 2026-08-05  
**Logs:** `docs/logs single disc 1.txt`, `docs/logs real disc 2.txt`  
**Bins:** playtest `ff7_d1_playtest_csr_sd_movies.bin` (766084032), pristine D2

## DuckStation sector vs ISO LBA

`Read sector N` is MSF absolute (= ISO LBA + 150).

Example: D2 CANONON ISO LBA **250450** → DS sector **250600**.

## CD streams during LOSLAKE1 FMV

| Disc | DS sectors (long stream) | Maps to |
|------|--------------------------|---------|
| Real D2 | **250600–257296** (6697) | **MOVIE/CANONON.MOV** (ISO 250450–257808) |
| Single D1 playtest | **250600–252128** (1529) | **MOVIE/RCKTFAIL.MOV** (ISO 245435–251857), then a bit of JAIROFLY |

Same start sector **250600** on both. On D2 that is CANONON. On D1 that absolute LBA is mid-RCKTFAIL (offset 5015 into the file).

Single-disc log **never** reads JAIROFAL/CANONON data at **318357** (+150 → 318507).

D1 also loads field LOSLAKE1/2 assets (~109954–110130). D2 log sample is almost only the FMV stream.

## MOVIE_ID slot 47 (20-byte records)

| Disc | Slot 47 LBA | File |
|------|------------:|------|
| Pristine D1 | 258385 | vanilla JAIROFAL (short) |
| Playtest D1 | **318357** | JAIROFAL file = pack CANONON bytes |
| Real D2 | **250450** | CANONON |

Playtest table is patched correctly. CD does not use 318357 for this play.

Slot covering DS start on D1: **slot 45** RCKTFAIL (245435…), not 47.

## Conclusion

Wrong picture is **not** a failed CANONON→JAIROFAL inject and **not** bad MOVIE_ID slot 47.

Player seeks absolute **~250450** (D2 CANONON LBA). On D1 layout that is RCKTFAIL → rocket-on-pad look.

Likely causes to check next:

1. Field/CSR path supplies D2 LBA 250450 (hardcoded / wrong disc table) instead of reading D1 MOVIE_ID[47].
2. Movie id used at stream start is not 47 (e.g. 45) despite earlier entity dump.
3. Separate movie LBA path ignores MINT/MOVIE_ID.BIN.

## Fix shipped (v0.1.1)

**Pack:** `builder/single-disc-csr-manip-movies-v0.1.1`
**Tool:** `mods/single-disc/scripts/alias_d2_seek_lba_on_d1.py`

Chose absolute-LBA alias: write CANONON at ISO **250450**, relocate overlapping JAIROFLY to EOF + MOVIE_ID patch.
Keeps JAIROFAL inject for id-47 path. Overwrites RCKTFAIL tail (accepted CSR manip tradeoff until engine seek uses MOVIE_ID[47]).

Playtest: `build_playtest_bin.py` checks `_user(img, 250450) == CANONON[:2048]`.
