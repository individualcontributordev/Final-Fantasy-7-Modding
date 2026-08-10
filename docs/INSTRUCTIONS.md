# Task: Paste Ghidra decompiles (BATRES victory path)

You already have three programs imported (BATRES / BATTLE / SCUS).
Setup guide: [ghidra-battle-overlays.md](ghidra-battle-overlays.md)

**Put evidence in this file** under **Evidence** (paste decompiler text).
Do not only say check with empty evidence.

## Goal

Get decompiler output so we can name what starts fanfare/poses and design the
next skip patch. Chat-only copies get lost — **the repo is the source of truth.**

## What to collect

### A. BATRES (base `801B0000`)

| Go to | Action |
|-------|--------|
| **`801B0000`** | Create function if needed; name **`batres_victory`**. Copy **full** decompile. |
| **`801B0E20`** | Own function; name e.g. **`batres_clear_battle_ui`**. Copy decompile. |

If `batres_victory` is huge, full function is still preferred. Minimum range in
listing terms: **`801B0270`–`801B0560`** behavior must appear in the paste.

### B. BATTLE (base `800A0000`)

For each address: **G** to address, then **D** if needed, then **Function → Create Function**, then copy decompile.

| Address | Suggested name (optional) |
|---------|---------------------------|
| **`800A7254`** | (pose/anim candidate; called a2=4 x10) |
| **`800A3354`** | wait-frame (ceremony x s4) |
| **`800B1060`** | conditional a0=8 |
| **`800A56B0`** | rewards UI |

### C. SCUS (base `80010000`)

| Address | Suggested name (optional) |
|---------|---------------------------|
| **`80014540`** | thin wrapper to 33E34 |
| **`80033E34`** | frame pump (one level deep is enough) |

### Minimum if short on time

Paste only these three:

1. `batres_victory` (`801B0000`)
2. `800A7254`
3. `800A3354`

## How to paste

In Ghidra Decompiler window: select all text, copy, paste into **Evidence**
below inside the fenced block. One section per function.

Do **not** commit large .dec / .bin binaries. Decompiler **text** in this
file (or docs/ghidra-pastes/*.md) is what we need.

## Evidence

```
### batres_victory (801B0000)

### batres_clear_battle_ui (801B0E20)

### 800A7254

### 800A3354

### 800B1060

### 800A56B0

### 80014540

### 80033E34

notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
git add docs/INSTRUCTIONS.md
# optional longer pastes:
# mkdir -p docs/ghidra-pastes && git add docs/ghidra-pastes/
git commit -m "ops: Ghidra decompiles for BATRES victory / fanfare path"
git push
```

Then say **check**.

## Refs

- Overlay import / decompress / SCUS: [ghidra-battle-overlays.md](ghidra-battle-overlays.md)
- Fanfare finding: [findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md](findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md)
