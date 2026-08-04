# Task: Finish single-disc-on-csr BLACKBGB; then Highwind

## Done (agent)

- Partial pack: builder/single-disc-on-csr-v0.1.1 vs csr-v0.14.1
- 17 FIELD maps from Clean recipe + SNOVA/BATTLE.X LBA v3
- FIELD.BIN left as CSR (no Clean engine delta)
- BLACKBGB left as CSR (cannot paste Clean file - CSR hub conflict)
- Work: workspace/iso-extract/ff7_d1_csr_single_disc_work.bin
- CSR base: workspace/iso-extract/ff7_d1_csr_base.bin
- Finding: docs/findings/2026-08-04-single-disc-on-csr-build-status.md

## Now (operator Makou)

1. Open ff7_d1_csr_single_disc_work.bin in Makou Reactor
2. Field blackbgb - remove all Ask for disc; keep CSR jumps/bits
3. Save FIELD into the same work bin
4. Rebuild layer vs CSR base (script below)
5. verify_builder_config vs csr-v0.14.1 + pack
6. DuckStation CSR + CSR+ + single-disc-on-csr smoke

### Rebuild layer after Makou

python3 -c "
import json, sys
from pathlib import Path
sys.path.insert(0, \"scripts\")
from bin_diff_to_layer import build_layer
base = Path(\"workspace/iso-extract/ff7_d1_csr_base.bin\")
work = Path(\"workspace/iso-extract/ff7_d1_csr_single_disc_work.bin\")
out = Path(\"builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json\")
layer = build_layer(base, work, layer_id=\"single-disc-on-csr-v0.1.1-disc1\",
    description=\"Single-disc on CSR D1 after BLACKBGB Makou\")
out.write_text(json.dumps(layer, indent=2) + chr(10))
print(layer[\"stats\"])
"

### Verify

python3 scripts/verify_builder_config.py \\
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \\
  --disc 1 --base csr-v0.14.1 \\
  --addon single-disc-on-csr-v0.1.1

## After CSR pack complete

- single-disc-on-highwind-v0.1.1 (same core recipe vs highwind-v0.2.0)
- Defer CSR-alone manip-movie pack (disc size)

## Evidence

BLACKBGB Makou done:
Layer rebuild:
verify_builder_config:
CSR+ smoke:
Notes:

Say check when BLACKBGB is done, or want Highwind next without waiting.
