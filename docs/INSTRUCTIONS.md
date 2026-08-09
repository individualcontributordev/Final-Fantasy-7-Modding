# Task: Bisect freeze — 800A2974 stub vs quiet FAN2.SND

## Why

Your freeze timing (`6fb15fb`) nails it:

| Checkpoint | Freeze? |
|------------|---------|
| At **801B0278** | **No** — starts only after continue |
| At **801B0458** | **Yes** already |
| At **801B0558** | Yes already |
| **Stock ISO** | **No freeze** (verified) |

So: **Fanfare Skip 0.1.4 regression**, window = BATRES after 0278 → before 0458.

0.1.4 has **two** independent changes:

1. **BATTLE.X** — victory-queue at **800A2974** (file+0x2974) patched to immediate return
2. **ENEMY6/FAN2.SND** — sequence body zeroed (quiet fanfare)

We need to know **which one** (or both) causes the held tone. That decides the fix.

Finding: `docs/findings/2026-08-09-batres-late-jals-stuck-tone.md`

Build flags were added: `--skip-fan2` and `--fan2-only`.

## What you do

### 1. Pull

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

### 2. Build two bisect discs (Disc 1)

```bash
# A) BATTLE stub ONLY (stock FAN2)
python mods/fanfare-skip/scripts/build_on_base.py --against clean --discs 1 --skip-fan2

# B) FAN2 quiet ONLY (stock BATTLE victory-queue)
python mods/fanfare-skip/scripts/build_on_base.py --against clean --discs 1 --fan2-only
```

| Build | pack stem | BATTLE.X | FAN2 |
|-------|-----------|----------|------|
| **A** | fanfare-skip-**stub-only**-v* | stub 800A2974 | **stock** |
| **B** | fanfare-skip-**fan2-only**-v* | **stock** | quiet |

Apply with your usual builder → DuckStation Disc 1 flow.
Bisect packs are **not** added to the public manifest (pack folder only).

### 3. Playtest (same save / last-hit fight)

No BPs required. For each build:

1. Kill last enemy
2. Listen victory → field/world map
3. Note held tone / fanfare / poses

## Evidence

```
Build A (BATTLE stub only, stock FAN2):
  held tone: YES/NO
  fanfare heard: YES/NO/quiet
  poses: YES/NO
  notes:

Build B (FAN2 quiet only, stock BATTLE):
  held tone: YES/NO
  fanfare heard: YES/NO/quiet
  poses: YES/NO
  notes:

Verdict: freeze caused by STUB / FAN2 / BOTH / UNSURE
```

## When done

```bash
git add docs/INSTRUCTIONS.md
git commit -m "ops: bisect freeze stub vs FAN2"
git push
```

Then say **check**.
