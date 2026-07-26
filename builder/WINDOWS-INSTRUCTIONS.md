# Windows (Git Bash): build Encounter layers

Use **Git Bash**. One Encounter pack per builder base (Unmodified / CSR / CSR+ / CSR++).

| Builder base | `--against` | Output pack |
|--------------|-------------|-------------|
| Unmodified | `clean` | `encounter-v…` |
| CSR | `csr` | `encounter-on-csr-v…` |
| CSR+ | `csr-plus` | `encounter-on-csr-plus-v…` |
| CSR++ | `csr-plusplus` | `encounter-on-csr-plusplus-v…` |

Retail Encounter **cannot** stack on CSR. Each CSR base needs its own Encounter pack.

---

## 0. Setup

```bash
cd /c/path/to/Final-Fantasy-7-Modding
git pull
```

`python` on PATH + network (to download published CSR layers).

```
workspace/pristine/
  FINALFANTASY7_D1.bin / .cue
  FINALFANTASY7_D2.bin / .cue
  FINALFANTASY7_D3.bin / .cue
```

You only need **local pristine** discs. CSR base layers are pulled from:

`https://individualcontributor.dev/Final-Fantasy-7-CSR/builder/manifest.json`

---

## Recommended: one command per base (no CDmage)

Downloads the published CSR layer (unless `--against clean`), applies it onto pristine, extracts `FIELD/FIELD.BIN`, applies the stub, pad-injects, diffs, updates `builder/manifest.json`.

```bash
# Unmodified
python scripts/build_encounter_on_base.py --against clean --discs 1 --version 0.1.0

# CSR / CSR+ / CSR++ (Disc 1 examples)
python scripts/build_encounter_on_base.py --against csr --discs 1 --version 0.1.0
python scripts/build_encounter_on_base.py --against csr-plus --discs 1 --version 0.1.0
python scripts/build_encounter_on_base.py --against csr-plusplus --discs 1 --version 0.1.0
```

Optional:

| Flag | Meaning |
|------|---------|
| `--discs 1,2,3` | Multiple discs in one run |
| `--base-layer PATH_OR_URL` | Skip manifest lookup (single disc only) |
| `--csr-manifest URL` | Alternate CSR manifest |
| `--keep-work` | Keep temps under `workspace/iso-extract/_on_base/` |

Needs disk for a ~700MB temp image per disc (deleted unless `--keep-work`). First CSR layer download is large (~10MB+ JSON).

Must print `changedBytes` > 0. Then:

```bash
git add builder/
git status   # no .bin / .cue
git commit -m "Add Encounter-on-base builder layers."
git push
```

Message: **Encounter layers pushed — wire builder.**

Smoke-test in the site builder: pick matching base + Encounter add-on → DuckStation → **New Game**.

---

## Manual CDmage path (fallback)

Only if the automated inject fails. Same as before: copy base → `iso-extract`, CDmage import `FIELD.BIN.new`, then:

```bash
python scripts/build_encounter_layers.py --version 0.1.0 --discs 1 --against csr-plus \
  --base-dir /c/path/to/Final-Fantasy-7-CSR/workspace/csr-plus
```

Or retail:

```bash
python scripts/prepare_encounter_workspace.py --discs 1 --force
# … CDmage extract / stub / import …
python scripts/build_encounter_layers.py --version 0.1.0 --discs 1
```

Full manual steps are unchanged in spirit: never open `workspace/pristine/` in CDmage; only edit copies under `iso-extract/`.

---

## Builder behaviour

Each pack sets `compatibleBases`. The site greys out add-ons that do not match the selected base (e.g. retail Encounter stays disabled on CSR+).

---

## Git Bash notes

| Avoid (cmd) | Use (Git Bash) |
|-------------|----------------|
| `scripts\foo.py` | `scripts/foo.py` |
| `C:\…` | `/c/…` |
| paths with spaces | quote them |
