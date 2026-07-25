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

Extract disc `FIELD/FIELD.BIN` into the repo workspace and decompress it for Ghidra.

## Important

**Do not use Makou Reactor for this.** Makou edits field maps and updates `FIELD.BIN`
when saving an ISO — it has no “export FIELD.BIN” for the engine binary. Use **CDmage**.

## Prerequisites

- [ ] Repo cloned; this file is under `docs/windows-handoff.md`
- [ ] Clean FF7 disc 1 image you own (`.bin` + `.cue` if you have a cue)
- [ ] [CDmage](https://www.romhacking.net/utilities/1435/) installed (or equivalent ISO extractor)
- [ ] Python 3 on PATH (`python` or `python3`)

## Steps

### A. Put the disc image in place (Git Bash)

From the `ff7-modding` repo root:

```bash
mkdir -p workspace/iso-extract
# Copy your disc image(s) here — adjust source path to where your ISO lives
cp "/path/to/your/ff7_disc1.bin" workspace/iso-extract/ff7_disc1.bin
cp "/path/to/your/ff7_disc1.cue" workspace/iso-extract/ff7_disc1.cue   # if you have one
cp workspace/iso-extract/ff7_disc1.bin workspace/iso-extract/ff7_disc1_pristine.bin
ls -la workspace/iso-extract/
```

### B. Extract FIELD.BIN with CDmage (GUI)

1. Open **CDmage**
2. File → Open → select `workspace/iso-extract/ff7_disc1.bin` (or the `.cue`)
3. In the tree, open the **`FIELD`** folder
4. Select **`FIELD.BIN`** (the file in that folder — engine binary)
5. Right-click → **Extract** / **Extract files…**
6. Save to: `workspace/iso-extract/FIELD.BIN` (exact name)
7. Also keep a backup:

```bash
cp workspace/iso-extract/FIELD.BIN workspace/iso-extract/FIELD.BIN.pristine
ls -la workspace/iso-extract/FIELD.BIN*
```

### C. Decompress (Git Bash)

```bash
cd "$(git rev-parse --show-toplevel)"
python scripts/decompress_field_bin.py workspace/iso-extract/FIELD.BIN
# if that fails: python3 scripts/decompress_field_bin.py workspace/iso-extract/FIELD.BIN
```

## Pass criteria

- [ ] `workspace/iso-extract/FIELD.BIN` exists (tens/hundreds of KB compressed)
- [ ] Script prints sizes and writes `workspace/iso-extract/FIELD.BIN.dec`
- [ ] Script prints `RNG table found at file offset 0x…` (US disc expected)

## Report results (git pipe — do not paste to Mac)

Overwrite `docs/windows-results.md` with:

```markdown
# Windows → Mac results

**Status:** complete
**Task:** extract and decompress FIELD.BIN

## Output

FIELD.BIN size (bytes):
FIELD.BIN.dec size (bytes):
RNG table line (full script line):
Errors (or none):

## Notes

(anything else)
```

Then in Git Bash:

```bash
cd "$(git rev-parse --show-toplevel)"
git add docs/windows-results.md
git commit -m "Windows handoff results: FIELD.BIN decompress"
git push
```

Tell the user: on the Mac chat, say **“check results”**.

