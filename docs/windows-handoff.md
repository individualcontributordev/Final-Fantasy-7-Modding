# Windows handoff

**Status:** active

**Shell:** Git Bash (not PowerShell / cmd)

## If the user asks “what's next?”

1. Run `git pull --ff-only` in the repo root (Git Bash)
2. Re-read this file
3. If status is still **no active task** — tell the user there is nothing to run; stop
4. If status is **active** — follow the checklist below exactly; do not invent steps

Use Git Bash for all commands: forward slashes, `ls`/`cp`/`python`, bash `\` line continuation.

---

## Goal

Create a Ghidra project for `FIELD.BIN.dec`, import it, find the encounter RNG table, label it.

## Prerequisites

- [ ] `workspace/iso-extract/FIELD.BIN.dec` exists (from prior handoff)
- [ ] Ghidra installed (needs Java 21+)
- [ ] Can launch Ghidra

## Steps

### A. Create project (Ghidra GUI)

1. Start Ghidra
2. **File → New Project…** → **Non-Shared Project** → Next
3. Project directory: the repo’s `workspace/ghidra/` folder (create if needed)
4. Project name: `ff7-field-bin` → Finish

### B. Import FIELD.BIN.dec

1. **File → Import File…** → select `workspace/iso-extract/FIELD.BIN.dec`
2. Format: **Raw Binary**
3. Language: **MIPS** → **R3000** → **32-bit** → **little-endian** (exact labels may vary slightly by Ghidra version)
4. Options / base address: **`0x80000000`**
5. OK → open the file when prompted
6. When asked to analyze: **Yes** → accept default analyzers → Analyze

### C. Find and label the RNG table

1. **Search → Memory…** (or Memory Search)
2. Search for hex: `B1 CA EE 6C 5A 71 2E 55`
3. Search All — expect **one** hit
4. Go to that address
5. Right-click → **Add Label…** (or press `L`) → name: `g_field_rng_table` → OK

### D. Record addresses

In Ghidra, note:

- Address of `g_field_rng_table` (should be near `0x80040638` if file offset `0x40638` + base `0x80000000`)
- File offset shown (if available) or confirm it matches prior `0x40638`

## Pass criteria

- [ ] Project `ff7-field-bin` exists under `workspace/ghidra/`
- [ ] Binary imported at base `0x80000000` and analyzed
- [ ] Label `g_field_rng_table` created
- [ ] One search hit for `B1 CA EE 6C 5A 71 2E 55`

## Report results (git pipe)

Overwrite `docs/windows-results.md` with:

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
cd "$(git rev-parse --show-toplevel)"
git add docs/windows-results.md
git commit -m "Windows handoff results: Ghidra RNG table"
git push
```

Tell the user: on the Mac chat, say **“check results”**.
