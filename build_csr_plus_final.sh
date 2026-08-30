#!/bin/bash
set -euo pipefail

python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin ../Final-Fantasy-7-CSR/builder/csr-plus-v0.1.0/layers/disc1.layer.json -o workspace/iso-extract/ff7_d1_csrplus_step1.bin

# Zero-pad to the size the original proven 7-part endings layer set was
# authored/tested against (766340400 bytes = 325825 Mode2/2352 sectors),
# reintroduced 2026-08-30 to isolate whether dropping this padding (done
# when the build switched off the layered pipeline) affected ENDING01
# playback. Only MOVIE_ID row 25 (D1 slot "smk" -> ENDING01.MOV) is patched,
# per explicit request to minimize disc footprint; this script does a raw
# overwrite (no relocation) at ENDING01's D3-absolute LBA, so field-160
# (plrexp/fallpl) is expected to be clobbered -- that is intentional for
# this isolation test.
python3 -c "
data = bytearray(open('workspace/iso-extract/ff7_d1_csrplus_step1.bin', 'rb').read())
target = 766340400
assert len(data) <= target, f'base image already larger than expected ({len(data)} > {target})'
data.extend(b'\x00' * (target - len(data)))
open('workspace/iso-extract/ff7_d1_csrplus_step1_padded.bin', 'wb').write(data)
"

python3 mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py \
  --d1 workspace/iso-extract/ff7_d1_csrplus_step1_padded.bin \
  -o workspace/iso-extract/ff7_d1_csrplus_final.bin

printf 'FILE "ff7_d1_csrplus_final.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/ff7_d1_csrplus_final.cue

rm -f workspace/iso-extract/ff7_d1_csrplus_step1.bin workspace/iso-extract/ff7_d1_csrplus_step1_padded.bin