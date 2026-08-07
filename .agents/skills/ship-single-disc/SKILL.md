---
name: ship-single-disc
description: Build and verify single-disc-on-CSR packs (fields, SNOVA, manip movies)
---

# Ship single-disc (on CSR)

## When to use

Publishing or fixing **single-disc** for CSR base: field files on one D1 image,
Ask removal, SNOVA, optional manip-movies, playtest bin.

## Inputs

- `workspace/pristine/FINALFANTASY7_D{1,2,3}.bin`
- Sibling CSR: `../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/discN.layer.json`
- Prefer list: `mods/single-disc/patches/csr-field-disc-prefer.txt`

## Field maps shared across CSR discs

Tools index: `scripts/README.md`. Prefer listed CLIs over ad-hoc Python.

1. List collisions: `docs/findings/2026-08-06-csr-multi-disc-field-edits.md`
2. Structured compare (not size alone):

```bash
python3 scripts/compare_field_dat.py csr:1 csr:2 --field DEL1 -o /tmp/del1.md
python3 scripts/compare_field_dat.py --batch-collisions
```

3. Install the correct CSR disc’s map on the D1 work image:

```bash
python3 scripts/extract_field_dat.py --from csr:1 --field DEL1 -o /tmp/DEL1.DAT
python3 scripts/put_field_dat.py --bin work.bin --field DEL1 --dat /tmp/DEL1.DAT
```

Enforce `mods/single-disc/patches/csr-field-disc-prefer.txt` (d1/d2/review).
4. Verify with `compare_field_dat.py` (paths or csr:N sides) or INSTRUCTIONS confirm snippet.

## Playtest bin

```bash
python3 mods/single-disc/scripts/build_playtest_bin.py
```

Open only `workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue`.

## Packs (three families — do not merge)

| Pack | Role |
|------|------|
| `single-disc-on-csr-v*` | Main pack (fields, SNOVA, asks, trims) on CSR D1 |
| `single-disc-csr-manip-movies-v*` | **CSR alone** speedrun movies. Latest cumulative; auto only without CSR+ scenes. |
| `single-disc-endings-v0.1.0-part1`…`part7` | **Own mod:** ending/credits on D1. Auto with Single-disc on CSR (with or without CSR+). Multi-part for size. Also `compatibleBases` Highwind for later. |

Core layer is **diff vs CSR Disc 1 base**, not vs pristine.

## Before publish

```bash
python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 --base csr-v0.14.1 \
  --addon single-disc-on-csr-v0.1.2 \
  --addon single-disc-csr-manip-movies-v0.1.2 \
  --addon single-disc-endings-v0.1.0-part1 \
  --addon single-disc-endings-v0.1.0-part2 \
  --addon single-disc-endings-v0.1.0-part3 \
  --addon single-disc-endings-v0.1.0-part4 \
  --addon single-disc-endings-v0.1.0-part5 \
  --addon single-disc-endings-v0.1.0-part6 \
  --addon single-disc-endings-v0.1.0-part7
# CSR alone stack. CSR+: omit manip-movies, keep endings parts.
# Rebuild endings layers: build_ending_credits_test_bin.py && build_ending_credits_layers.py
```

Update `mods/single-disc/CHANGELOG.md` (newest top), `VERSION`, `builder/manifest.json`.

## Findings to keep in mind

- DEL1: CSR D1 has 442 trim; CSR D2 vs pris can be pad-only — still D1≠D2 scripts
- Lake cutscene needs lake movie bytes at one fixed disc place; endings pack restores that after writing long credits
- See rule `single-disc-fields.mdc` and `plain-english.mdc` for chat

## Human ops

Write one atomic task to `docs/INSTRUCTIONS.md` (what + why + COPY-PASTE), push,
short chat pointer. Plain English; one map per pass when merging fields.
