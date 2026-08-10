# Task: BATRES-path BPs while fanfare still in battle

## Why

Your 0x47 pass (`145a809`) is a clean **negative**:

| BP | During battle win ceremony |
|----|----------------------------|
| **801B0000** | **HIT** (only one) |
| **800AB2AC / AB2D0 / A2CC4 / B1060** | **MISS** until **after rewards** / world map |

Hits after rewards at those VAs are a **different overlay** (live code ≠ BATTLE.X).
Discard for fanfare RE.

So on 0.1.5, **fanfare + poses start after BATRES entry**, still in battle, **without**
the FAN2 id `0x47` block. Next: first jals **inside** BATRES after `801B0000` before
the rewards page.

Finding: docs/findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md

## What you do

### 1. Pull

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

### 2. Play image

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p workspace/iso-extract

python3 scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  builder/fanfare-skip-v0.1.5/layers/disc1.layer.json \
  -o workspace/iso-extract/ff7_d1_fanfare_skip_v015.bin
```

### 3. DuckStation — Execute BPs only

1. File → Open Image → workspace/iso-extract/ff7_d1_fanfare_skip_v015.bin
2. Save before last hit.
3. **Clear all BPs** (including 800AB2AC / 800B1060 / 800A2CC4).
4. Enable **Execute**:

| Address | Role (static BATRES) |
|---------|----------------------|
| **801B0000** | victory entry (anchor) |
| **801B010C** | `jal 80014A58` (early kernel helper) |
| **801B0278** | `jal 801B0E20` (already known live) |
| **801B03D0** | `jal 80014540` |
| **801B03E0** | `jal 800A3354` (wait/spin path; s4 often 0x31) |
| **801B0458** | `jal 800A31A0` |
| **801B0524** | `jal 800A56B0` |
| **801B06D8** | `jal 800B0F04` |

5. If one address **spam-hits every frame**, disable it and note which.

### 4. One kill — stay on victory screen

1. Kill last enemy.
2. Record **first hit after kill** for each address **while still in battle**
   (before rewards page). Ignore hits after you leave victory/rewards.
3. Note when **fanfare becomes audible** and when **win poses** appear relative
   to those addresses.
4. Optional shots: first **801B010C**, first **801B03E0**, first **801B06D8**
   → `docs/801B010C.png` etc.

## Evidence

```
Image: ff7_d1_fanfare_skip_v015.bin

In-battle hit order after last kill (stop at rewards — do not count world map):

1) address:   a0 a1 a2 ra:   fanfare already?  poses already?  shot:
2) ...

Table:
801B0000 hit in battle? YES/NO
801B010C hit in battle? YES/NO  count≈
801B0278 hit in battle? YES/NO
801B03D0 hit in battle? YES/NO
801B03E0 hit in battle? YES/NO  (spam? YES/NO)
801B0458 hit in battle? YES/NO
801B0524 hit in battle? YES/NO
801B06D8 hit in battle? YES/NO

Fanfare first audible: BEFORE/AFTER which address?
Win poses first visible: BEFORE/AFTER which address?

Disabled for spam:
notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git add docs/INSTRUCTIONS.md docs/*.png 2>/dev/null || git add docs/INSTRUCTIONS.md
git commit -m "ops: BATRES-path BPs during in-battle fanfare"
git push
```

Then say **check**.

Do **not** commit .bin images.

see screenshot names for order
801B03D0 looping during fanfair music and animations
801B0524 loops after as rewards page loading