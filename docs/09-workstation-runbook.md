# Workstation runbook (CSR+, Highwind, Makou)

Manual commands for the other workstation. Scripts live in this repo.
BIN artifacts go under the CSR repo’s gitignored `build/`. Do not commit
BIN/CUE files.

Expected checkouts (sibling directories):

- `Final-Fantasy-7-Modding` — this repo (build scripts)
- `Final-Fantasy-7-CSR` — bases, layers, `pristine/`, `build/`

Retail images you supply (never committed):

- `Final-Fantasy-7-CSR/pristine/FINALFANTASY7_D1.bin`
- `Final-Fantasy-7-CSR/pristine/FINALFANTASY7_D2.bin`
- `Final-Fantasy-7-CSR/pristine/FINALFANTASY7_D3.bin`

Highwind stage 1 needs CSR git history: it reads retired Disc 2/3 layers
from a pinned commit. A shallow clone without that history will fail.

```bash
cd ~/Final-Fantasy-7-Modding
git pull --ff-only
git -C ../Final-Fantasy-7-CSR pull --ff-only
CSR=../Final-Fantasy-7-CSR
```

CLI cookbook and publish hash checks: [08-engineer-build-guide.md](08-engineer-build-guide.md).
Hardware burn ladder: [07-hardware-burn.md](07-hardware-burn.md).

## Which job

| Job | Use |
|-----|-----|
| Edit CSR+ or Highwind from a rebuilt working BIN | `prepare` then Makou then `finalize` |
| Makou “Invalid archive” on an existing FF7 raw BIN | `make_makou_safe.py` |
| Inspect or bisect every pipeline stage | chainable stage scripts |
| Addon on an existing base | `prepare_working_bin.py` then `process_edited_bin.py` |
| Ship a layer players can rebuild | copy candidate pack into `builder/`, then `verify_builder_config.py` |

Do not use `mods/single-disc/scripts/build_collapsed_bases.py` for new work.
It mutates CSR `builder/` in place and can skip field merges.

## Rules that prevent the old failures

- Never overwrite the working BIN Makou opened. Always **File → Save** to a new path.
- SNOVA is injected **after** Makou, not before.
- `--layer-base` is the image the builder already has before this layer (retail for a new **base**; `01-layer-stack.bin` for a **mod**).
- `--working-baseline` is the safe image you opened in Makou (`02-working.bin` or the `prepare` checkpoint).
- Stage scripts refuse to overwrite. Rerun with a new `--run-name` or output directory.
- Stages extract Disc 2/3 fields by ISO path. Do not apply another disc’s layer at raw offsets onto Disc 1.

---

## 1. Edit CSR+ or Highwind (normal path)

`prepare` rebuilds sources, collapses later-disc fields onto Disc 1 by ISO
path, fixes FIELD/WORLD lookup tables, reserves Makou `FIELD.BIN` space, and
repairs EDC/ECC. `finalize` restabilizes the Makou save, injects SNOVA, aliases
the Disc 3 ending, then writes a **candidate** pack plus a console BIN/CUE. It
does not write into `builder/`.

If you only need a Makou-openable image, stop after `prepare`.

### The ending stage

`finalize` writes `04-finalize/03-endings.bin`, placing the truncated ENDING2E
stream at its hardcoded Disc 3 LBA (197242) in the `MOVIE/MONITOR.STR` slot.
This runs **before** the layer is diffed, so the ending's sectors travel inside
the published layer. That is required: builder users only load pristine Disc 1,
so anything absent from the layer cannot exist on their disc.

Reusing the slot makes that extent run into `MOVIE/NVLMK.MOV`. The layout check
allows exactly that one overlap and still fails on any other overlap or
duplicate LBA. Pass `--no-ending-alias` only to deliberately publish a disc
with no ending.

### CSR+

```bash
python3 mods/single-disc/scripts/build_csrplus_staged.py prepare \
  --csr-root "$CSR" --run-name csrplus-edit-01
```

Open `$CSR/build/csr-plus/csrplus-edit-01/03-working/CSRPLUS_D1.bin` in Makou. Save to a **new** file.

```bash
python3 mods/single-disc/scripts/build_csrplus_staged.py finalize \
  --csr-root "$CSR" \
  --run-dir "$CSR/build/csr-plus/csrplus-edit-01" \
  --edited-image /path/to/makou-saved.bin \
  --version 0.1.2
```

### Highwind

```bash
python3 mods/single-disc/scripts/build_highwind_staged.py prepare \
  --csr-root "$CSR" --run-name highwind-edit-01
```

Open `$CSR/build/highwind/highwind-edit-01/03-working/HIGHWIND_D1.bin`. Save to a **new** file.

```bash
python3 mods/single-disc/scripts/build_highwind_staged.py finalize \
  --csr-root "$CSR" \
  --run-dir "$CSR/build/highwind/highwind-edit-01" \
  --edited-image /path/to/highwind-makou-saved.bin \
  --version 0.2.1
```

Highwind rebuilds the same Disc 1 collapse as CSR+ from CSR discs and scene
trims, then copies Highwind's extra early Disc 1 fields. It does not read
`builder/csr-plus/` or a CSR+ `build/` run.

---

## Where to Makou-edit (CSR+ and Highwind)

Both bases may gain more field/script changes on Disc 1, 2, or 3 *content*.
That content still ships as one Disc 1 image. Two routes:

### Default for a burnable disc (most stable)

Collapse first, then edit the **single** working BIN, then finalize.

1. `prepare` (sources → collapse → Makou-safe `03-working`)
2. Open `03-working/CSRPLUS_D1.bin` or `03-working/HIGHWIND_D1.bin`
3. Save Makou to a **new** file
4. `finalize` (stabilize → SNOVA → layer vs retail D1 → BIN/CUE)

Use this for almost all new work, including later-game maps that already live
on the collapsed Disc 1. One ISO, one `FIELD.BIN`, SNOVA only after Makou,
EDC/ECC repaired on the image you will burn.

Do not Makou the SNOVA image. Do not burn a Makou save without `finalize`.

### Per-disc first (only when the filename is disc-specific)

Same `FIELD/NAME.DAT` can differ on Disc 2 vs Disc 3. If you must author the
disc-correct payload before the merge:

1. Run stage 1 only (`csrplus_stage_1_sources.py` or `highwind_stage_1_sources.py`)
2. `make_makou_safe.py` on that disc's BIN (`01-current-csr/FINALFANTASY7_D{n}.bin`,
   or Highwind extras at `06-highwind-d1-extras/FINALFANTASY7_D1.bin`)
3. Edit, save a new file, playtest that disc image
4. Copy the saved BIN into a **new** sources directory (stages refuse overwrite)
5. Collapse → `prepare_working_bin.py` → optional extra Makou on `03-working` →
   stabilize → SNOVA → release

After collapse, later-disc files exist only as the merge picked them. Further
edits to those maps belong on `03-working`.

Highwind extras (`HIGHWIND_D1_EXTRA_FIELDS`) are copied after collapse. Edit
them either on the extras image (step 2) or on `03-working`. Do not expect a
Highwind D2/D3 merge; there isn't one.

---

## 2. Repair an existing FF7 raw BIN for Makou

Use when you already have a MODE2/2352 FF7 `.bin` that Makou rejects as
“Invalid archive”, and you are not rebuilding from layers. No retail
comparison is required.

```bash
python3 mods/single-disc/scripts/make_makou_safe.py \
  /path/to/problem.bin \
  -o /path/to/problem-makou-safe.bin
```

If you still have the unchanged image from before the bad save:

```bash
python3 mods/single-disc/scripts/make_makou_safe.py \
  /path/to/problem.bin \
  --table-baseline /path/to/pre-edit.bin \
  -o /path/to/problem-makou-safe.bin
```

The input is never overwritten. Existing output paths are refused. The
command writes a `.cue` and `<output>.makou-safe.json`.

Open the **output** in Makou, not the original. This is not a generic
CD-image converter. It stops if a FIELD/WORLD table record is ambiguous or
the ISO already has duplicate/overlapping extents.

After you save in Makou, do **not** burn that save raw. Run
`stabilize_working_bin.py`, `process_edited_bin.py`, or the matching
`finalize` so tables and EDC/ECC are repaired again.

---

## 3. Inspect every stage (debugging)

Each output directory must not already exist. Full command blocks:
[08-engineer-build-guide.md](08-engineer-build-guide.md) (“Chainable CSR+
stages” and “Chainable Highwind stages”).

Order:

1. Base-specific sources: `csrplus_stage_1_sources.py` or `highwind_stage_1_sources.py`
2. Collapse: `csrplus_stage_2_collapse.py` or `highwind_stage_2_collapse.py`
3. `prepare_working_bin.py`
4. Edit `02-working.bin` in Makou; save to a new path
5. `stabilize_working_bin.py`
6. `csrplus_stage_5_snova.py` (filename is historical; both collapsed bases use it)
7. `build_release_artifacts.py`

CSR+ collapse artifact: `06-field-world-tables-fixed.bin`.
Highwind collapse artifact: `08-field-world-tables-fixed.bin`.

For a **mod on an existing base**:

```bash
python3 mods/single-disc/scripts/prepare_working_bin.py \
  --base-image /path/to/exact-layer-base.bin \
  --layer /path/to/existing-change.layer.json \
  --edc-reference "$CSR/pristine/FINALFANTASY7_D1.bin" \
  --output-dir /path/to/build/working
```

`--base-image` must be the exact image the first layer targets (reconstructed
CSR / CSR+ / Highwind, not always retail).

Edit `02-working.bin`, save a new file, then:

```bash
python3 mods/single-disc/scripts/process_edited_bin.py \
  --edited-image /path/to/makou-saved.bin \
  --working-baseline /path/to/build/working/02-working.bin \
  --layer-base /path/to/build/working/01-layer-stack.bin \
  --edc-reference "$CSR/pristine/FINALFANTASY7_D1.bin" \
  --output-dir /path/to/build/release \
  --pack-id my-mod --name "My mod" --version 0.1.0 --kind mod \
  --compatible-base csr
```

`--snova-disc3` only for collapsed CSR+ or Highwind **bases**, not typical addons.

`01-layer-stack.bin` is the builder-side parent of a new mod layer.
`02-working.bin` has synchronized tables, spare `FIELD.BIN` capacity, and
repaired EDC/ECC; that is the file to open in Makou.

---

## 4. Publish and prove the builder can rebuild it

Do not copy a Makou save into `builder/`. Copy only the candidate pack after
`stage-report.json` shows:

- `layerRoundTrip: pass`
- release SHA-256 equals `builderRebuildSha256`
- EDC/ECC, disc bounds, and ISO layout checks passed

### Copy Highwind candidate into the CSR catalog

After `build_highwind_staged.py finalize`:

```bash
RUN="$CSR/build/highwind/highwind-edit-01"
diff -ru "$CSR/builder/highwind" "$RUN/05-release-candidate/pack/highwind"

cp "$RUN/05-release-candidate/pack/highwind/pack.json" \
  "$CSR/builder/highwind/pack.json"
cp "$RUN/05-release-candidate/pack/highwind/VERSION" \
  "$CSR/builder/highwind/VERSION"
cp "$RUN/05-release-candidate/pack/highwind/layers/disc1.layer.json" \
  "$CSR/builder/highwind/layers/disc1.layer.json"
```

Update the matching `bases` entry in `$CSR/builder/manifest.json` (version,
name, blurb, Disc 1 path). CSR+ uses `$CSR/builder/csr-plus/` the same way.
Addons use this repo’s `builder/<pack-id>/` and the `addons` array in
`builder/manifest.json`.

Commit JSON, `VERSION`, and manifest only.

### Reconstruct through the catalog

```bash
python3 scripts/verify_builder_config.py \
  --csr-root "$CSR" \
  --pristine "$CSR/pristine/FINALFANTASY7_D1.bin" \
  --disc 1 --base highwind \
  -o "$RUN/published-rebuild.bin"

shasum -a 256 \
  "$RUN/05-release-candidate/image/highwind-disc1.bin" \
  "$RUN/published-rebuild.bin"
```

Those hashes must match. That proves the site can rebuild the layer stack.
It does not prove a burned disc works.

Pass every addon id explicitly; this script does not apply `autoIncludeWhen`.

### Hardware (required before calling a burn “done”)

1. Boot and exercise edited transitions in DuckStation Safe Mode.
2. Same BIN/CUE on MiSTer PSX if available.
3. Burn the verified CUE at a conservative speed with write verification.
4. Boot the critical path on the target console / optical drive.
5. Record image SHA-256, burner/media, console model, and result.

See [07-hardware-burn.md](07-hardware-burn.md).
