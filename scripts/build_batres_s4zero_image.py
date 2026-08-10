#!/usr/bin/env python3
"""Build pristine D1 image with BATRES ceremony wait counts forced to 0."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.compress_gzipps import compress_gzipps
from scripts.decompress_gzipps import decompress_gzipps
from scripts.psx_mode2_iso import extract_file, replace_file_padded

BATTLE_BASE = 0x801B0000
# ori s4, zero, imm  -> force imm=0 (skip ceremony wait frames)
WAIT_PATCH_VAS = (0x801B02F8, 0x801B032C, 0x801B03A0)
ORI_S4_ZERO = 0x34140000
STOCK_ORI = {0x3414001E, 0x34140008, 0x34140031}


def main() -> None:
    pristine = ROOT / "workspace/pristine/FINALFANTASY7_D1.bin"
    if not pristine.is_file():
        raise SystemExit(f"missing pristine disc: {pristine}")

    raw_dir = ROOT / "workspace/iso-extract/battle-raw"
    dec_dir = ROOT / "workspace/iso-extract/battle-dec"
    raw_dir.mkdir(parents=True, exist_ok=True)
    dec_dir.mkdir(parents=True, exist_ok=True)

    img = bytearray(pristine.read_bytes())
    raw_path = raw_dir / "BATTLE_BATRES.X"
    raw_path.write_bytes(extract_file(img, "BATTLE/BATRES.X"))

    dec_path = dec_dir / "BATRES.X.dec"
    decompress_gzipps(raw_path, dec_path)

    dec = bytearray(dec_path.read_bytes())
    for va in WAIT_PATCH_VAS:
        o = va - BATTLE_BASE
        old = struct.unpack_from("<I", dec, o)[0]
        print(f"{va:08X}: {old:08X} -> {ORI_S4_ZERO:08X}")
        if old not in STOCK_ORI:
            raise SystemExit(f"unexpected word at {va:08X}: {old:08X}")
        struct.pack_into("<I", dec, o, ORI_S4_ZERO)

    patched_dec = dec_dir / "BATRES.X.s4zero.dec"
    patched_dec.write_bytes(dec)

    new_bin = raw_dir / "BATTLE_BATRES.X.s4zero"
    compress_gzipps(patched_dec, raw_path, new_bin)
    if new_bin.stat().st_size > raw_path.stat().st_size:
        raise SystemExit(
            f"compressed BATRES too big: {new_bin.stat().st_size} > {raw_path.stat().st_size}"
        )

    img2 = bytearray(pristine.read_bytes())
    replace_file_padded(img2, "BATTLE/BATRES.X", new_bin.read_bytes())
    out = ROOT / "workspace/iso-extract/ff7_d1_batres_s4zero.bin"
    out.write_bytes(img2)
    print(f"PLAY: {out}")


if __name__ == "__main__":
    main()
