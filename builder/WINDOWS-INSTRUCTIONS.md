# Windows (Git Bash): Encounter layers + version naming

## Version rule

| Thing | Version file / flag | Bumps when |
|-------|---------------------|------------|
| Encounter stub | `builder/ENCOUNTER_VERSION` | FORCE stub / rate changes |
| CSR / CSR+ / CSR++ | `--version` on CSR layer build | That cutscene pack changes |

They do **not** need to match. Example this release:

| Pack | Version | Notes |
|------|---------|--------|
| CSR | `0.14.1` | bump from `0.14.0` |
| CSR+ | `0.1.0` | unchanged |
| CSR++ | `0.1.0` | unchanged |
| Encounter | `0.1.1` | lure/2 stub (from `0.1.0`) |

### PPF short names (CSR site `patcher/`)

Match what’s already on the site (no hyphen inside `csrplus` / `csrplusplus`):

```
csr-disc1-v0.14.1.ppf
csr-disc2-v0.14.1.ppf
csr-disc3-v0.14.1.ppf

csrplus-disc1-v0.1.0.ppf
csrplus-disc2-v0.1.0.ppf
csrplus-disc3-v0.1.0.ppf

csrplusplus-disc1-v0.1.0.ppf
…
```

Encounter PPF (optional; builder is preferred for stacks):

```
encounter-disc1-v0.1.1.ppf
```

Builder pack ids keep hyphens: `csr-plus-v0.1.0`, `encounter-on-csr-plus-v0.1.1`.

---

## Setup

```bash
cd /c/path/to/Final-Fantasy-7-Modding
git pull
```

`python` on PATH + network. Pristine discs in `workspace/pristine/FINALFANTASY7_DN.bin`.

Current stub version is in `builder/ENCOUNTER_VERSION` (no need to pass `--version` unless overriding).

---

## Build Encounter layers (recommended)

```bash
# reads version from builder/ENCOUNTER_VERSION (0.1.1)
# pulls CSR base id from live CSR manifest when needed

python scripts/build_encounter_on_base.py --against clean --discs 1
python scripts/build_encounter_on_base.py --against csr-plus --discs 1
# optional:
python scripts/build_encounter_on_base.py --against csr --discs 1
python scripts/build_encounter_on_base.py --against csr-plusplus --discs 1
```

Then:

```bash
git add builder/
git status   # JSON only
git commit -m "Encounter v0.1.1 (lure/2)."
git push
```

Older `encounter-*-v0.1.0` addons are auto-disabled in the manifest when the new pack is written.

---

## CSR base bump (only if releasing CSR 0.14.1)

In **Final-Fantasy-7-CSR**:

```bash
python scripts/build_csr_base_layers.py workspace/csr --version 0.14.1
# copy PPFs → patcher/csr-discN-v0.14.1.ppf
# update index.html PATCHES entries
# commit builder/ + patcher/ + index.html · push
```

CSR+ / CSR++ stay on `0.1.0` — no rebuild unless those packs change.

After CSR `0.14.1` is live, rebuild Encounter against it:

```bash
python scripts/build_encounter_on_base.py --against csr --discs 1
```

(`compatibleBases` becomes `csr-v0.14.1` automatically.)

---

## Manual CDmage fallback

See git history or ask — prefer `build_encounter_on_base.py`.
