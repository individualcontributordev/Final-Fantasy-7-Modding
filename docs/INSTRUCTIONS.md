# Task: Bisect freeze — stub-only vs fan2-only discs

## Why

Freeze is a **0.1.4 regression** (stock ISO clean). Window: after **801B0278**, before **801B0458**.

Two independent patches:

1. BATTLE.X victory-queue stub at **800A2974**
2. Quiet **ENEMY6/FAN2.SND**

Build A = stub only. Build B = FAN2 only. Which freezes decides the fix.

Finding: docs/findings/2026-08-09-batres-late-jals-stuck-tone.md

## What you do

### 1. Pull

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

### 2. Build both bisect packs (Disc 1, clean base)

```bash
cd "$(git rev-parse --show-toplevel)"

python mods/fanfare-skip/scripts/build_on_base.py --against clean --discs 1 --skip-fan2

python mods/fanfare-skip/scripts/build_on_base.py --against clean --discs 1 --fan2-only
```

Expected packs (VERSION 0.1.4):

- builder/fanfare-skip-stub-only-v0.1.4/layers/disc1.layer.json
- builder/fanfare-skip-fan2-only-v0.1.4/layers/disc1.layer.json

### 3. Make playtest disc images

Needs workspace/pristine/FINALFANTASY7_D1.bin.

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p workspace/iso-extract

python scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  builder/fanfare-skip-stub-only-v0.1.4/layers/disc1.layer.json \
  -o workspace/iso-extract/ff7_d1_fanfare_stub_only.bin

python scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  builder/fanfare-skip-fan2-only-v0.1.4/layers/disc1.layer.json \
  -o workspace/iso-extract/ff7_d1_fanfare_fan2_only.bin
```

### 4. Playtest in DuckStation

No breakpoints. Same save / last-hit fight for both.

**Build A — stub only**

1. File → Open Image → workspace/iso-extract/ff7_d1_fanfare_stub_only.bin
2. Load save, kill last enemy, listen through victory → field/world map.
3. Fill Evidence A.

**Build B — fan2 only**

1. File → Open Image → workspace/iso-extract/ff7_d1_fanfare_fan2_only.bin
2. Same fight path.
3. Fill Evidence B.

## Evidence

```
Build A (stub only, stock FAN2) — ff7_d1_fanfare_stub_only.bin
  held tone: YES/NO
  fanfare heard: YES/NO/quiet
  poses: YES/NO
  notes:

Build B (fan2 only, stock BATTLE) — ff7_d1_fanfare_fan2_only.bin
  held tone: YES/NO
  fanfare heard: YES/NO/quiet
  poses: YES/NO
  notes:

Verdict: freeze caused by STUB / FAN2 / BOTH / UNSURE
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git add docs/INSTRUCTIONS.md
git commit -m "ops: bisect freeze stub vs FAN2"
git push
```

Then say **check**.

Do **not** commit .bin images.
