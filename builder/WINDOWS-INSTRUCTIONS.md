# Windows (Git Bash): build Encounter layers for all discs

Use **Git Bash**. Mods ship **one layer per disc** (Disc 1 / 2 / 3). Absolute `.bin` offsets differ per disc, so do not reuse a Disc 1 layer on Disc 2/3.

Goal: `builder/encounter-v0.1.0/layers/disc{1,2,3}.layer.json`

---

## 0. Setup

```bash
cd /c/path/to/Final-Fantasy-7-Modding   # or ~/Final-Fantasy-7-Modding
git pull
```

`python` on PATH. Images under `workspace/iso-extract/` (gitignored):

```
workspace/iso-extract/
  FINALFANTASY7_D1.bin / .cue              — pristine
  FINALFANTASY7_D2.bin / .cue
  FINALFANTASY7_D3.bin / .cue
  FINALFANTASY7_D1_encounter.bin / .cue    — working copies (create below)
  FINALFANTASY7_D2_encounter.bin / .cue
  FINALFANTASY7_D3_encounter.bin / .cue
```

---

## 1. Patch each disc (repeat for N = 1, 2, 3)

Never overwrite pristine `FINALFANTASY7_DN.bin`.

### 1a. Extract `FIELD/FIELD.BIN` (CDmage)

1. Open `FINALFANTASY7_DN.cue`  
2. Extract `FIELD/FIELD.BIN` → `workspace/iso-extract/FIELD.BIN`  
   (overwrite this extract each disc — or use `FIELD.BIN.D{N}` if you prefer)

### 1b. Stub + recompress

```bash
python scripts/build_field_encounter_patch.py workspace/iso-extract/FIELD.BIN
```

Expect `workspace/iso-extract/FIELD.BIN.new`.

### 1c. Reimport (CDmage)

1. Copy pristine → `FINALFANTASY7_DN_encounter.bin` + matching `.cue`  
2. Import `FIELD.BIN.new` over **`FIELD/FIELD.BIN`**  
3. Pad if shorter; **never** accept truncate  
4. Save  

### 1d. Smoke test (DuckStation)

Boot that disc’s encounter image — field loads, encounters still happen.

---

## 2. Diff + verify all discs (one command)

After D1–D3 encounter images exist:

```bash
python scripts/build_encounter_layers.py --version 0.1.0
# or only some discs:
python scripts/build_encounter_layers.py --version 0.1.0 --discs 1,2,3
```

This writes layers, updates `pack.json`, and sets `builder/manifest.json` `"enabled": true` with a **discs** map for 1/2/3.

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

## CSR bases

`Final-Fantasy-7-CSR/builder/WINDOWS-INSTRUCTIONS.md` — already multi-disc.

---

## Git Bash notes

| Avoid (cmd) | Use (Git Bash) |
|-------------|----------------|
| `scripts\foo.py` | `scripts/foo.py` |
| `^` | `\` |
| `C:\…` | `/c/…` or `~/…` |
