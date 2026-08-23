# Engineer's Build Guide (no agent required)

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
  --disc 1 --base csr-v0.14.2 \
  --addon single-disc-on-csr \
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
  builder/single-disc-on-csr/layers/disc1.layer.json \
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
  -o workspace/iso-extract/single-disc-work.bin \
  --blackbgb-manual-bin workspace/iso-extract/BLACKBGB.manual.dat
```

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

## Where to look next

| Need | Doc |
|------|-----|
| Full edit→rebuild→test loop for engine/field patches | `docs/04-workflow.md` |
| Regression test suite | `scripts/README.md` → "Regression tests" |
| All shared CLI tools | `scripts/README.md` |
| Starting a brand-new mod | `docs/06-new-mod-research.md` |
| Single-disc specifics | `mods/single-disc/README.md`, skill `ship-single-disc` |
