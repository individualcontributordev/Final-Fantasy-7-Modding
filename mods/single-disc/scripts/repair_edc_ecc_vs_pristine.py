#!/usr/bin/env python3
"""Repair EDC/ECC for every sector changed by apply_layer.py, relative to a
pristine reference image. Required for console-hardware playback: the PSX
BIOS/drive firmware validates Mode 2 Form 1 EDC/ECC on read, unlike most
emulators which tolerate stale checksums (see psx_mode2_iso.py).

Only touches sectors that differ from `--pristine` (i.e. sectors patched by
the ISO9660 file-replacement layer, which only rewrites the 2048-byte user
data and leaves the old EDC/ECC trailer stale). Sectors appended past the
pristine image's length are also repaired (covers any relocated files).

Run this BEFORE any step that writes raw whole sectors copied verbatim from
a real disc (e.g. alias_d3_ending_lbas_on_d1.py) -- those sectors already
carry valid EDC/ECC from the source disc and must not be recomputed.

    python3 repair_edc_ecc_vs_pristine.py --pristine d1.bin --in step1.bin -o step1_edc.bin
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from edc_ecc import repair_sector_edc_ecc  # noqa: E402

SECTOR = 2352


def repair_vs_pristine(img: bytearray, pristine: bytes) -> int:
    total = len(img) // SECTOR
    plen = len(pristine) // SECTOR
    fixed = 0
    for i in range(total):
        off = i * SECTOR
        sector = img[off : off + SECTOR]
        if i >= plen or sector != pristine[off : off + SECTOR]:
            repair_sector_edc_ecc(sector)
            img[off : off + SECTOR] = sector
            fixed += 1
    return fixed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pristine", required=True, type=Path)
    ap.add_argument("--in", dest="inp", required=True, type=Path)
    ap.add_argument("-o", "--out", required=True, type=Path)
    args = ap.parse_args()

    pristine = args.pristine.read_bytes()
    img = bytearray(args.inp.read_bytes())

    fixed = repair_vs_pristine(img, pristine)
    print(f"EDC/ECC repaired: {fixed:,} / {len(img)//SECTOR:,} sectors modified vs pristine")

    args.out.write_bytes(img)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
