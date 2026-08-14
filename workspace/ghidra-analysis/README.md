# Ghidra Analysis - Structured Game Data

This directory contains **structured analysis output** from Ghidra exports, not raw game code.

## What's in this directory (committed to repo)

- `*.json` - Structured data (functions, symbols, control flow, opcodes)
- `*.md` - Human-readable summaries and documentation
- Agent can read these files to understand game structure without raw decompilation

## What's NOT in this directory (gitignored)

- `../ghidra-exports/` - Raw Ghidra exports (listings, decompiled code, binaries)
- These stay **local only** on the Ghidra machine

## Workflow

### 1. Human exports from Ghidra (on Ghidra machine)

Follow instructions in `docs/INSTRUCTIONS.md` to:
- Import game files with correct base addresses
- Let Ghidra analyze/decompile
- Export to `workspace/ghidra-exports/` (local only, gitignored)

### 2. Human runs parser scripts

```bash
python scripts/ghidra/parse_field_listing.py
python scripts/ghidra/parse_field_functions.py
# etc - outputs to workspace/ghidra-analysis/
```

### 3. Human commits the structured output

```bash
git add workspace/ghidra-analysis/
git commit -m "Add analyzed FIELD.BIN structure from Ghidra"
git push
```

### 4. Agent reads the structured data

In future sessions, Agent can:
- Read function addresses and signatures from JSON
- Understand control flow without seeing raw code
- Generate patches based on structure, not guesswork

## Why this approach?

- **Legal**: No raw game code in public repo (only metadata)
- **Efficient**: Agent doesn't need to pattern-match blind
- **Reproducible**: Scripts document exactly how we extract info
- **Fast**: Agent queries JSON instead of asking human for exports

## Current exports

(This list will be updated as we add more analysis files)

- None yet - starting with FIELD.BIN proof-of-concept
