# Task: Where fanfare starts inside BATRES (0278 → 042C)

## Why

Your pass (`deafeab`) corrected the map:

| Finding | Detail |
|---------|--------|
| **80033E34** | Hits **mid-fight** (enemies alive) — global pump. **Disable.** |
| **801B03D0** | **HitCount 0** while ceremony plays — **skipped** when s4=0x31 path sets flag |
| **80014540** | First hit is **mid fanfare** (poses already on) = post-wait **801B042C** |

Fanfare/poses begin **after 801B0278** and **before first 80014540**.

Static sequence after 0278:

1. `801B0E20` (at 0278)
2. loop `800A7254` (028C, a2=4) ×10
3. maybe `800B1060` (02FC)
4. **`s4 = 0x31`** + ceremony flag (03A0)
5. wait: `800A3354` × s4 (03E0)
6. `80014540` at **042C** (mid fanfare)

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
3. **Clear all BPs.** Do **not** enable 80033E34, 801B03D0, or 800AB2*.
4. Enable **only**:

| Address | Role |
|---------|------|
| **801B0278** | `jal 801B0E20` — victory anchor |
| **801B028C** | `jal 800A7254` pose/anim seed (will multi-hit; note first) |
| **801B03A0** | sets **s4=0x31** ceremony wait |
| **801B03E0** | first frame of wait `jal 800A3354` |
| **801B042C** | post-wait `jal 80014540` |

5. If **801B028C** spam-blocks, after **first** hit disable it and continue.

### 4. One kill — freeze and listen at each first hit

At **each first stop**, pause long enough to hear:

- fanfare audible YES/NO  
- win poses already YES/NO  

Order expected: 0278 → 028C → 03A0 → 03E0 → (many 03E0) → 042C.

Shots (first hit only):

- `docs/801B0278.png`
- `docs/801B028C-first.png`
- `docs/801B03A0.png`
- `docs/801B03E0-first.png`
- `docs/801B042C-first.png`

## Evidence

```
Image: ff7_d1_fanfare_skip_v015.bin

1) 801B0278 first: fanfare? poses? a0 a1 a2 ra: shot:
2) 801B028C first: fanfare? poses? a0 a1 a2: shot:
3) 801B03A0 first: fanfare? poses? s4= shot:
4) 801B03E0 first: fanfare? poses? shot:
5) 801B042C first: fanfare? poses? shot:

Earliest BP where fanfare becomes YES:
Earliest BP where poses become YES:

Disabled for spam:
notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git add docs/INSTRUCTIONS.md docs/*.png 2>/dev/null || git add docs/INSTRUCTIONS.md
git commit -m "ops: BATRES 0278-042C fanfare start bracket"
git push
```

Then say **check**.

Do **not** commit .bin images.
