# Final Fantasy VII PSX add-on layers

This repository builds local `ic-layer-v1` add-ons for the
[disc builder](https://individualcontributor.dev/builder/). Run commands from
the repository root with Python 3.

## Inputs and outputs

Place clean NTSC-U raw MODE2/2352 images at:

```text
workspace/pristine/FINALFANTASY7_D1.bin
workspace/pristine/FINALFANTASY7_D2.bin
workspace/pristine/FINALFANTASY7_D3.bin
```

CSR, CSR+, and Highwind builds read the separate CSR checkout only through
`--csr-root` or:

```bash
export FF7_CSR_ROOT=/path/to/Final-Fantasy-7-CSR
```

Builds use disposable files below `workspace/iso-extract/` and publish pack
JSON below `builder/<pack-id>/`. Encounter and fanfare pack ids are stable
across versions:

```text
field-encounter-{0,25,50,75}
field-encounter-on-{csr,csr-plus,highwind}-{0,25,50,75}
world-encounter-{0,25,50,75}
world-encounter-on-{csr,csr-plus,highwind}-{0,25,50,75}
fanfare-skip
fanfare-skip-on-{csr,csr-plus,highwind}
```

## Build field, world, and fanfare add-ons

Valid bases are `clean`, `csr`, `csr-plus`, and `highwind`. Encounter density
is one of `off`, `light`, `standard`, `dense`, or `all`.

Clean discs 1–3:

```bash
python3 mods/field-random-encounters/scripts/build_on_base.py \
  --against clean --discs 1,2,3 --density all
python3 mods/world-map-random-encounters/scripts/build_on_base.py \
  --against clean --discs 1,2,3 --density all
python3 mods/fanfare-skip/scripts/build_on_base.py \
  --against clean --discs 1,2,3
```

One CSR-family base:

```bash
python3 mods/field-random-encounters/scripts/build_on_base.py \
  --against csr-plus --discs 1 --density all
python3 mods/world-map-random-encounters/scripts/build_on_base.py \
  --against highwind --discs 1 --density standard
python3 mods/fanfare-skip/scripts/build_on_base.py \
  --against csr --discs 1
```

Build fanfare skip for every supported base with:

```bash
python3 mods/fanfare-skip/scripts/build_on_base.py --against all --discs 1
```

Each build reconstructs its selected base locally, patches the extracted
overlay, injects it without moving ISO files, emits a layer against that exact
base, round-trip verifies it, writes `pack.json`, and updates
`builder/manifest.json`.

## Build a generic Makou add-on

Use the exact reconstructed builder base image. Optional `--layer` arguments
apply in command order before the editing checkpoint:

```bash
python3 mods/single-disc/scripts/prepare_working_bin.py \
  --base-image /path/to/reconstructed-base.bin \
  --layer /path/to/parent-addon.layer.json \
  --edc-reference workspace/pristine/FINALFANTASY7_D1.bin \
  --output-dir workspace/build/my-mod-work
```

Open `workspace/build/my-mod-work/02-working.bin` in Makou Reactor and save to
a new BIN. Keep `01-layer-stack.bin` unchanged: it is the layer's builder-side
parent.

```bash
python3 mods/single-disc/scripts/process_edited_bin.py \
  --edited-image /path/to/makou-saved.bin \
  --working-baseline workspace/build/my-mod-work/02-working.bin \
  --layer-base workspace/build/my-mod-work/01-layer-stack.bin \
  --edc-reference workspace/pristine/FINALFANTASY7_D1.bin \
  --output-dir workspace/build/my-mod-release \
  --pack-id my-mod \
  --name "My mod" \
  --version 0.1.0 \
  --compatible-base csr-plus
```

Release outputs are under `workspace/build/my-mod-release/02-release/`:
`image/` contains the hardware-test BIN/CUE, `verification/` contains the
builder reconstruction, and `pack/my-mod/` contains the publishable stable-id
pack. Copy `pack/my-mod/` to `builder/my-mod/`, add or replace its entry in
`builder/manifest.json`, then validate.

## Make an image safe for Makou

Prefer the unchanged pre-edit image as table evidence:

```bash
python3 mods/single-disc/scripts/make_makou_safe.py \
  /path/to/edited.bin \
  --table-baseline /path/to/unchanged.bin \
  --output workspace/build/makou-safe.bin
```

If no baseline exists, omit `--table-baseline`; ambiguous table records are
rejected instead of guessed. The command writes a new BIN, CUE, and JSON report
and never overwrites the input.

## Verify and publish

```bash
python3 scripts/validate_manifest.py
python3 scripts/verify_builder_config.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 \
  --base csr-plus \
  --addon fanfare-skip-on-csr-plus \
  --output workspace/build/verify.bin
python3 scripts/verify_iso_integrity.py workspace/build/verify.bin
```

Use `--csr-root /path/to/Final-Fantasy-7-CSR` when `FF7_CSR_ROOT` is unset.
Publish only the intended `builder/` JSON files. The hosted builder reads:

```text
https://individualcontributor.dev/Final-Fantasy-7-Modding/builder/manifest.json
```

## Script reference

| Script | Purpose | Example |
|---|---|---|
| `scripts/apply_layer.py` | Apply or round-trip check a layer | `python3 scripts/apply_layer.py base.bin layer.json --expect expected.bin` |
| `scripts/bin_diff_to_layer.py` | Diff exact parent and result | `python3 scripts/bin_diff_to_layer.py base.bin patched.bin -o out.layer.json --id my-mod-disc1` |
| `scripts/decompress_gzipps.py` | Extract an overlay payload | `python3 scripts/decompress_gzipps.py FIELD.BIN FIELD.BIN.dec` |
| `scripts/compress_gzipps.py` | Rebuild an overlay | `python3 scripts/compress_gzipps.py FIELD.BIN.dec FIELD.BIN FIELD.BIN.new` |
| `scripts/verify_iso_integrity.py` | Check ff7tk ISO layout constraints | `python3 scripts/verify_iso_integrity.py workspace/build/verify.bin` |
| `scripts/verify_builder_config.py` | Reconstruct a local selection | `python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin --disc 1 --base clean --output workspace/build/clean.bin` |
| `scripts/validate_manifest.py` | Validate publication references | `python3 scripts/validate_manifest.py builder/manifest.json` |
| `mods/field-random-encounters/scripts/apply_force_stub_rcnt2.py` | Patch decompressed FIELD.BIN | `python3 mods/field-random-encounters/scripts/apply_force_stub_rcnt2.py FIELD.BIN.dec --density light` |
| `mods/field-random-encounters/scripts/build_field_bin.py` | Build FIELD.BIN.new | `python3 mods/field-random-encounters/scripts/build_field_bin.py FIELD.BIN --density standard` |
| `mods/field-random-encounters/scripts/build_on_base.py` | Publish field packs | `python3 mods/field-random-encounters/scripts/build_on_base.py --against clean --discs 1 --density all` |
| `mods/world-map-random-encounters/scripts/apply_world_force_stub.py` | Patch decompressed WORLD.BIN | `python3 mods/world-map-random-encounters/scripts/apply_world_force_stub.py WORLD.BIN.dec --density light` |
| `mods/world-map-random-encounters/scripts/build_world_bin.py` | Build WORLD.BIN.new | `python3 mods/world-map-random-encounters/scripts/build_world_bin.py WORLD.BIN --density standard` |
| `mods/world-map-random-encounters/scripts/build_on_base.py` | Publish world packs | `python3 mods/world-map-random-encounters/scripts/build_on_base.py --against clean --discs 1 --density all` |
| `mods/fanfare-skip/scripts/apply_fanfare_skip.py` | Patch decompressed BATTLE.X | `python3 mods/fanfare-skip/scripts/apply_fanfare_skip.py BATTLE.X.dec --verify-only` |
| `mods/fanfare-skip/scripts/build_battle_x.py` | Build BATTLE.X.new | `python3 mods/fanfare-skip/scripts/build_battle_x.py BATTLE.X --output BATTLE.X.new` |
| `mods/fanfare-skip/scripts/build_on_base.py` | Publish fanfare packs | `python3 mods/fanfare-skip/scripts/build_on_base.py --against clean --discs 1` |
| `mods/single-disc/scripts/prepare_working_bin.py` | Create Makou checkpoints | `python3 mods/single-disc/scripts/prepare_working_bin.py --base-image base.bin --edc-reference workspace/pristine/FINALFANTASY7_D1.bin --output-dir workspace/build/work` |
| `mods/single-disc/scripts/process_edited_bin.py` | Build a generic release | `python3 mods/single-disc/scripts/process_edited_bin.py --edited-image edited.bin --working-baseline work/02-working.bin --layer-base work/01-layer-stack.bin --edc-reference workspace/pristine/FINALFANTASY7_D1.bin --output-dir release --pack-id my-mod --name "My mod" --version 0.1.0 --compatible-base clean` |
| `mods/single-disc/scripts/make_makou_safe.py` | Repair a Makou input copy | `python3 mods/single-disc/scripts/make_makou_safe.py input.bin --output workspace/build/makou-safe.bin` |
