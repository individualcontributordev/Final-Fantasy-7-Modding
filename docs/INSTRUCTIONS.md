# Task: Hit FAN2 id path (0x47 / 800A2CC4 / 800B1060)

## Why

Your 0.1.5 BP pass (`4ff7341`) showed:

| BP | Useful? |
|----|---------|
| **800ABE4C** | Yes — **hit count 1** (stub is called) |
| **801B0000** | Anchor — still **no** fanfare/poses at entry |
| **800DCF94** | Clears only (`a0=-1`); not the play call |
| **80015248** | Spam SFX (e.g. a0=5) — disable for next pass |

Fanfare anims start **after** BATRES, around later DCF94 noise — still no unique play BP.

Static: FAN2 song id **0x47** is loaded at **800AB2B0** into:

- `jal 800A2CC4` @ **800AB2AC** (a0=0x47 in delay)
- `jal 800B1060` @ **800AB2D0** same block

Finding: docs/findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md

## What you do

### 1. Pull

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

### 2. Play image (same 0.1.5)

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p workspace/iso-extract

python3 scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  builder/fanfare-skip-v0.1.5/layers/disc1.layer.json \
  -o workspace/iso-extract/ff7_d1_fanfare_skip_v015.bin
```

### 3. DuckStation BPs

1. File → Open Image → workspace/iso-extract/ff7_d1_fanfare_skip_v015.bin
2. Save before last hit.
3. **Clear all BPs.**
4. Enable **only** these Execute BPs:

| Address | Role |
|---------|------|
| **800AB2AC** | `jal 800A2CC4` (delay sets a0=**0x47** FAN2 id) |
| **800AB2D0** | `jal 800B1060` same victory block |
| **800A2CC4** | callee entry (confirm a0) |
| **800B1060** | music wrapper entry |
| **801B0000** | optional timing only |

5. Do **not** arm 80015248 or 800DCF94 this pass.

### 4. One kill

1. Kill last enemy.
2. On **first** hit of each new address: note regs + whether fanfare already audible / poses visible.
3. Screenshot first hit of **800AB2AC** and **800B1060** into `docs/` if possible  
   (e.g. `docs/800AB2AC.png`, `docs/800B1060.png`).

## Evidence

```
Image: ff7_d1_fanfare_skip_v015.bin

Hit order after last kill:

1) address:
   a0 a1 a2 ra:
   fanfare already? YES/NO
   poses already? YES/NO
   shot:

2) ...

800AB2AC hit? YES/NO  count:  a0 at hit:
800AB2D0 hit? YES/NO  count:
800A2CC4 hit? YES/NO  a0:
800B1060 hit? YES/NO  a0 a1 a2:
801B0000 relative: before/after the 0x47 block?

Fanfare first audible: BEFORE/AFTER which address?
Win poses first visible: BEFORE/AFTER which address?

notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git add docs/INSTRUCTIONS.md docs/*.png 2>/dev/null || git add docs/INSTRUCTIONS.md
git commit -m "ops: FAN2 0x47 path BP hits"
git push
```

Then say **check**.

Do **not** commit .bin images.

only 801B0000 hit in battle, all others hit after rewards page
loops between 800AB2D0 and 800AB2AC when loading the world map