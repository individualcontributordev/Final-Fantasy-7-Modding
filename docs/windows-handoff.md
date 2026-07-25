# Windows checklist (human)

**Status:** active

**Shell:** Git Bash  
**Agent:** none on Windows — follow this file yourself; talk to the Mac chat only.

## Start

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

Then do the steps below.

---

## Goal

Create a Ghidra project for `FIELD.BIN.dec`, import it, find the encounter RNG table, label it.

## Prerequisites

- [ ] `workspace/iso-extract/FIELD.BIN.dec` exists
- [ ] Ghidra installed (Java 21+)

## Steps

### A. Create project (Ghidra GUI)

1. Start Ghidra
2. **File → New Project…** → **Non-Shared Project** → Next
3. Project directory: repo `workspace/ghidra/` (create if needed)
4. Project name: `ff7-field-bin` → Finish

### B. Import FIELD.BIN.dec

1. **File → Import File…** → `workspace/iso-extract/FIELD.BIN.dec`
2. Format: **Raw Binary**
3. Language: **MIPS** → **R3000** → **32-bit** → **little-endian**
4. Base address: **`0x80000000`**
5. Open when prompted; analyze with defaults when asked

### C. Find and label the RNG table

1. **Search → Memory…**
2. Hex: `B1 CA EE 6C 5A 71 2E 55`
3. Search All — expect **one** hit
4. Go there → label (`L`): `g_field_rng_table`

Expected address ≈ `0x80040638` (file offset `0x40638` + base).

## Pass criteria

- [ ] Project under `workspace/ghidra/`
- [ ] Imported at `0x80000000`, analyzed
- [ ] `g_field_rng_table` labeled; one search hit

## Send results to Mac (git)

Edit `docs/windows-results.md` (Notepad/`vim`/etc.) to:

```markdown
# Windows → Mac results

**Status:** complete
**Task:** Ghidra import + RNG table label

## Output

Ghidra project path:
Language selected (exact string):
Base address used:
g_field_rng_table address:
Search hit count for B1CAEE6C…:
Errors (or none):

## Notes

(anything else)
```

Then:

```bash
git add docs/windows-results.md
git commit -m "Windows results: Ghidra RNG table"
git push
```

In the **Mac** Cursor chat, say: **check results**
