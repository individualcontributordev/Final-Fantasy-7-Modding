# Field random encounters

RCnt2 FORCE stub in `FIELD/FIELD.BIN` — **Light / Standard / Dense** presets.

Play via https://individualcontributor.dev/builder/. Release steps: repo root README.

```bash
# prompts: Light / Standard / Dense / All
python mods/field-random-encounters/scripts/build_all_rates.py

# or non-interactive
python mods/field-random-encounters/scripts/build_on_base.py --against csr-plus --density light --discs 1
```

- `VERSION` — pack version  
- `patches/` — stub bytes + technical notes  
- `scripts/` — build entrypoints (`density.py` owns the presets/menu)  
