# World map random encounters

Same density model as Field encounters (Light / Standard / Dense), targeting **`WORLD.BIN`** instead of `FIELD.BIN`.

**Status:** scaffold only — not in the disc builder yet.

When layers exist they will ship as separate add-ons (`exclusiveGroup: world-map-encounter-rate`) so players can pick Field and World Map densities independently.

## Planned build

```bash
# (future)
python mods/world-map-random-encounters/scripts/build_all_rates.py
```

Version file is ready for the first release.
