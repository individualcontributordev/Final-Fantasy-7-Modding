# Task: Smoke-test Fanfare Skip 0.1.5 play image

## Why

Repo is cleaned up:

- Bisect locked: **quiet FAN2 freezes**, **stub only does not**
- **0.1.5** packs built for clean + CSR + Highwind, discs 1-3 (BATTLE stub only)
- Live manifest enables **0.1.5**, disables freeze-shipping **0.1.4**

One DuckStation pass on the official 0.1.5 clean Disc 1 image confirms what players get.

## What you do

### 1. Pull

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

### 2. Make Disc 1 play image (pack already built)

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p workspace/iso-extract

python3 scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  builder/fanfare-skip-v0.1.5/layers/disc1.layer.json \
  -o workspace/iso-extract/ff7_d1_fanfare_skip_v015.bin
```

### 3. DuckStation

1. File → Open Image → workspace/iso-extract/ff7_d1_fanfare_skip_v015.bin
2. Same last-hit fight as before.
3. Fill Evidence.

No breakpoints.

## Evidence

```
held tone freeze: no
fanfare heard: yes
win poses: yes
loot/exp screens still OK: yes
notes: both field and world map
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git add docs/INSTRUCTIONS.md
git commit -m "ops: smoke-test fanfare-skip 0.1.5"
git push
```

Then say **check**.

Do **not** commit .bin images.
