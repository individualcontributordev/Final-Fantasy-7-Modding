# Task: Catch fanfare/pose handoff after last kill

## Why

Post-kill execute hits at 800A1500 / 1540 / 1580 all sit inside BATTLE.X
function **800A1158..800A1790**. That function waits (loop **800A16F4 -> 800A1200**),
then falls through and calls **801B0000** — when your triad BPs go silent, fanfare
starts. We need one clean capture of that handoff for the pose-skip target.

Detail already in repo: `docs/findings/2026-08-09-win-transition-fn-800a1158.md`

## What you do

### 1. Pull

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

### 2. DuckStation breakpoints

1. **Remove** execute BPs on **800A1500**, **800A1540**, **800A1580** (done).
2. Leave write BP on **800F83C6** off.
3. **Do not** enable **800D3098** or **800A54A0**.
4. Add **execute** BPs:
   - **800A16F4** — wait branch (may hit several times)
   - **800A1700** — fall-through right after wait ends (expect once)
   - **801B0000** — victory overlay entry (enable only after last kill if spam)

### 3. Fight

- Disc with **Fanfare Skip 0.1.4**
- Enter normal battle; wait until **HUD is fully up**
- Save state before last kill
- Kill last enemy
- If **801B0000** was left disabled: enable it **after** kill, before/during wait

### 4. Optional Ghidra (read-only, same session OK)

| | |
|--|--|
| File | `workspace/iso-extract/BATTLE_X_dec.bin` |
| Format | Raw Binary |
| Language | MIPS R3000 32 LE |
| Base | **0x800A0000** |
| Go To | **800A1158** — Create Function if needed; rename e.g. `win_transition` |
| Also open | 800A16F4, 800A1700, 800A172C (jal 801B0000) |

**801B0000 is not in that bin** — only DuckStation can stop there live.

## Evidence (fill in, then commit)

Paste under this heading (or attach screenshots under `docs/` and list paths).

### A. First stop at 800A16F4 after kill

```
800A16F4:
  pc / ra / hit count:
  s1 (0xFFFF = wait done):
  halfword 801083C6 (value; bits & 0x1E):
  game moment:
```

Continue if it re-loops. Note when s1 becomes 0xFFFF or when 16F4 stops hitting.

### B. First stop at 800A1700

```
800A1700:
  ra:
  s5 / halfword 800F83C6:
  game moment:
```

### C. First stop at 801B0000

```
801B0000:
  ra: (expect ~800A1734 if called from win fn)
  a0 a1 a2 a3:
  screenshot: (path if any)
```

If ra is not 800A1734, note the real caller. If a BP never hit, write NEVER HIT.

## When done

```bash
git add docs/INSTRUCTIONS.md docs/*.png 2>/dev/null || git add docs/INSTRUCTIONS.md
git commit -m "ops: fanfare handoff BP evidence"
git push
```

Then say **check** in chat.

all hit, no loops, ra and s1 verify where requested