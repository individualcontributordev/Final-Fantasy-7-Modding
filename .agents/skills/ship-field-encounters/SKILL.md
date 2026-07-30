---
name: ship-field-encounters
description: >-
  Builds and publishes Field encounter Light/Standard/Dense ic-layer packs for
  the disc builder. Use when releasing field encounter mods, rebuilding after a
  CSR base id change, running build_all_rates / build_on_base, or updating
  builder/manifest.json in Final-Fantasy-7-Modding.
---

# Ship Field encounter packs

## Preconditions

- `workspace/pristine/FINALFANTASY7_D1.bin` present (gitignored)
- `mods/field-random-encounters/VERSION` bumped when shipping a new release
- Know which CSR base ids are live (CSR Pages `builder/manifest.json`) if stacking on CSR

## Preferred commands

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only

# Interactive: Light / Standard / Dense / All (+ all againsts by default)
python mods/field-random-encounters/scripts/build_all_rates.py

# One against + one density (omit --density to prompt)
# against: clean | csr | highwind  (csr-plus base is retired)
python mods/field-random-encounters/scripts/build_on_base.py --against highwind --discs 1
python mods/field-random-encounters/scripts/build_on_base.py --against clean --density light --discs 1
```

Densities are **presets**, not free-form `%`. Invalid: `--density 1`. Valid: `light` / `standard` / `dense` / `all` (or 25 / 50 / 75).

## After build — verify builder config (required before publish)

Stack the pack like the site builder (needs CSR sibling repo + pristine bin):

```bash
# clean Light disc 1 example — use the pack ids you just built
python scripts/verify_builder_config.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 --base clean \
  --addon field-encounter-25-vX.Y.Z

# CSR / Highwind variants:
#   --base csr-v0.14.1 --addon field-encounter-on-csr-25-vX.Y.Z
#   --base highwind-v0.1.1 --addon field-encounter-on-highwind-25-vX.Y.Z
```

Must print `PASS` for each base/disc you ship. Wrong `compatibleBases` or missing disc layer fails here.

Optional post-builder zip smoke:

```bash
# Prefer extract folder or stamped .bin — infers disc/base/addons from name + APPLIED.txt
python scripts/verify_built_disc.py "/path/to/ff7-builder-d1+…/"
# Overrides still work if needed: --disc 1 --base clean --addon field-encounter-25-vX.Y.Z
```

**Zip verify rules** (see `docs/findings/2026-07-30-verify-built-disc-stacking.md`):

- Inference order: CLI → builder stamp (`ff7-builder-dN+base+addons…`) → APPLIED display names via catalog.
- Ignores Mode2 EDC/ECC (`sector_off >= 2072`) and **base** user-bytes later addons overwrite.

Then: `git status` → commit `builder/` (+ VERSION) → push → Pages.

## If CSR base ids changed

Rebuild against the new ids so `compatibleBases` stay correct. Old packs can stay `"enabled": true` until explicitly disabled in `builder/manifest.json`.

## Do not

- Reintroduce PPF / Windows patcher UI
- Put patch notes only in chat — stub notes go under `mods/field-random-encounters/patches/`
- Commit disc images
