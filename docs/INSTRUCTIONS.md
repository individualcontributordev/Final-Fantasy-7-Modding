# Task: Verify Fanfare Skip 0.1.5 (stub only, no quiet FAN2)

## Why

Bisect result:

- **stub only** → no freeze; regular fanfare can still be heard
- **fan2 only** → held tone freeze

0.1.5 default build **drops quiet FAN2** and ships **BATTLE.X victory-queue stub
only**. Confirm: no freeze, and note poses/fanfare behaviour for the next music fix.

Finding: docs/findings/2026-08-09-batres-late-jals-stuck-tone.md

## What you do

### 1. Pull

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

### 2. Build 0.1.5 Disc 1 (clean)

```bash
cd "$(git rev-parse --show-toplevel)"
python mods/fanfare-skip/scripts/build_on_base.py --against clean --discs 1
```

Expect: builder/fanfare-skip-v0.1.5/layers/disc1.layer.json

### 3. Make playtest image

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p workspace/iso-extract

python scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  builder/fanfare-skip-v0.1.5/layers/disc1.layer.json \
  -o workspace/iso-extract/ff7_d1_fanfare_skip_v015.bin
```

### 4. DuckStation playtest

1. File → Open Image → workspace/iso-extract/ff7_d1_fanfare_skip_v015.bin
2. Same save / last-hit fight as bisect.
3. Listen victory → field/world map.
4. Fill Evidence (freeze + fanfare + poses).

No breakpoints required.

## Evidence

```
held tone freeze: YES/NO
fanfare heard: YES/NO/partial
win poses: YES/NO/partial
loot/exp screens still OK: YES/NO
notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git add docs/INSTRUCTIONS.md
git commit -m "ops: verify fanfare-skip 0.1.5 no freeze"
git push
```

Then say **check**.

Do **not** commit .bin images.

fan2 only causes the freeze, regular music and no freeze with stub only
