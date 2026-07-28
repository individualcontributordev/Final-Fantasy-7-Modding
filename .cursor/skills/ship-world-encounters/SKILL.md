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

## After build

1. Commit `builder/` JSON (+ VERSION if bumped)
2. Push; wait for Pages; confirm builder UI lists world packs

## Do not

- Commit `.bin` / `.cue`
- Mix into `field-encounter-rate` exclusive group
