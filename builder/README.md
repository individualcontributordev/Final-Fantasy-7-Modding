# Encounter builder packs

Ship Encounter layers for https://individualcontributor.dev/builder/

Version: `ENCOUNTER_VERSION` (bump **before** a release build).

```bash
python scripts/build_all_encounter_rates.py
git add builder/
git commit -m "Encounter vX.Y.Z — Light/Standard/Dense for clean + CSR bases."
git push
```

See `WINDOWS-INSTRUCTIONS.md`. Players use the disc builder, not a separate Encounter PPF page.
