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

## After build

1. `git status` — only `builder/**/*.json` (and VERSION if bumped)
2. Commit + push (auto-commit rule applies)
3. Wait for Pages; confirm https://individualcontributor.dev/builder/ lists the packs
4. Optional Windows smoke on a built zip (Mac writes task to `docs/windows-last-task.md` first):

```bash
python scripts/verify_built_disc.py "/path/to/built/FINALFANTASY7_D1.bin"
# FIELD stub@0xbb7c=YES for Light/Standard/Dense field packs on that image
```

## If CSR base ids changed

Rebuild against the new ids so `compatibleBases` stay correct. Old packs can stay `"enabled": true` until explicitly disabled in `builder/manifest.json`.

## Do not

- Reintroduce PPF / Windows patcher UI
- Put patch notes only in chat — stub notes go under `mods/field-random-encounters/patches/`
- Commit disc images
