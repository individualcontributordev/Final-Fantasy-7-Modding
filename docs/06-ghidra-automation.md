# Ghidra Analysis Automation

This document explains the automated Ghidra workflow using ghidra-cli.

## Overview

**Problem:** Agent needs to understand FF7's code structure to make accurate patches, but committing decompiled game code isn't appropriate.

**Solution:** 
1. Use Ghidra to analyze game binaries (locally, not committed)
2. Run automation scripts to extract structured metadata
3. Commit only the metadata JSON (not raw game code)
4. Agent queries the JSON in future sessions

## Setup Status

✅ ghidra-cli installed at: `/d/ghidra-cli-v0.2.2`  
✅ Ghidra installation: `D:/ghidra_12.1_PUBLIC/ghidra_12.1_PUBLIC`  
✅ Java JDK 21: OK  
✅ Bridge script compiles: OK  

(See `docs/INSTRUCTIONS.md` for full `ghidra doctor` output)

## Workflow

### 1. Prepare Game Files

Decompress binaries if needed:

```bash
# FIELD.BIN (field scripts and code)
python scripts/decompress_gzipps.py \
  workspace/iso-extract/FIELD.BIN \
  workspace/iso-extract/FIELD.BIN.dec
```

### 2. Run Analysis Script

```bash
cd ~/Final-Fantasy-7-Modding
python scripts/ghidra/analyze_field_bin.py
```

This will:
- Import FIELD.BIN.dec into Ghidra (if not already imported)
- Run auto-analysis
- Extract functions, symbols, xrefs
- Output JSON to `workspace/ghidra-analysis/`

### 3. Review Output

```bash
ls -lh workspace/ghidra-analysis/
# field-functions.json - function addresses, names, sizes
# field-symbols.json   - global symbols (RNG table, etc.)
# field-xrefs.json     - cross-references (who calls what)
```

### 4. Commit Metadata

```bash
git add workspace/ghidra-analysis/
git commit -m "Add Ghidra analysis metadata for FIELD.BIN"
git push
```

## What Gets Committed

**✅ Committed (structured metadata):**
- Function addresses and sizes
- Symbol names and locations
- Control flow information
- Call graphs
- Data structure layouts

**❌ Not committed (raw game data):**
- Decompiled source code
- Full disassembly listings
- Original game binaries
- Ghidra project files

## Using the Metadata

Agent can query the JSON files:

```python
import json
functions = json.load(open("workspace/ghidra-analysis/field-functions.json"))
rng_func = [f for f in functions if "random" in f["name"].lower()][0]
print(f"RNG at: {rng_func['address']}, size: {rng_func['size']}")
```

This enables:
- Accurate patching (no address guessing)
- Understanding code relationships
- Finding all callers of a function
- Identifying data structures

## Troubleshooting

### ghidra command not found

```bash
which ghidra  # Should show /d/ghidra-cli-v0.2.2/ghidra

# If not, add to ~/.zshrc:
export PATH="/d/ghidra-cli-v0.2.2:$PATH"
```

### analyzeHeadless not found

```bash
echo $GHIDRA_INSTALL_DIR  # Should show D:/ghidra_12.1_PUBLIC/ghidra_12.1_PUBLIC

# If not set, add to ~/.zshrc:
export GHIDRA_INSTALL_DIR="/d/ghidra_12.1_PUBLIC/ghidra_12.1_PUBLIC"
```

### Script fails to run

```bash
# Verify ghidra-cli works:
ghidra doctor  # All checks should pass

# Check prerequisites:
ls -lh workspace/iso-extract/FIELD.BIN.dec  # File must exist
```

## Architecture

```
Game Binaries (local, gitignored)
  workspace/iso-extract/FIELD.BIN.dec
          │
          ├─ ghidra-cli import + analyze
          ▼
Ghidra Project (local, gitignored)
  %APPDATA%/Local/ghidra-cli/projects/
          │
          ├─ scripts/ghidra/*.py (extract metadata)
          ▼
Structured JSON (COMMITTED)
  workspace/ghidra-analysis/*.json
          │
          ├─ Agent reads JSON
          ▼
    Fast, accurate patches!
```

## Next Steps

Agent will implement the actual extraction scripts once the automation framework is tested.

Current stub: `scripts/ghidra/analyze_field_bin.py`  
Next: Implement Ghidra Python scripts to extract functions/symbols/xrefs
