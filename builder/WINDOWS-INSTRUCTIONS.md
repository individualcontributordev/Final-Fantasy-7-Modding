# Windows (Git Bash): Encounter layers

## Versions (this release)

| Pack | Version | Source |
|------|---------|--------|
| CSR | `0.14.1` | CSR repo builder + PPFs |
| CSR+ | `0.1.1` | CSR repo |
| CSR++ | `0.1.1` | CSR repo |
| Encounter | `0.1.2` | `builder/ENCOUNTER_VERSION` — rates **25 / 50 / 75** |

Encounter `--against` resolves the live CSR base id from Pages (e.g. `csr-plus-v0.1.1`).

Rates are % of raw `lure/256` (default lure 16 → ~1.6% / 3.1% / 4.7% per check).

---

## Build all rates × all bases (Disc 1)

Needs `workspace/pristine/FINALFANTASY7_D1.bin` (never open in CDmage).

```bash
cd /c/path/to/Final-Fantasy-7-Modding
git pull

python scripts/build_all_encounter_rates.py

git add builder/
git status   # JSON only — no .bin
git commit -m "Encounter v0.1.2 — 25/50/75% for clean + CSR bases."
git push
```

One pack:

```bash
python scripts/build_encounter_on_base.py --against csr-plus --rate 25 --discs 1
```

New builds **do not** auto-disable older Encounter packs. Set `"enabled": false` in `builder/manifest.json` yourself when you want to hide one.

No `--version` needed unless overriding `ENCOUNTER_VERSION`.
