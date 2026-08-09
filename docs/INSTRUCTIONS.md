# Task: Find what still starts fanfare/poses on 0.1.5

## Why

0.1.5 smoke: **no freeze**, but **fanfare + win poses still play**.

Ship only stubs `800A2974` (one caller `800ABE4C`). Ceremony must start
elsewhere. We need the **first live music/pose hits after last kill** on the
official 0.1.5 image — without quiet FAN2.

Finding: docs/findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md

## What you do

### 1. Pull

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

### 2. Build play image (pack already on main)

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p workspace/iso-extract

python3 scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  builder/fanfare-skip-v0.1.5/layers/disc1.layer.json \
  -o workspace/iso-extract/ff7_d1_fanfare_skip_v015.bin
```

### 3. DuckStation setup

1. File → Open Image → workspace/iso-extract/ff7_d1_fanfare_skip_v015.bin
2. Load save just before last hit (HUD up).
3. **Clear old BPs.**
4. Add **Execute** breakpoints (all enabled):

| # | Address | Why |
|---|---------|-----|
| 1 | **800ABE4C** | only `jal 800A2974` (stub) — does ceremony still call it? |
| 2 | **800DCF94** | music flag helper (`a0==-1` clear; else set/play path) |
| 3 | **80015248** | AKAO/play helper used after DCF94 set path |
| 4 | **801B0000** | BATRES victory entry (optional timing anchor) |

5. Disable any other BPs (especially 800D3098 renderer).

### 4. One kill pass

1. Kill last enemy.
2. For **each first hit after the kill**, while paused, fill Evidence.
3. Continue (F8 / resume) to next hit until fanfare is clearly audible or you have
   first hits on all four (whichever comes first).
4. If a BP spam-hits every frame: disable it, note that, keep going.

### 5. Screenshots (optional but useful)

Save into `docs/` if easy:

- first hit on 80015248 after kill
- first hit on 800DCF94 with a0 ≠ -1 (if any)
- first hit on 800ABE4C (if any)

Names e.g. `docs/bp-80015248-first.png`

## Evidence

```
Image: ff7_d1_fanfare_skip_v015.bin (fanfare-skip-v0.1.5)

After last kill, first hits (order matters — number them):

1) address:
   pc / ra:
   a0 a1 a2 a3:
   game moment (death anim / silence / fanfare starting / poses):
   shot:

2) address:
   pc / ra:
   a0 a1 a2 a3:
   game moment:
   shot:

3) address:
   ...

800ABE4C ever hit this fight? YES/NO  hit count:
800DCF94 hits: count≈   a0 values seen (list):
80015248 first post-kill: a0= a1= a2= ra=   fanfare already on? YES/NO
801B0000 hit? YES/NO

Fanfare first became audible: BEFORE/AFTER which BP address?
Win poses first visible: BEFORE/AFTER which BP address?

notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git add docs/INSTRUCTIONS.md docs/*.png 2>/dev/null || git add docs/INSTRUCTIONS.md
git commit -m "ops: 0.1.5 ceremony still-plays BP hits"
git push
```

Then say **check**.

Do **not** commit .bin images.
