# Windows: build Encounter layer for the disc builder

Do this on the PC that has your pristine discs, CDmage, DuckStation, and this repo.

Goal: publish `builder/encounter-v0.1.0/layers/disc1.layer.json` (no game `.bin` in git).

---

## 0. Setup

```bat
cd C:\path\to\Final-Fantasy-7-Modding
git pull
```

Python 3 on PATH. Game images stay under `workspace\` (gitignored).

Put files here (names can vary — adjust commands):

```
workspace\iso-extract\
  FINALFANTASY7_D1.bin
  FINALFANTASY7_D1.cue
```

---

## 1. Build a Disc 1 image with the Encounter stub only

Use a **copy** of pristine (never overwrite the only pristine).

### 1a. Extract `FIELD\FIELD.BIN` (CDmage)

1. Open `FINALFANTASY7_D1.cue` in CDmage  
2. Extract `FIELD\FIELD.BIN` → `workspace\iso-extract\FIELD.BIN`

### 1b. Patch + recompress

```bat
cd C:\path\to\Final-Fantasy-7-Modding
python scripts\build_field_encounter_patch.py workspace\iso-extract\FIELD.BIN
```

Expect `workspace\iso-extract\FIELD.BIN.new`.

### 1c. Reimport (CDmage)

1. Copy pristine → `workspace\iso-extract\FINALFANTASY7_D1_encounter.bin` (+ matching `.cue`)  
2. Open that working `.cue` in CDmage  
3. Import `FIELD.BIN.new` over **`FIELD\FIELD.BIN`**  
4. If shorter → pad zeros = Yes. If truncate → Cancel and fix.  
5. Save.

### 1d. Smoke test (DuckStation)

Boot `FINALFANTASY7_D1_encounter` — field loads, encounters still happen.

---

## 2. Diff → layer JSON

```bat
python scripts\bin_diff_to_layer.py ^
  workspace\iso-extract\FINALFANTASY7_D1.bin ^
  workspace\iso-extract\FINALFANTASY7_D1_encounter.bin ^
  -o builder\encounter-v0.1.0\layers\disc1.layer.json ^
  --id encounter-disc1-v0.1.0 ^
  --description "Encounter RCnt2 FORCE stub — NTSC-U Disc 1"
```

### Verify (required)

```bat
python scripts\apply_layer.py ^
  workspace\iso-extract\FINALFANTASY7_D1_pristine.bin ^
  builder\encounter-v0.1.0\layers\disc1.layer.json ^
  --expect workspace\iso-extract\FINALFANTASY7_D1_encounter.bin
```

Must print `OK — layer apply matches --expect`.

---

## 3. Pack metadata

Edit `builder\manifest.json` and set the Encounter entry:

```json
"enabled": true
```

(Only after `disc1.layer.json` exists and verify passed.)

Templates:

- `builder\encounter-v0.1.0\pack.json`  
- `builder\manifest.json`  


---

## 4. Commit and push (JSON only)

```bat
git status
git add builder\encounter-v0.1.0\layers\disc1.layer.json builder\encounter-v0.1.0\pack.json builder\manifest.json
git commit -m "Add Encounter Disc 1 builder layer."
git push
```

Do **not** `git add` any `.bin` / `.cue`.

---

## 5. Tell Mac / agent

Message something like: **Encounter disc1 layer pushed — wire builder.**

After Pages deploys, the main site can load:

`https://individualcontributor.dev/Final-Fantasy-7-Modding/builder/manifest.json`

---

## CSR bases

Cutscene packs are built in the **CSR** repo. See:

`Final-Fantasy-7-CSR\builder\WINDOWS-INSTRUCTIONS.md`
