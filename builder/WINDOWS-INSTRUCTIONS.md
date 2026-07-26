# Windows (Git Bash): build Encounter layers for all discs

Use **Git Bash**. Mods ship **one layer per disc** (Disc 1 / 2 / 3). Absolute `.bin` offsets differ per disc, so do not reuse a Disc 1 layer on Disc 2/3.

**Why two folders:** CDmage auto-saves on `FIELD.BIN` import into the open file. Keep masters outside `iso-extract/` and only open working copies there. No Save As needed.

There are **four** Encounter packs (separate add-ons in the builder):

| Builder base | `--against` | Diff left side (stack base) | Output pack |
|--------------|-------------|-----------------------------|-------------|
| Unmodified | `clean` (default) | `workspace/pristine/` | `encounter-v…` |
| CSR | `csr` | CSR repo `workspace/csr/` | `encounter-on-csr-v…` |
| CSR+ | `csr-plus` | CSR repo `workspace/csr-plus/` | `encounter-on-csr-plus-v…` |
| CSR++ | `csr-plusplus` | CSR repo `workspace/csr-plusplus/` | `encounter-on-csr-plusplus-v…` |

Retail Encounter **cannot** stack on CSR — it overwrites CSR’s `FIELD.BIN` and breaks New Game. Each CSR stack needs its **own** Encounter layer built from that base’s image.

---

## 0. Setup

```bash
cd /c/path/to/Final-Fantasy-7-Modding   # or ~/Final-Fantasy-7-Modding
git pull
```

`python` on PATH.

```
workspace/pristine/                 — retail masters (never open in CDmage)
  FINALFANTASY7_D1.bin / .cue …
workspace/iso-extract/              — disposable working copies only
  FINALFANTASY7_DN.bin / .cue
  FIELD.BIN / FIELD.BIN.new
```

CSR patched images stay in the **CSR** repo (do not move them into Modding pristine):

```
/c/path/to/Final-Fantasy-7-CSR/workspace/csr/FINALFANTASY7_DN (patched).bin
/c/path/to/Final-Fantasy-7-CSR/workspace/csr-plus/…
/c/path/to/Final-Fantasy-7-CSR/workspace/csr-plusplus/…
```

Set a shortcut once per shell (edit the path):

```bash
CSR_WS=/c/path/to/Final-Fantasy-7-CSR/workspace
```

---

## A. Unmodified + Encounter (retail)

### A1. Working copy from retail vault

```bash
python scripts/prepare_encounter_workspace.py --discs 1
# replace existing working copy:
python scripts/prepare_encounter_workspace.py --discs 1 --force
```

### A2–A4. Extract → stub → import

1. Open **`workspace/iso-extract/FINALFANTASY7_D1.cue`** in CDmage  
2. Extract `FIELD/FIELD.BIN` → `workspace/iso-extract/FIELD.BIN`  
3. Stub:

```bash
python scripts/build_field_encounter_patch.py workspace/iso-extract/FIELD.BIN
```

4. Import `FIELD.BIN.new` over **`FIELD/FIELD.BIN`** (pad if shorter; never truncate). Auto-save is fine.

### A5. Diff

```bash
python scripts/build_encounter_layers.py --version 0.1.0 --discs 1
# same as: --against clean
```

Must show `changedBytes` > 0. Then commit `builder/` JSON only.

---

## B. CSR / CSR+ / CSR++ + Encounter (one pack per base)

Repeat the whole block for each base you want (`csr`, `csr-plus`, `csr-plusplus`). Example = **CSR+ Disc 1**.

### B1. Working copy from that CSR base (not retail)

```bash
python scripts/prepare_encounter_workspace.py --discs 1 --force \
  --from-dir "$CSR_WS/csr-plus"
```

This copies `FINALFANTASY7_D1 (patched).bin` → `iso-extract/FINALFANTASY7_D1.bin`.  
**Do not** open files under the CSR workspace in CDmage for import.

### B2–B4. Extract → stub → import

Same as A2–A4 on the **iso-extract** working image. The stub must be applied to **CSR+’s** `FIELD.BIN`, not retail’s.

### B5. Diff against that CSR base

```bash
python scripts/build_encounter_layers.py --version 0.1.0 --discs 1 \
  --against csr-plus \
  --base-dir "$CSR_WS/csr-plus"
```

| Base | `--against` | `--base-dir` |
|------|-------------|--------------|
| CSR | `csr` | `$CSR_WS/csr` |
| CSR+ | `csr-plus` | `$CSR_WS/csr-plus` |
| CSR++ | `csr-plusplus` | `$CSR_WS/csr-plusplus` |

Writes e.g. `builder/encounter-on-csr-plus-v0.1.0/` and appends that add-on to `builder/manifest.json` with `compatibleBases: ["csr-plus-v0.1.0"]`. Retail `encounter-v0.1.0` is left alone.

### B6. Smoke test

Boot the **iso-extract** working image in DuckStation — New Game must load (this image is CSR+ with Encounter already applied).

---

## C. Commit and push (JSON only)

```bash
git add builder/
git status   # no .bin / .cue / FIELD.BIN*
git commit -m "Add Encounter builder layers."
git push
```

Then message: **Encounter layers pushed — wire builder.**

---

## Builder behaviour

- Each Encounter pack lists `compatibleBases`. The site builder greys out add-ons that do not match the selected base.
- Pick **CSR+** + **Encounter rate (on CSR+)**, not the retail Encounter add-on.

---

## Git Bash notes

| Avoid (cmd) | Use (Git Bash) |
|-------------|----------------|
| `scripts\foo.py` | `scripts/foo.py` |
| `^` | `\` |
| `C:\…` | `/c/…` or `~/…` |
| paths with spaces | quote them: `"$CSR_WS/csr-plus"` |
