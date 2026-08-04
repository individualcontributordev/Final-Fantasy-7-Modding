# Finding: ioslake3 missing FMV — D1 movie IDs are wrong streams

**Date:** 2026-08-03
**Status:** root-caused from Makou dump + MOVIE dir listing
**Map:** ioslake3 — S0 Main, GameMoment == 1398

## Symptom

Bugenhagen on-field (animated/idle). FMV should play; does not. Not a hard freeze.

## Script (operator dump in INSTRUCTIONS)

If GameMoment == 1398:
- Set next movie: No57 (D1), loslake1 (D2), No57 (D3)
- Play movie
- Set next movie: No58 (D1), lslmv (D2), No58 (D3)
- Play movie
- Jump to map loslake1 (#637)

## Root cause

Makou No57/No58 are movie table indices, not missing filenames.

| Index | D1 file (pristine list order) | D2 intended |
|------:|-------------------------------|-------------|
| 57 | ONTRAIN.MOV (~3.9 MB) | LOSLAKE1.MOV (~6.0 MB) |
| 58 | OPENING.BIN (~149 KB, not a normal FMV) | LSLMV.STR (~1.8 MB) |

On D1-only single-disc, Play movie uses the D1 column → wrong/unplayable
streams → no scene FMV, field left up. Script can still finish waits and
Jump to loslake1 if MOVIE wait completes.

D2-only assets: MOVIE/LOSLAKE1.MOV, MOVIE/LSLMV.STR (not on D1/D3).

## Options

| Option | Effort | Result |
|--------|--------|--------|
| A. Leave vanilla | none | Missing FMV; continue if jump fires |
| B. Makou trim Play movie (+ Set next movie) | small | No empty stare; keep Execute/Wait/Jump |
| C. Copy D2 LOSLAKE1 + LSLMV onto D1 + fix IDs | large | Correct video |

Clean pack default: B for polish; A if shipping minimal.
Do not engine-stub MOVIE 0xF9.

## Recommended Makou edit (option B)

In ioslake3 S0 Main, GameMoment 1398 block only:

Delete both Set next movie lines and both Play movie lines.

Keep: Execute script lines (mf + Untitled), all Wait frames,
Execute script #7, Jump to loslake1.

Do not touch Label 1 / other GameMoment paths unless playtest shows a problem.

## Pack rebuild

After edit on combined work bin: inject SNOVA if needed, build_clean_d1_layer,
verify_builder_config, push, new builder zip.

## Related

- 2026-08-03-single-disc-fmv-wait-vs-stream.md
- mods/single-disc/patches/field-movie-trims.md
