# Engineer's Build Guide (CLI only)

How to build/verify disc images from repo files the same way the builder site
does, using only the CLI scripts below. For mod-specific pipelines see each
mod's `scripts/` + `README.md`; this page covers the shared tools.

## Prereqs

- `workspace/pristine/FINALFANTASY7_D{1,2,3}.bin` (gitignored, your own copy)
- Sibling checkout: `../Final-Fantasy-7-CSR` (for CSR base layers/manifest)
- `git pull --ff-only` in both repos before building

## Two ways a `.bin` gets made

| Method | What it is | Tool |
|--------|------------|------|
| **Work bin** | Direct injection/patching scripts write bytes straight into a copy of pristine/CSR. Used to *develop* a mod. | `mods/<name>/scripts/build_*.py` |
| **Layered bin** | Stack `ic-layer-v1` JSON diffs onto pristine, exactly like the browser builder. Used to *verify what players get*. | `scripts/apply_layer.py`, `scripts/verify_builder_config.py` |

A release is only "done" once its work-bin content has been diffed into a
layer (`bin_diff_to_layer.py`) and the layered bin matches — see
`docs/04-workflow.md` step "Shipping to the disc builder".

## Reproduce the builder site locally

`scripts/verify_builder_config.py` stacks layers exactly like the site: pick
a base id and 0+ addon ids from `builder/manifest.json` (this repo) or
`../Final-Fantasy-7-CSR/builder/manifest.json`.

```bash
cd Final-Fantasy-7-Modding
git pull --ff-only

python3 scripts/verify_builder_config.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 --base highwind \
  --addon fanfare-skip-on-highwind \
  -o workspace/iso-extract/single-disc-builder-check.bin
```

- `--base` / `--addon` values are pack `id`s from `manifest.json` (`bases` /
  `addons` arrays), not version strings you invent.
- Add more `--addon` flags to mirror a specific player selection.
- This does **not** apply a manifest's `autoIncludeWhen` auto-stacking logic
  for you — pass every addon id explicitly that you expect to be included.
- Output is a bootable `.bin`; load it in DuckStation the same as any other.

If you only need to apply one known layer file (no manifest lookup):

```bash
python3 scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  builder/highwind/layers/disc1.layer.json \
  -o workspace/iso-extract/out.bin
```

Stack more layers by re-running with the previous output as the new
"pristine" input, in the same order the manifest lists them.

## Smoke-test a zip downloaded from the live site

If you have an actual builder-site zip/output folder (with `APPLIED.txt`
next to the `.bin`), verify its content matches the catalog without
re-deriving config:

```bash
python3 scripts/verify_built_disc.py path/to/builder-output-folder/
# or directly:
python3 scripts/verify_built_disc.py path/to/extracted-or.bin
```

- Reads config **only** from `APPLIED.txt` (Base / Add-on lines) — no
  `--disc`/`--base`/`--addon` flags to pass.
- Confirms every record from the resolved layer stack is present on the
  image (ignores EDC/ECC and base bytes a later addon intentionally
  overwrites).
- Run this **before publish** for every ship skill (see each mod's SKILL.md).

## Build a mod's work bin directly (dev loop)

Each mod owns its own work-bin builder under `mods/<name>/scripts/`. Example
for single-disc:

```bash
python3 mods/single-disc/scripts/build_work_bin.py \
  -o workspace/iso-extract/single-disc-work.bin
```

(BLACKBGB's DSKCG removal is applied automatically from the committed
`mods/single-disc/patches/BLACKBGB.dskcg-removal.layer.json` ic-layer-v1
diff -- pass `--blackbgb-manual-bin path/to/other.layer.json` only to
override it.)

Run `python3 mods/<name>/scripts/<script>.py -h` for flags — every script has
argparse `--help` and a docstring explaining what it does and why.

## Publish: diff a work bin into a layer

```bash
python3 scripts/bin_diff_to_layer.py \
  <base.bin> <modified.bin> \
  -o builder/<pack-id>/layers/disc<N>.layer.json \
  --id <pack-id>-disc<N> \
  --description "<short description>"
```

- `<base.bin>` is whatever the pack's `compatibleBases` says (pristine or a
  CSR base) — **not** always pristine. Diffing against the wrong base
  produces a layer that corrupts other players' builds.
- After regenerating a layer, re-run `verify_builder_config.py` with that
  pack's id to confirm it still applies cleanly before bumping
  `manifest.json`/`pack.json` versions.

## Manifest gotcha: `autoIncludeWhen` ignores `enabled: false`

If an addon is retired (`"enabled": false`) but still has an
`autoIncludeWhen` block matching a live pack, the **site will still stack
it** — the builder does not check `enabled` before auto-including. To retire
an addon fully, also repoint its `autoIncludeWhen` match to a dead sentinel
id (see any occurrence of `DISABLED-pending-*` in `manifest.json` for the
pattern) or delete the block entirely.

## Build every base × mod permutation (CLI cookbook)

Base IDs: `clean` (Unmodified, implicit — no layer, no script), `csr` (3-disc,
built in `Final-Fantasy-7-CSR`), `csr-plus` (single-disc), `highwind`
(single-disc). `csr` and `csr-plus`/`highwind` addons live in different repos'
`manifest.json` — CSR-only scene add-ons in `Final-Fantasy-7-CSR`, everything
else (`field-encounter-*`, `world-encounter-*`, `fanfare-skip*`,
`single-disc-*`) in this repo's `builder/manifest.json`.

### Field encounter rate (`mods/field-random-encounters`)

One script builds any base × rate combo; `--density` picks 0/25/50/75%
(interactive prompt if omitted):

```bash
python3 mods/field-random-encounters/scripts/build_on_base.py \
  --against clean --discs 1 --density standard
python3 mods/field-random-encounters/scripts/build_on_base.py \
  --against csr --discs 1 --density all       # builds all 4 rates
python3 mods/field-random-encounters/scripts/build_on_base.py \
  --against csr-plus --discs 1 --density light
python3 mods/field-random-encounters/scripts/build_on_base.py \
  --against highwind --discs 1 --density dense
```

`--against` is one of `clean|csr|csr-plus|highwind`; writes/updates
`builder/field-encounter[-on-<base>]-<rate>/` and `builder/manifest.json`.

### World-map encounter rate (`mods/world-map-random-encounters`)

Same shape as field, plus a batch driver for every base at once:

```bash
python3 mods/world-map-random-encounters/scripts/build_on_base.py \
  --against clean --discs 1 --density all
python3 mods/world-map-random-encounters/scripts/build_on_base.py \
  --against highwind --discs 1 --density standard

# all 4 bases (clean/csr/csr-plus/highwind) in one go:
python3 mods/world-map-random-encounters/scripts/build_all_rates.py \
  --density all --discs 1
```

### Fanfare skip (`mods/fanfare-skip`)

No density — single on/off layer per base:

```bash
python3 mods/fanfare-skip/scripts/build_on_base.py --against clean --discs 1
python3 mods/fanfare-skip/scripts/build_on_base.py --against csr --discs 1
python3 mods/fanfare-skip/scripts/build_on_base.py --against csr-plus --discs 1
python3 mods/fanfare-skip/scripts/build_on_base.py --against highwind --discs 1
python3 mods/fanfare-skip/scripts/build_on_base.py --against all --discs 1
```

### Single-disc bases themselves (csr-plus, highwind)

These aren't addons — see "Collapsed single-disc bases" in
`Final-Fantasy-7-CSR/docs/CREATE_ADDON_FROM_MAKOU.md` for the full writeup.
Rebuild both in one pass:

```bash
python3 mods/single-disc/scripts/build_collapsed_bases.py
# csr-plus's intermediate .bin already cached from a prior run:
python3 mods/single-disc/scripts/build_collapsed_bases.py --skip-csrplus
```

For an inspectable CSR+ rebuild intended for Makou edits, use the staged
pipeline instead. It reconstructs all three CSR discs, reconstructs each
historical CSR+ scene trim on its original disc, preserves every intermediate
image under the CSR repo's gitignored `build/`, and reserves enough space for
Makou/ff7tk to recompress `FIELD.BIN` after a field changes size:

```bash
python3 mods/single-disc/scripts/build_csrplus_staged.py prepare
# Edit the reported 07-editable/FINALFANTASY7_D1.bin and save a new file.
python3 mods/single-disc/scripts/build_csrplus_staged.py finalize \
  --run-dir ../Final-Fantasy-7-CSR/build/csr-plus/<run> \
  --edited-image /path/to/makou-saved.bin
```

The final command writes a candidate publish layer and a `.bin`/`.cue` console
test image inside the same run. It never changes published `builder/` files.
Disc 2/3 layers are not applied at raw offsets to Disc 1; the pipeline extracts
their selected fields and injects them by ISO path because each disc has a
different physical layout.

#### Chainable CSR+ stages

Use these when you need to inspect, compare, or bisect every boundary. Each
script refuses to overwrite an existing artifact:

```bash
CSR=../Final-Fantasy-7-CSR
RUN="$CSR/build/csr-plus/debug-01"

# 1. Reconstruct current/historical CSR discs and each scene-trim disc/layer.
python3 mods/single-disc/scripts/csrplus_stage_1_sources.py \
  --csr-root "$CSR" --output-dir "$RUN/01-sources"

# 2. Merge Disc 2/3 fields by ISO path and fix FIELD/WORLD lookup tables.
python3 mods/single-disc/scripts/csrplus_stage_2_collapse.py \
  --csr-root "$CSR" \
  --sources-dir "$RUN/01-sources" \
  --output-dir "$RUN/02-collapse"

# 3. Reserve Makou FIELD.BIN space, repair EDC/ECC, and validate the image.
python3 mods/single-disc/scripts/prepare_working_bin.py \
  --base-image "$RUN/02-collapse/06-field-world-tables-fixed.bin" \
  --edc-reference "$CSR/pristine/FINALFANTASY7_D1.bin" \
  --output-dir "$RUN/03-working"

# Edit 03-working/02-working.bin in Makou and save a NEW file.

# 4. Normalize and validate Makou's saved image.
python3 mods/single-disc/scripts/stabilize_working_bin.py \
  --input /path/to/makou-saved.bin \
  --table-baseline "$RUN/03-working/02-working.bin" \
  --edc-reference "$CSR/pristine/FINALFANTASY7_D1.bin" \
  --output "$RUN/04-stabilized/disc1.bin" \
  --report "$RUN/04-stabilized/stage-report.json"

# 5. CSR+ only: append SNOVA after Makou is finished.
python3 mods/single-disc/scripts/csrplus_stage_5_snova.py \
  --input "$RUN/04-stabilized/disc1.bin" \
  --disc3 "$CSR/pristine/FINALFANTASY7_D3.bin" \
  --output "$RUN/05-snova/disc1.bin" \
  --report "$RUN/05-snova/stage-report.json"

# 6. Build candidate pack JSON plus the hardware-test BIN/CUE.
python3 mods/single-disc/scripts/build_release_artifacts.py \
  --input "$RUN/05-snova/disc1.bin" \
  --layer-base "$CSR/pristine/FINALFANTASY7_D1.bin" \
  --edc-reference "$CSR/pristine/FINALFANTASY7_D1.bin" \
  --output-dir "$RUN/06-release" \
  --pack-id csr-plus --name "CSR+ (single-disc)" \
  --version 0.1.2 --kind base
```

Every stage writes `stage-report.json` with hashes and relevant validation
results. The intermediate BIN from one stage is the explicit input to the next.

#### Simple working-BIN workflow for another base or mod

Build a Makou-safe image from an exact base plus zero or more layers:

```bash
python3 mods/single-disc/scripts/prepare_working_bin.py \
  --base-image /path/to/exact-layer-base.bin \
  --layer /path/to/existing-change.layer.json \
  --edc-reference /path/to/retail-disc.bin \
  --output-dir /path/to/build/working
```

Edit `02-working.bin`, save a new file, then normalize and package it in one
command:

```bash
python3 mods/single-disc/scripts/process_edited_bin.py \
  --edited-image /path/to/makou-saved.bin \
  --working-baseline /path/to/build/working/02-working.bin \
  --layer-base /path/to/build/working/02-working.bin \
  --edc-reference /path/to/retail-disc.bin \
  --output-dir /path/to/build/release \
  --pack-id my-mod --name "My mod" --version 0.1.0 --kind mod \
  --compatible-base csr
```

`--layer-base` is the image used for the byte diff. For a base release it is
normally retail. For a mod, use the unchanged `02-working.bin` that you opened
in Makou; it represents the fully reconstructed compatible base with the same
safe archive layout. Passing the wrong layer base can produce valid JSON that
corrupts a player's disc.

### CSR base / CSR+ scenes / CSR-only single-disc addon

Live in `Final-Fantasy-7-CSR`, not this repo — see that repo's
`docs/MANUAL_CSR_BASE_BUILD_GUIDE.md` (new CSR/Highwind base version) and
`docs/CREATE_ADDON_FROM_MAKOU.md` (CSR+ scene add-ons, Makou-authored).

### Verify any permutation before publishing

Stack whatever base + addon ids you just built, exactly like the site would:

```bash
python3 scripts/verify_builder_config.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 --base highwind \
  --addon field-encounter-on-highwind-50 \
  --addon fanfare-skip-on-highwind \
  -o workspace/iso-extract/check.bin
```

Pass every addon id explicitly — `autoIncludeWhen` auto-stacking is not
applied by this script. Then load `check.bin` in DuckStation.

### Full base × mod matrix (`clean`/`csr`/`csr-plus`/`highwind`)

| Mod family | `clean` | `csr` | `csr-plus` | `highwind` |
|---|---|---|---|---|
| Field encounter rate | ✅ `field-encounter-<rate>` | ✅ `field-encounter-on-csr-<rate>` | ✅ `field-encounter-on-csr-plus-<rate>` | ✅ `field-encounter-on-highwind-<rate>` |
| World encounter rate | ✅ `world-encounter-<rate>` | ✅ `world-encounter-on-csr-<rate>` | ✅ `world-encounter-on-csr-plus-<rate>` | ✅ `world-encounter-on-highwind-<rate>` |
| Fanfare skip | ✅ `fanfare-skip` | ✅ `fanfare-skip-on-csr` | ✅ `fanfare-skip-on-csr-plus` | ✅ `fanfare-skip-on-highwind` |
| Single-disc | n/a (already 1 disc) | ⛔ `single-disc-on-csr` (`enabled: false`, retired) | n/a (already single-disc base) | n/a (already single-disc base) |
| CSR+ scenes (Hojo/Aerith/Endgame) | ⛔ not applicable | ✅ free checkboxes (CSR repo) | baked into the base already | baked into the base already |

`<rate>` = `0`/`25`/`50`/`75`. Rows marked n/a mean the combination doesn't
exist as an addon because the behavior is either baked into the base or
structurally impossible (e.g. you can't add "single-disc" to a base that's
already single-disc).

## Where to look next

| Need | Doc |
|------|-----|
| Full edit→rebuild→test loop for engine/field patches | `docs/04-workflow.md` |
| Regression test suite | `scripts/README.md` → "Regression tests" |
| All shared CLI tools | `scripts/README.md` |
| Starting a brand-new mod | `docs/06-new-mod-research.md` |
| Single-disc specifics | `mods/single-disc/README.md`, skill `ship-single-disc` |
