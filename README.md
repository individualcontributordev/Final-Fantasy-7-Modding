# Final Fantasy VII PSX Modding

Published packs for the [disc builder](https://individualcontributor.dev/builder/).
Players never download a `.bin` from this repo — only `ic-layer-v1` JSON.

Removed notes and one-off scripts: [ARCHIVED.md](ARCHIVED.md).

## Init a workspace

```bash
bash scripts/init_workspace.sh
```

That clones `../Final-Fantasy-7-CSR` (bases) and `../individualcontributordev.github.io` (builder UI) if they are missing. Copy your NTSC-U discs to `workspace/pristine/FINALFANTASY7_D{1,2,3}.bin`.

## CSR (3-disc base)

Lives in `Final-Fantasy-7-CSR`. From that repo:

```bash
python3 scripts/apply_layer.py pristine/FINALFANTASY7_D1.bin builder/csr/layers/disc1.layer.json -o cache/csr/FINALFANTASY7_D1.bin
# edit cache/csr/FINALFANTASY7_DN.bin in Makou, then:
python3 scripts/repair_mode2_edc.py --pristine pristine/FINALFANTASY7_D1.bin --input cache/csr/FINALFANTASY7_D1.bin --in-place
python3 scripts/build_csr_base_layers.py cache/csr --version X.Y.Z
```

See `Final-Fantasy-7-CSR/docs/MANUAL_CSR_BASE_BUILD_GUIDE.md`.

## CSR+ (collapsed base)

```bash
python3 mods/single-disc/scripts/build_csrplus_staged.py --csr-root ../Final-Fantasy-7-CSR \
  prepare --run-name my-csrplus
# Open 03-working/CSRPLUS_D1.bin in Makou. Save a NEW file.
python3 mods/single-disc/scripts/build_csrplus_staged.py --csr-root ../Final-Fantasy-7-CSR \
  finalize --run-dir ../Final-Fantasy-7-CSR/build/csr-plus/my-csrplus \
  --edited-image /path/to/makou-saved.bin --version X.Y.Z
```

If you overwrite the working BIN: `prepare --run-name my-csrplus --resume`.
Copy `05-release-candidate/pack/csr-plus/` into `../Final-Fantasy-7-CSR/builder/csr-plus/` and bump `builder/manifest.json`.

## Highwind (collapsed base)

Same shape as CSR+, different script and filenames:

```bash
python3 mods/single-disc/scripts/build_highwind_staged.py --csr-root ../Final-Fantasy-7-CSR \
  prepare --run-name my-highwind
# Open 03-working/HIGHWIND_D1.bin in Makou. Save a NEW file.
python3 mods/single-disc/scripts/build_highwind_staged.py --csr-root ../Final-Fantasy-7-CSR \
  finalize --run-dir ../Final-Fantasy-7-CSR/build/highwind/my-highwind \
  --edited-image /path/to/makou-saved.bin --version X.Y.Z
```

Copy `05-release-candidate/pack/highwind/` into `../Final-Fantasy-7-CSR/builder/highwind/`.

## Field / world encounters

Generated rate patches, not Makou maps. One pack per base × rate (`0/25/50/75`).

```bash
python3 mods/field-random-encounters/scripts/build_on_base.py --against csr-plus --discs 1 --density all
python3 mods/world-map-random-encounters/scripts/build_on_base.py --against highwind --discs 1 --density standard
```

`--against` is `clean|csr|csr-plus|highwind`. Writes `builder/` in this repo.

## Fanfare skip

Engine patch per base (`clean|csr|csr-plus|highwind|all`):

```bash
python3 mods/fanfare-skip/scripts/build_on_base.py --against all --discs 1
```

## New Makou addon on an existing base

```bash
python3 mods/single-disc/scripts/prepare_working_bin.py \
  --base-image /path/to/reconstructed-parent.bin \
  --edc-reference workspace/pristine/FINALFANTASY7_D1.bin \
  --output-dir /tmp/mod-working
# Edit 02-working.bin in Makou; save a NEW file.
python3 mods/single-disc/scripts/process_edited_bin.py \
  --edited-image /path/to/makou-saved.bin \
  --working-baseline /tmp/mod-working/02-working.bin \
  --layer-base /tmp/mod-working/01-layer-stack.bin \
  --edc-reference workspace/pristine/FINALFANTASY7_D1.bin \
  --output-dir /tmp/mod-release \
  --pack-id my-mod --name "My mod" --version 0.1.0 --kind mod \
  --compatible-base csr-plus
```

`--layer-base` is the image the builder already has before this pack. Do not pass `--snova-disc3` for addons.

Repair an arbitrary BIN for Makou: `python3 mods/single-disc/scripts/make_makou_safe.py --input in.bin --output out.bin`.

## Publish and prove the builder path

1. Copy the candidate `pack/<id>/` into this repo's `builder/` (addons) or the CSR repo `builder/` (bases).
2. Update `builder/manifest.json` version and disc paths.
3. Commit JSON only — never `.bin`.
4. Rebuild locally as the site does:

```bash
python3 scripts/verify_builder_config.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 --base csr-plus \
  --addon fanfare-skip-on-csr-plus \
  -o /tmp/builder-check.bin
```

`--base` / `--addon` are pack `id`s from the two manifests.
`python3 scripts/validate_manifest.py` checks this repo's catalog.

GitHub Pages deploys `builder/` from `main`. After push, confirm versions at
`https://individualcontributor.dev/Final-Fantasy-7-Modding/builder/manifest.json`
(or the CSR catalog URL for bases).
