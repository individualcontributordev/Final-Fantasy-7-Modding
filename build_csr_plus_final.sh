#!/bin/bash
set -euo pipefail

python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin ../Final-Fantasy-7-CSR/builder/csr-plus-v0.1.0/layers/disc1.layer.json -o workspace/iso-extract/ff7_d1_csrplus_step1.bin

# Console hardware validates Mode2 Form1 EDC/ECC on read; apply_layer.py only
# rewrites the 2048-byte user-data payload and leaves the old trailer stale
# (fine for emulators, fatal on real hardware/optical drives). Recompute it
# for every sector the layer touched, before the raw-sector D3 movie write
# below (those sectors are copied verbatim from a real disc and must not be
# recomputed -- see repair_edc_ecc_vs_pristine.py header).
python3 mods/single-disc/scripts/repair_edc_ecc_vs_pristine.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --in workspace/iso-extract/ff7_d1_csrplus_step1.bin \
  -o workspace/iso-extract/ff7_d1_csrplus_step1.bin

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

# alias_d3_ending_lbas_on_d1.py itself patches Form1 sectors after our first
# repair pass (directory entries via _patch_dirent_lba_size, MINT/MOVIE_ID.BIN,
# and the PVD volume space size), leaving those stale again. Repair once more
# against pristine. Safe/idempotent: repair_sector_edc_ecc skips Form2 sectors,
# so the raw-copied D3 movie sectors (already valid from a real disc) are left
# untouched.
python3 mods/single-disc/scripts/repair_edc_ecc_vs_pristine.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --in workspace/iso-extract/ff7_d1_csrplus_final.bin \
  -o workspace/iso-extract/ff7_d1_csrplus_final.bin

printf 'FILE "ff7_d1_csrplus_final.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/ff7_d1_csrplus_final.cue

rm -f workspace/iso-extract/ff7_d1_csrplus_step1.bin workspace/iso-extract/ff7_d1_csrplus_step1_padded.bin