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

### Collapsed CSR+ and Highwind bases

`build_collapsed_bases.py` is retained for historical investigation. New work
uses the staged pipelines because they preserve every checkpoint and stop when
a field does not fit instead of silently publishing a partial merge.

For an inspectable CSR+ rebuild intended for Makou edits, the staged pipeline
reconstructs all three CSR discs, reconstructs each
historical CSR+ scene trim on its original disc, preserves every intermediate
image under the CSR repo's gitignored `build/`, and reserves enough space for
Makou/ff7tk to recompress `FIELD.BIN` after a field changes size:

```bash
python3 mods/single-disc/scripts/build_csrplus_staged.py prepare \
  --run-name csrplus-v0.1.2
# Edit the reported working BIN and save a new file.
python3 mods/single-disc/scripts/build_csrplus_staged.py finalize \
  --run-dir ../Final-Fantasy-7-CSR/build/csr-plus/csrplus-v0.1.2 \
  --edited-image /path/to/makou-saved.bin \
  --version 0.1.2
```

Highwind uses the same safety and release functions. Its source stage
reconstructs the retired v0.2.0 Disc 1/2/3 layers and restores only the field
payloads that its first collapsed release intentionally borrowed from CSR+:

```bash
python3 mods/single-disc/scripts/build_highwind_staged.py prepare \
  --run-name highwind-v0.2.1
# Edit build/highwind/highwind-v0.2.1/03-working/HIGHWIND_D1.bin.
python3 mods/single-disc/scripts/build_highwind_staged.py finalize \
  --run-dir ../Final-Fantasy-7-CSR/build/highwind/highwind-v0.2.1 \
  --edited-image /path/to/highwind-makou-saved.bin \
  --version 0.2.1
```

Each final command writes a candidate pack, release BIN/CUE, independent
builder-rebuild BIN/CUE, hashes, and verification reports inside the run. It
never changes published `builder/` files.
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

# 5. Append SNOVA after Makou is finished (also used by Highwind).
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

#### Chainable Highwind stages

The source and collapse stages are Highwind-specific. Stages 3 onward are the
same reusable commands shown above:

```bash
CSR=../Final-Fantasy-7-CSR
RUN="$CSR/build/highwind/debug-01"

# 1. Reconstruct retired Highwind D1/D2/D3 and pinned shared fields.
python3 mods/single-disc/scripts/highwind_stage_1_sources.py \
  --csr-root "$CSR" --output-dir "$RUN/01-sources"

# 2. Merge unambiguous later-disc fields, shared scenes, and fix lookup tables.
python3 mods/single-disc/scripts/highwind_stage_2_collapse.py \
  --csr-root "$CSR" \
  --sources-dir "$RUN/01-sources" \
  --output-dir "$RUN/02-collapse"

# 3. Create the image to open in Makou.
python3 mods/single-disc/scripts/prepare_working_bin.py \
  --base-image "$RUN/02-collapse/04-field-world-tables-fixed.bin" \
  --edc-reference "$CSR/pristine/FINALFANTASY7_D1.bin" \
  --output-dir "$RUN/03-working"

# Edit 03-working/02-working.bin and save to a new path.

# 4. Normalize Makou's save.
python3 mods/single-disc/scripts/stabilize_working_bin.py \
  --input /path/to/highwind-makou-saved.bin \
  --table-baseline "$RUN/03-working/02-working.bin" \
  --edc-reference "$CSR/pristine/FINALFANTASY7_D1.bin" \
  --output "$RUN/04-stabilized/disc1.bin" \
  --report "$RUN/04-stabilized/stage-report.json"

# 5. Inject SNOVA after editing.
python3 mods/single-disc/scripts/csrplus_stage_5_snova.py \
  --input "$RUN/04-stabilized/disc1.bin" \
  --disc3 "$CSR/pristine/FINALFANTASY7_D3.bin" \
  --output "$RUN/05-snova/disc1.bin" \
  --report "$RUN/05-snova/stage-report.json"

# 6. Diff against retail because Highwind is a base, then verify reconstruction.
python3 mods/single-disc/scripts/build_release_artifacts.py \
  --input "$RUN/05-snova/disc1.bin" \
  --layer-base "$CSR/pristine/FINALFANTASY7_D1.bin" \
  --edc-reference "$CSR/pristine/FINALFANTASY7_D1.bin" \
  --output-dir "$RUN/06-release" \
  --pack-id highwind --name "Highwind" \
  --version 0.2.1 --kind base \
  --blurb "Heavily shortened story, collapsed onto Disc 1."
```

Highwind's `stage-report.json` deliberately lists fields retained from Disc 1.
When both later discs differ, choosing either whole-file payload could replace
early-game behavior with a later-game script. The current policy matches the
published Highwind build: keep Disc 1 until a field-specific verdict is
playtested. Before producing its output, the collapse stage also compares all
787 rebuilt `FIELD/*.DAT` payloads with the pinned published baseline.

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
  --layer-base /path/to/build/working/01-layer-stack.bin \
  --edc-reference /path/to/retail-disc.bin \
  --output-dir /path/to/build/release \
  --pack-id my-mod --name "My mod" --version 0.1.0 --kind mod \
  --compatible-base csr
```

`--working-baseline` preserves the safe layout used while stabilizing Makou's
save. `--layer-base` has a different role: it is the exact builder image before
the new layer. For a base release that is normally retail; for a mod created
with `prepare_working_bin.py`, it is normally `01-layer-stack.bin`. The
reservation and repairs added to `02-working.bin` then become part of the new
layer and are reproduced for players. Passing the wrong layer base can produce
valid JSON that corrupts a player's disc.

#### Repair an existing BIN for Makou

When you only have an FF7 raw BIN, create a separate repaired copy:

```bash
python3 mods/single-disc/scripts/make_makou_safe.py \
  /path/to/problem.bin \
  -o /path/to/problem-makou-safe.bin
```

No retail or pristine comparison is required. The script:

1. infers and repairs stale FIELD.BIN/WORLD.BIN lookup records;
2. reserves FIELD.BIN recompression headroom;
3. verifies Makou's lookup and YAMADA preconditions;
4. recalculates every recognized Mode 2 Form 1 EDC/ECC footer;
5. validates PVD size and rejects duplicate or overlapping ISO extents;
6. writes a CUE and `<output>.makou-safe.json` report.

If you kept the unchanged image that existed before the problematic Makou
save, use it as a stronger table reference:

```bash
python3 mods/single-disc/scripts/make_makou_safe.py \
  /path/to/problem.bin \
  --table-baseline /path/to/pre-edit.bin \
  -o /path/to/problem-makou-safe.bin
```

The input is never overwritten, and existing outputs are refused. This is an
FF7 PSX raw MODE2/2352 repair tool, not a universal CD-image converter. It
stops when a table record is ambiguous or the filesystem is already
overlapping; those cases require a known-good pre-edit image or reconstruction
from layers.

#### Publish a candidate pack

Do not publish directly from a Makou save. Publish only the `pack/<pack-id>/`
directory emitted by `build_release_artifacts.py` after its
`stage-report.json` says:

- `layerRoundTrip: pass`;
- release and builder-rebuild SHA-256 values are identical;
- EDC/ECC, disc bounds, and ISO layout checks passed.

For Highwind, review the candidate before copying it into the CSR catalog:

```bash
RUN=../Final-Fantasy-7-CSR/build/highwind/highwind-v0.2.1
diff -ru \
  ../Final-Fantasy-7-CSR/builder/highwind \
  "$RUN/05-release-candidate/pack/highwind"

cp "$RUN/05-release-candidate/pack/highwind/pack.json" \
  ../Final-Fantasy-7-CSR/builder/highwind/pack.json
cp "$RUN/05-release-candidate/pack/highwind/VERSION" \
  ../Final-Fantasy-7-CSR/builder/highwind/VERSION
cp "$RUN/05-release-candidate/pack/highwind/layers/disc1.layer.json" \
  ../Final-Fantasy-7-CSR/builder/highwind/layers/disc1.layer.json
```

Then update the matching `bases` entry in
`Final-Fantasy-7-CSR/builder/manifest.json` to the same version, name, blurb,
and Disc 1 path. Add-on packs use the same process in this repo's
`builder/<pack-id>/` and `addons` manifest array. Never commit BIN/CUE files;
only layer JSON, pack metadata, VERSION, and manifest changes are published.

#### Verify the published builder path

After copying the candidate, reconstruct it through the catalog resolver:

```bash
python3 scripts/verify_builder_config.py \
  --csr-root ../Final-Fantasy-7-CSR \
  --pristine ../Final-Fantasy-7-CSR/pristine/FINALFANTASY7_D1.bin \
  --disc 1 --base highwind \
  -o ../Final-Fantasy-7-CSR/build/highwind/highwind-v0.2.1/published-rebuild.bin

shasum -a 256 \
  ../Final-Fantasy-7-CSR/build/highwind/highwind-v0.2.1/05-release-candidate/image/highwind-disc1.bin \
  ../Final-Fantasy-7-CSR/build/highwind/highwind-v0.2.1/published-rebuild.bin
```

The hashes must match. If the browser builder performs a final EDC/ECC repair,
compare again after running the same repair on both images; repaired footer
bytes are derived data, while user-data mismatches indicate a wrong layer
base, path, order, or stale manifest.

Builder reconstruction proves distribution correctness, not hardware
playability. Complete the verification ladder from `docs/07-hardware-burn.md`:

1. Boot and exercise edited transitions in DuckStation Safe Mode.
2. Test the same BIN/CUE on MiSTer PSX if available.
3. Burn the verified CUE at a conservative speed with write verification.
4. Boot and play the critical path on the target console/optical drive.
5. Record the image SHA-256, burner/media, console model, and result.

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
