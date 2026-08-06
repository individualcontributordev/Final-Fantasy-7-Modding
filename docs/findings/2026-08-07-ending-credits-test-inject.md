# Ending credits test inject (DuckStation oversize bin)

**Date:** 2026-08-07  
**Status:** test image built; not a CD-sized pack

## Approach

PMVIE uses **`MINT/MOVIE_ID.BIN` row index** (D1 has 54 rows), not ISO filename sort order.

On **Disc 3** the ending streams are:

| MOVIE_ID id | File |
|------------:|------|
| 25 | ENDING01.MOV |
| 26 | ENDING3E.MOV |
| 29 | ENDING2E.MOV |

On **current single-disc D1 playtest** those same ids pointed at small files:

| id | Was | Now (test) |
|---:|-----|------------|
| 25 | SMK.STR (~0.6 MiB) | ENDING01 bytes |
| 26 | SOUTHMK.MOV (~5.7 MiB) | ENDING3E bytes |
| 29 | MONITOR.STR (~2.2 MiB) | ENDING2E bytes |

Injection: `inject_movies_by_disc_id.py` with  
`mods/single-disc/patches/ending-credits-test-manifest.txt`  
(grow Form2 raw + patch MOVIE_ID LBA/size).

Verified: sector0 and full payload match pristine D3 for all three.

## Image size

| Bin | Bytes | Notes |
|-----|------:|-------|
| Normal playtest | 766340400 | CD-oriented |
| **ending test** | **1008274176** (~1008 MB) | ~429k sectors; **over** 80-min CD (~−69k sectors) |

No pure “reclaim on CD” yet: slots were too small, so streams were **appended** (grow). True CD fit still needs cutting other data first.

## How to playtest

```bash
# already produced locally as:
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Open that **.cue** in DuckStation (not the normal movies cue).  
After final battle, ids 25/26/29 should stream real D3 endings instead of garbage/black.

Rebuild from scratch:

```bash
python3 mods/single-disc/scripts/build_playtest_bin.py
cp -f workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin \
      workspace/iso-extract/ff7_d1_playtest_ending_test.bin
python3 mods/single-disc/scripts/inject_movies_by_disc_id.py \
  --d1 workspace/iso-extract/ff7_d1_playtest_ending_test.bin \
  --manifest mods/single-disc/patches/ending-credits-test-manifest.txt \
  --in-place
# write cue if missing (FILE name = bin name)
```

## Caveats

- Overwrites D1 movie ids 25/26/29 — anything on D1 that legitimately used SMK/SOUTHMK/MONITOR streams will show ending video instead.
- Not for burn/CDN until size is solved.
- Not in builder packs yet.
