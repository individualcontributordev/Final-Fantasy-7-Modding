# Windows (Git Bash): build Encounter layer for the disc builder

Use **Git Bash** on the PC that has your pristine discs, CDmage, DuckStation, and this repo.

Goal: publish `builder/encounter-v0.1.0/layers/disc1.layer.json` (no game `.bin` in git).

Scripts take whatever paths you pass. Prefer **forward slashes**. Keep names **consistent** in every step.

---

## 0. Setup

```bash
cd /c/path/to/Final-Fantasy-7-Modding   # e.g. cd ~/Final-Fantasy-7-Modding
git pull
```

`python` (or `py`) on PATH. Game images stay under `workspace/` (gitignored).

```
workspace/iso-extract/
  FINALFANTASY7_D1.bin              — untouched retail
  FINALFANTASY7_D1.cue
  FINALFANTASY7_D1_encounter.bin    — working copy (create in step 1c)
  FINALFANTASY7_D1_encounter.cue
```

---

## 1. Build a Disc 1 image with the Encounter stub only

Never overwrite `FINALFANTASY7_D1.bin`.

### 1a. Extract `FIELD/FIELD.BIN` (CDmage)

1. Open `FINALFANTASY7_D1.cue` in CDmage  
2. Extract `FIELD/FIELD.BIN` → `workspace/iso-extract/FIELD.BIN`

### 1b. Patch + recompress

```bash
cd /c/path/to/Final-Fantasy-7-Modding
python scripts/build_field_encounter_patch.py workspace/iso-extract/FIELD.BIN
```

Expect `workspace/iso-extract/FIELD.BIN.new` (script default output next to the input).

### 1c. Reimport (CDmage)

1. Copy pristine → `FINALFANTASY7_D1_encounter.bin` + matching `.cue` (point the cue at the new bin name)  
2. Open that working `.cue` in CDmage  
3. Import `FIELD.BIN.new` over **`FIELD/FIELD.BIN`**  
4. If shorter → pad zeros = Yes. If truncate → Cancel and fix.  
5. Save.

### 1d. Smoke test (DuckStation)

Boot `FINALFANTASY7_D1_encounter` — field loads, encounters still happen.

---

## 2. Diff → layer JSON

```bash
python scripts/bin_diff_to_layer.py \
  workspace/iso-extract/FINALFANTASY7_D1.bin \
  workspace/iso-extract/FINALFANTASY7_D1_encounter.bin \
  -o builder/encounter-v0.1.0/layers/disc1.layer.json \
  --id encounter-disc1-v0.1.0 \
  --description "Encounter RCnt2 FORCE stub — NTSC-U Disc 1"
```

### Verify (required)

Use the **same** pristine path as the diff:

```bash
python scripts/apply_layer.py \
  workspace/iso-extract/FINALFANTASY7_D1.bin \
  builder/encounter-v0.1.0/layers/disc1.layer.json \
  --expect workspace/iso-extract/FINALFANTASY7_D1_encounter.bin
```

Must print `OK — layer apply matches --expect`.

---

## 3. Pack metadata

Edit `builder/manifest.json` and set the Encounter entry:

```json
"enabled": true
```

(Only after `disc1.layer.json` exists and verify passed.)

Templates:

- `builder/encounter-v0.1.0/pack.json`  
- `builder/manifest.json`  

---

## 4. Commit and push (JSON only)

```bash
git status
git add builder/encounter-v0.1.0/layers/disc1.layer.json \
        builder/encounter-v0.1.0/pack.json \
        builder/manifest.json
git commit -m "Add Encounter Disc 1 builder layer."
git push
```

Do **not** `git add` any `.bin` / `.cue` / `FIELD.BIN*`.

---

## 5. Tell Mac / agent

Message something like: **Encounter disc1 layer pushed — wire builder.**

After Pages deploys, the main site can load:

`https://individualcontributor.dev/Final-Fantasy-7-Modding/builder/manifest.json`

---

## CSR bases

Cutscene packs are built in the **Final-Fantasy-7-CSR** repo. See:

`Final-Fantasy-7-CSR/builder/WINDOWS-INSTRUCTIONS.md`

---

## Git Bash notes

| Avoid (cmd) | Use (Git Bash) |
|-------------|----------------|
| `scripts\foo.py` | `scripts/foo.py` |
| `^` line continue | `\` at end of line |
| `C:\path\to\repo` | `/c/path/to/repo` or `~/…` |
| Unquoted spaces | Always quote: `"…(patched).bin"` |
