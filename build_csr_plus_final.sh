#!/bin/bash
set -euo pipefail

python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin ../Final-Fantasy-7-CSR/builder/csr-plus-v0.1.0/layers/disc1.layer.json -o workspace/iso-extract/ff7_d1_csrplus_step1.bin

# The 7-part endings layer set (single-disc-endings-v0.1.0-partN) was built against a
# base image padded to 766340400 bytes (325825 Mode2/2352 sectors) — 7468 sectors
# larger than the current CSR+ step1 output. Zero-pad to that size before applying,
# so apply_layer's per-record offsets land on the same absolute positions the layer
# was authored against. This 7-part set (not the narrower 2-part csrplus alias-only
# set) is the one confirmed to patch MOVIE_ID.BIN correctly for the full ending
# movie sequence (IDs 23-29), not just the single aliased ENDING01 slot.
python3 -c "
data = bytearray(open('workspace/iso-extract/ff7_d1_csrplus_step1.bin', 'rb').read())
target = 766340400
assert len(data) <= target, f'base image already larger than expected ({len(data)} > {target})'
data.extend(b'\x00' * (target - len(data)))
open('workspace/iso-extract/ff7_d1_csrplus_step1_padded.bin', 'wb').write(data)
"

cp workspace/iso-extract/ff7_d1_csrplus_step1_padded.bin workspace/iso-extract/ff7_d1_csrplus_endings_build.bin
for part in 1 2 3 4 5 6 7; do
  python3 scripts/apply_layer.py workspace/iso-extract/ff7_d1_csrplus_endings_build.bin "builder/single-disc-endings-v0.1.0-part${part}/layers/disc1.layer.json" -o workspace/iso-extract/ff7_d1_csrplus_endings_next.bin
  mv workspace/iso-extract/ff7_d1_csrplus_endings_next.bin workspace/iso-extract/ff7_d1_csrplus_endings_build.bin
done
mv workspace/iso-extract/ff7_d1_csrplus_endings_build.bin workspace/iso-extract/ff7_d1_csrplus_final.bin

printf 'FILE "ff7_d1_csrplus_final.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/ff7_d1_csrplus_final.cue

rm -f workspace/iso-extract/ff7_d1_csrplus_step1.bin workspace/iso-extract/ff7_d1_csrplus_step1_padded.bin