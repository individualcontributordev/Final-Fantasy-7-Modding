# Task: First steps inside victory overlay 801B0000

## Why

Handoff is confirmed live:

- **800A16F4**: s1 = 0xFFFF (wait done, no loop)
- **800A1700**: fall-through in win_transition
- **801B0000**: **ra = 800A1734** (called from win fn); real function, prologue addiu sp,sp,-136

Poses/fanfare setup almost certainly live in this overlay. BATTLE_X_dec.bin does not contain it.
We need the first control flow inside 801B0000 after the post-kill jal.

Shots already in repo: docs/800A16F4.png, docs/800A1700.png, docs/801B0000.png
Finding: docs/findings/2026-08-09-win-transition-fn-800a1158.md

## What you do

### 1. Pull

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

### 2. DuckStation breakpoints

1. **Remove** execute BPs on **800A16F4** and **800A1700** (done).
2. Keep or re-add execute **801B0000** (enable only after last kill if it fires mid-fight).
3. Add execute BPs on the first real body instructions (from your 801B0000 shot):
   - **801B0008** — early body (after sw s2 / before halfword load)
   - **801B000C** — lhu from s2 path (flag-ish)
4. Optional if those spam: only **801B0000**, then single-step 10-20 instructions and note each jal target.
5. Still **do not** enable 800D3098 or 800A54A0.

### 3. Fight

- Fanfare Skip 0.1.4, HUD up, save before last kill
- Kill last enemy
- Stop on **801B0000** (confirm ra still ~800A1734)
- Continue / step until **801B0008** or **801B000C** (or step manually if those never hit)

### 4. Dump (important)

While stopped inside 801B with code visible:

1. DuckStation memory view at **801B0000**
2. Dump or screenshot enough bytes to cover ~0x200 (or full if easy)
3. If you can export: save as `docs/801B0000-dump.bin` (or paste hex range in Evidence)
4. Screenshot full debugger for first interesting jal / branch

## Evidence

### A. 801B0000 (post-kill)

```
801B0000:
  ra:
  a0 a1 a2 a3:
  s5 / any 800F83xx:
  game moment:
```

### B. First body stop (0008 / 000C / stepped PC)

```
pc:
  ra:
  notable regs:
  first jal targets seen (addresses):
  game moment: (still pre-pose? pose start?)
  screenshot path:
```

### C. Dump

```
dump path or NEVER:
size / range:
```

## When done

```bash
git add docs/INSTRUCTIONS.md docs/*.png docs/*dump* 2>/dev/null || git add docs/INSTRUCTIONS.md
git commit -m "ops: 801B0000 victory overlay first steps"
git push
```

Then say **check**.
