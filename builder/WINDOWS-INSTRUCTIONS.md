# Windows (Git Bash): build Encounter layers for all discs

Use **Git Bash**. Mods ship **one layer per disc** (Disc 1 / 2 / 3). Absolute `.bin` offsets differ per disc, so do not reuse a Disc 1 layer on Disc 2/3.

Goal: `builder/encounter-v0.1.0/layers/disc{1,2,3}.layer.json`

**Why two folders:** CDmage can auto-save when you import `FIELD.BIN.new`. The open image is what gets updated — so keep retail masters in `workspace/pristine/` and only open copies under `workspace/iso-extract/`. No Save As needed.

---

## 0. Setup

```bash
cd /c/path/to/Final-Fantasy-7-Modding   # or ~/Final-Fantasy-7-Modding
git pull
```

`python` on PATH. Layout (binaries gitignored):

```
workspace/pristine/                         — retail masters (never open in CDmage)
  FINALFANTASY7_D1.bin / .cue
  FINALFANTASY7_D2.bin / .cue
  FINALFANTASY7_D3.bin / .cue

workspace/iso-extract/                      — disposable working copies
  FINALFANTASY7_DN.bin / .cue               — prepare script, then CDmage import
  FIELD.BIN / FIELD.BIN.new
```

One-time: put clean Disc 1–3 images into `workspace/pristine/` (same names as above).

---

## 1. Patch each disc (repeat for N = 1, 2, 3)

### 1a. Refresh working copy from the vault

```bash
python scripts/prepare_encounter_workspace.py --discs N
# if iso-extract already has that disc:
python scripts/prepare_encounter_workspace.py --discs N --force
```

Copies `pristine/FINALFANTASY7_DN.*` → `iso-extract/FINALFANTASY7_DN.*`.

**Never open anything under `workspace/pristine/` in CDmage.**

### 1b. Extract `FIELD/FIELD.BIN` (CDmage)

1. Open **`workspace/iso-extract/FINALFANTASY7_DN.cue`**  
2. Extract `FIELD/FIELD.BIN` → `workspace/iso-extract/FIELD.BIN`

### 1c. Stub + recompress

```bash
python scripts/build_field_encounter_patch.py workspace/iso-extract/FIELD.BIN
```

Expect `workspace/iso-extract/FIELD.BIN.new`.

### 1d. Import (CDmage)

With that same `iso-extract` image still open:

1. Import `FIELD.BIN.new` over **`FIELD/FIELD.BIN`**  
2. Pad if shorter; **never** accept truncate  
3. If CDmage auto-saves, that updates the **working** `.bin` only — vault is untouched  

No Save As. The open file is the patched image.

### 1e. Smoke test (DuckStation)

Boot `workspace/iso-extract/FINALFANTASY7_DN` — field loads, encounters still happen.

---

## 2. Diff + verify

```bash
python scripts/build_encounter_layers.py --version 0.1.0 --discs 1
# or after all discs are ready:
python scripts/build_encounter_layers.py --version 0.1.0 --discs 1,2,3
```

Uses:

| Role | Path |
|------|------|
| Pristine | `workspace/pristine/FINALFANTASY7_DN.bin` |
| Patched | `workspace/iso-extract/FINALFANTASY7_DN.bin` |

Writes layers, updates `pack.json`, sets `builder/manifest.json` `"enabled": true`.

**Must see `changedBytes` > 0.** Empty diff usually means import never stuck, the vault is already patched, or you ran `prepare --force` after patching (wiped the working copy).

```bash
python -c "import json; d=json.load(open('builder/encounter-v0.1.0/layers/disc1.layer.json')); print(d['stats'])"
```

---

## 3. Commit and push (JSON only)

```bash
git add builder/
git status   # no .bin / .cue / FIELD.BIN*
git commit -m "Add Encounter builder layers for all discs."
git push
```

Then message: **Encounter layers pushed — wire builder.**

---

## Stacking with CSR

The retail Encounter layer **cannot** stack on CSR / CSR+ / CSR++ in the builder — it overwrites CSR’s `FIELD.BIN` region and breaks New Game. Manifest sets `compatibleBases: ["clean"]`.

To ship CSR+Encounter later: prepare from a CSR-patched image, stub that disc’s `FIELD.BIN`, diff CSR base vs CSR+stub, publish a separate layer (or rebuild against each base).

---

## CSR bases

`Final-Fantasy-7-CSR/builder/WINDOWS-INSTRUCTIONS.md` — same idea (`workspace/pristine/` vs patched folders).

---

## Git Bash notes

| Avoid (cmd) | Use (Git Bash) |
|-------------|----------------|
| `scripts\foo.py` | `scripts/foo.py` |
| `^` | `\` |
| `C:\…` | `/c/…` or `~/…` |
