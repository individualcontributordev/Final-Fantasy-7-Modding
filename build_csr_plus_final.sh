#!/bin/bash
set -euo pipefail

python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin ../Final-Fantasy-7-CSR/builder/csr-plus-v0.1.0/layers/disc1.layer.json -o workspace/iso-extract/ff7_d1_csrplus_step1.bin

python3 scripts/apply_layer.py workspace/iso-extract/ff7_d1_csrplus_step1.bin builder/single-disc-endings-csrplus-v0.1.0-part1/layers/disc1.layer.json -o workspace/iso-extract/ff7_d1_csrplus_step2.bin

python3 scripts/apply_layer.py workspace/iso-extract/ff7_d1_csrplus_step2.bin builder/single-disc-endings-csrplus-v0.1.0-part2/layers/disc1.layer.json -o workspace/iso-extract/ff7_d1_csrplus_final.bin

printf 'FILE "ff7_d1_csrplus_final.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/ff7_d1_csrplus_final.cue

rm workspace/iso-extract/ff7_d1_csrplus_step*.bin