# Task: First 801B03D0 / 80014540 — is fanfare already on?

## Why

Your BATRES pass (`3eff3a6`) locks the timeline:

| Order | Address | When |
|-------|---------|------|
| 1 | **801B0000** | entry |
| 2 | **801B0278** | then |
| 3 | **801B03D0** | **`jal 80014540` — loops during fanfare + win anims** |
| later | **801B0524** | rewards page (not fanfare start) |

Missed in-battle: 010C, 0458, 06D8 (and 03E0 not observed in panels).

`80014540` (SCUS) only calls `80033E34` → `80033CB8` with **a0=3**.

We need one fact before patching:

**At the very first 801B03D0 stop after the kill, is fanfare already audible / are poses already visible?**

- If **NO** → ceremony starts inside 14540/33E34/33CB8 (or first 03E0 wait).  
- If **YES** → music/poses were kicked earlier (between 0278 and 03D0, or before 0000); 03D0 only pumps the frame.

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
3. **Clear all BPs.**
4. Enable **only**:

| Address | Role |
|---------|------|
| **801B0278** | last checkpoint before ceremony pump |
| **801B03D0** | first ceremony `jal 80014540` |
| **80014540** | SCUS wrapper entry |
| **80033E34** | next hop (a0 becomes 3 inside) |

5. Disable everything else.

### 4. Kill + listen carefully

1. Kill last enemy.
2. At **801B0278** (first hit after kill):  
   fanfare audible? poses visible? (expect NO)  
   Continue.
3. At **first 801B03D0** after that (hit count → 1):  
   **pause and listen 1–2s while frozen**  
   fanfare already on? poses already on?  
   Note a0/a1/a2/ra (should be thin call). Shot: `docs/801B03D0-first.png`
4. Step into or continue to **first 80014540** if not same frame:  
   note a0 a1 a2 (loaded from globals). Shot optional `docs/80014540-first.png`
5. **First 80033E34**: note a0 a1 a2 a3 (expect a0=3 after shuffle).  
   Shot optional `docs/80033E34-first.png`
6. Resume; note roughly when fanfare **starts** if it was off at first 03D0  
   (e.g. after N more 03D0 hits — hit count on panel).

Stop before rewards. Do not need 0524.

## Evidence

```
Image: ff7_d1_fanfare_skip_v015.bin

At first 801B0278 after kill:
  fanfare audible: YES/NO
  poses visible: YES/NO

At first 801B03D0 (hit count 1):
  fanfare audible: YES/NO
  poses visible: YES/NO
  a0 a1 a2 ra:
  shot: docs/801B03D0-first.png

At first 80014540:
  a0 a1 a2:
  shot:

At first 80033E34:
  a0 a1 a2 a3:
  shot:

If fanfare was OFF at first 03D0:
  became audible after ~N more 03D0 hits (hit count):
  or after 80033E34/unknown:

Verdict: music starts BEFORE_FIRST_03D0 / AT_OR_INSIDE_14540_CHAIN / AFTER_SEVERAL_03D0 / UNSURE
notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git add docs/INSTRUCTIONS.md docs/*.png 2>/dev/null || git add docs/INSTRUCTIONS.md
git commit -m "ops: first 03D0 fanfare already on?"
git push
```

Then say **check**.

Do **not** commit .bin images.

order of hits
80033E34
801B0278
80033E34
80014540 (mid fanfair)
80033E34 (mid fanfar)
80033E34 (on world map loading)