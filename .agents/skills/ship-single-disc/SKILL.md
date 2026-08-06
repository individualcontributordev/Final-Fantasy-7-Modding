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

1. List collisions: finding `docs/findings/2026-08-06-csr-multi-disc-field-edits.md`
2. Structured compare (not size alone):

```bash
python3 scripts/compare_field_dat.py csr:1 csr:2 --field DEL1 -o /tmp/del1.md
python3 scripts/compare_field_dat.py --batch-collisions
```

3. Put the correct CSR disc’s `FIELD/<NAME>.DAT` on the D1 work image
   (`replace_file_padded` / layer rebuild). Enforce prefer file; never overwrite
   a `d1` pick with a D2 copy by accident.
4. Verify:

```bash
# example: core stack DEL1 == CSR D1 DEL1
python3 scripts/compare_field_dat.py  # or INSTRUCTIONS confirm snippet
```

## Playtest bin

```bash
python3 mods/single-disc/scripts/build_playtest_bin.py
```

Open only `workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue`.

## Packs

| Pack | Role |
|------|------|
| `single-disc-on-csr-v*` | Core (fields, SNOVA, asks, trims) on CSR D1 |
| `single-disc-csr-manip-movies-v*` | Movie body + LBA aliases (may split base/delta) |

Core layer is **diff vs CSR Disc 1 base**, not vs pristine.

## Before publish

```bash
python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 --base csr-v0.14.1 --addon single-disc-on-csr-v0.1.1
# stack movies pack if shipping manip
```

Update `mods/single-disc/CHANGELOG.md` (newest top), `VERSION`, `builder/manifest.json`.

## Findings to keep in mind

- DEL1: CSR D1 has 442 trim; CSR D2 vs pris can be pad-only — still D1≠D2 scripts
- LOSLAKE1: absolute LBA 250450 needs CANONON Form2 alias on D1
- See rule `single-disc-fields.mdc`

## Human ops

Write one atomic task to `docs/INSTRUCTIONS.md` (what + why + COPY-PASTE), push,
short chat pointer. Plain English; one map per pass when merging fields.
