# Task: Playtest CSR single-disc + movie seed pack

## Stack

    Base: csr-v0.14.1
    Add-ons:
      single-disc-on-csr-v0.1.1
      single-disc-csr-manip-movies-v0.1.0
    CSR+ scenes: none

## What the movie pack does

Overwrites four D1 MOVIE ids (same PMVIE index as on D2/D3) with:

| Source | Id | Overwrites D1 slot |
|--------|---:|--------------------|
| D3 LASTFLOR.MOV | 36 | JAIROFAL.MOV |
| D3 LAST4_3.BIN | 34 | GOLD7_2.MOV |
| D3 LASTMAP.BIN | 37 | JAIROFLY.MOV |
| D2 CANONHT2.MOV | 7 | CAR_1209.STR |

Those D1 clips are sacrificed so CSR scripts that still Play those ids get the multi-disc stream.

## Optional local re-inject

    python3 mods/single-disc/scripts/inject_movies_by_disc_id.py \
      --d1 workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin \
      --manifest mods/single-disc/patches/csr-manip-movie-seed.txt \
      --in-place

Site builder: CSR + both packs above; Disc 1 for this playtest.

## Playtest focus

1. Endgame/FD-adjacent LASTFLOR path on CSR-alone
2. Hojo path CANONHT2 if that scene still Plays
3. No crawl/softlock on those maps
4. Note any other wrong/missing multi-disc FMV — add name + map to
   mods/single-disc/patches/csr-manip-movie-whitelist.md as candidate

## Not done yet

- BLACKBGB Ask on CSR core pack still pending Makou
- More movies after playtest
- Highwind single-disc pack

## Evidence

    Builder stack:
    Scenes checked:
    Movies OK:
    Still wrong / crawl (name + map):
    Notes:

Say check with results.
