#!/bin/bash
set -euo pipefail

python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin ../Final-Fantasy-7-CSR/builder/csr-plus-v0.1.0/layers/disc1.layer.json -o workspace/iso-extract/ff7_d1_csrplus_step1.bin

# Only patch MOVIE_ID row 25 (D1 slot "smk" -> ENDING01.MOV), per explicit
# request to minimize disc footprint and avoid touching any other movie
# slot. This script relocates (not overwrites) any D1 movie whose sectors
# would otherwise collide with the raw ENDING01 write, so field-160
# (plrexp/fallpl) and every other movie stay at their original bytes unless
# their sectors physically overlap the ENDING01 write range.
python3 mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py \
  --d1 workspace/iso-extract/ff7_d1_csrplus_step1.bin \
  -o workspace/iso-extract/ff7_d1_csrplus_final.bin

printf 'FILE "ff7_d1_csrplus_final.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/ff7_d1_csrplus_final.cue

rm -f workspace/iso-extract/ff7_d1_csrplus_step1.bin