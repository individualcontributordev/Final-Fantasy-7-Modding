# Windows (Git Bash): Encounter layers

## Versions (this release)

| Pack | Version | Source |
|------|---------|--------|
| CSR | `0.14.1` | CSR repo builder + PPFs |
| CSR+ | `0.1.1` | CSR repo |
| CSR++ | `0.1.1` | CSR repo |
| Encounter | `0.1.1` | `builder/ENCOUNTER_VERSION` |

Encounter `--against` resolves the live CSR base id from Pages (e.g. `csr-plus-v0.1.1`).

---

## After CSR bases are live on Pages

```bash
cd /c/path/to/Final-Fantasy-7-Modding
git pull

python scripts/build_encounter_on_base.py --against clean --discs 1
python scripts/build_encounter_on_base.py --against csr --discs 1
python scripts/build_encounter_on_base.py --against csr-plus --discs 1
python scripts/build_encounter_on_base.py --against csr-plusplus --discs 1

git add builder/
git status   # JSON only — no .bin
git commit -m "Encounter v0.1.1 (lure/2) for clean + CSR bases."
git push
```

No `--version` needed unless overriding `ENCOUNTER_VERSION`.
