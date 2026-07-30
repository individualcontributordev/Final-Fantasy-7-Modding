---
name: ship-world-encounters
description: >-
  Builds and publishes world-map encounter Light/Standard/Dense ic-layer packs.
  Use when releasing world encounter mods, running build_all_rates / build_on_base
  under mods/world-map-random-encounters, or updating builder/manifest.json for
  world packs.
---

# Ship world-map encounter packs

## Preconditions

- `workspace/pristine/FINALFANTASY7_D1.bin` present
- `mods/world-map-random-encounters/VERSION` bumped when shipping a new release
- Stub playtested (Light/Standard/Dense feel OK)

## Commands

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only

python mods/world-map-random-encounters/scripts/build_all_rates.py --density all --discs 1
```

`exclusiveGroup`: `world-encounter-rate` (stacks with Field packs).

## After build — verify builder config (required before publish)

```bash
python scripts/verify_builder_config.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 --base clean \
  --addon world-encounter-25-vX.Y.Z
# also --base csr-v0.14.1 / highwind-v0.1.1 with matching -on-csr- / -on-highwind- pack ids
# must PASS per disc you ship
```

Optional zip smoke:

```bash
python scripts/verify_built_disc.py path/to/ff7-builder-d1+…/
# infers disc/base/addons from stamp + APPLIED.txt; CLI flags still override
```

**Zip verify rules** (see `docs/findings/2026-07-30-verify-built-disc-stacking.md`):

- Inference: CLI → builder stamp → APPLIED names via catalog.
- Ignores Mode2 EDC/ECC and base bytes later addons overwrite.

Then commit `builder/` (+ VERSION) → push → Pages.

## Do not

- Commit `.bin` / `.cue`
- Mix into `field-encounter-rate` exclusive group
