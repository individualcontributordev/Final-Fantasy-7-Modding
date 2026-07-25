# Windows checklist (human)

**Status:** active

**Shell:** Git Bash  
Report outcomes in the **Mac Cursor chat** (not a results file).

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

---

## Goal

Ghidra: import `FIELD.BIN.dec`, go to RNG table, label it, list xrefs.

## Steps

### A. Project + import (if not done)

1. Ghidra → **New Project** → Non-Shared → `workspace/ghidra/` → name `ff7-field-bin`
2. **Import** `workspace/iso-extract/FIELD.BIN.dec`
3. Raw Binary · MIPS R3000 32-bit LE · base **`0x80000000`**
4. Analyze with defaults

### B. RNG table

1. Press **G** → `0x80040638` (or Search Memory hex `B1 CA EE 6C 5A 71 2E 55`)
2. Label (`L`): `g_field_rng_table`
3. Right-click address → **References → Show References to Address**
4. Note how many xrefs and 1–2 function names/addresses if shown

## Tell the Mac chat

- Base address used
- `g_field_rng_table` address
- Search hit count
- Xref count (and any function names/addresses)
- Errors, if any
