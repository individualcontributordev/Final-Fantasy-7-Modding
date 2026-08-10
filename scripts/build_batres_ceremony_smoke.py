#!/usr/bin/env python3
"""Build pristine D1 with BATRES ceremony patches for fanfare smoke tests.

  python3 scripts/build_batres_ceremony_smoke.py --skip-setup --s4-zero --no-anim4
  python3 scripts/build_batres_ceremony_smoke.py --s4-zero --no-anim4
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.compress_gzipps import compress_gzipps
from scripts.decompress_gzipps import decompress_gzipps
from scripts.psx_mode2_iso import extract_file, replace_file_padded

BATRES_BASE = 0x801B0000
WAIT_VAS = (0x801B02F8, 0x801B032C, 0x801B03A0)
ORI_S4_ZERO = 0x34140000
STOCK_ORI = {0x3414001E, 0x34140008, 0x34140031, ORI_S4_ZERO}
JAL_ANIM_VA = 0x801B028C
JAL_800A7254 = 0x0C029C95
NOP = 0x00000000
SETUP_BR_VA = 0x801B02E0
STOCK_BNE_TO_03B0 = 0x14400033
J_TO_03B0 = 0x08000000 | ((0x801B03B0 & 0x0FFFFFFF) >> 2)


def patch_dec(dec: bytearray, *, s4_zero: bool, no_anim4: bool, skip_setup: bool) -> list[str]:
    log: list[str] = []
    if skip_setup:
        o = SETUP_BR_VA - BATRES_BASE
        old = struct.unpack_from("<I", dec, o)[0]
        if old not in (STOCK_BNE_TO_03B0, J_TO_03B0):
            raise SystemExit(f"unexpected branch at {SETUP_BR_VA:08X}: {old:08X}")
        struct.pack_into("<I", dec, o, J_TO_03B0)
        log.append(f"{SETUP_BR_VA:08X}: setup-br {old:08X} -> j 801B03B0")
    if s4_zero:
        for va in WAIT_VAS:
            o = va - BATRES_BASE
            old = struct.unpack_from("<I", dec, o)[0]
            if old not in STOCK_ORI:
                raise SystemExit(f"unexpected wait word at {va:08X}: {old:08X}")
            struct.pack_into("<I", dec, o, ORI_S4_ZERO)
            log.append(f"{va:08X}: wait {old:08X} -> {ORI_S4_ZERO:08X}")
    if no_anim4:
        o = JAL_ANIM_VA - BATRES_BASE
        old = struct.unpack_from("<I", dec, o)[0]
        if old not in (JAL_800A7254, NOP):
            raise SystemExit(f"unexpected jal at {JAL_ANIM_VA:08X}: {old:08X}")
        struct.pack_into("<I", dec, o, NOP)
        log.append(f"{JAL_ANIM_VA:08X}: jal800A7254 {old:08X} -> nop")
    return log


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--s4-zero", action="store_true")
    ap.add_argument("--no-anim4", action="store_true")
    ap.add_argument("--skip-setup", action="store_true")
    ap.add_argument("--no-s4-zero", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--no-anim-nop", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("-o", "--output", type=Path, default=None)
    args = ap.parse_args()
    positive = args.s4_zero or args.no_anim4 or args.skip_setup
    if not positive:
        s4_zero, no_anim4, skip_setup = (not args.no_s4_zero), (not args.no_anim_nop), False
    else:
        s4_zero, no_anim4, skip_setup = args.s4_zero, args.no_anim4, args.skip_setup
    if not (s4_zero or no_anim4 or skip_setup):
        raise SystemExit("nothing to patch")
    tag = []
    if skip_setup:
        tag.append("skipsetup")
    if s4_zero:
        tag.append("s4zero")
    if no_anim4:
        tag.append("noanim4")
    tag_s = "_".join(tag)
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
    for line in patch_dec(dec, s4_zero=s4_zero, no_anim4=no_anim4, skip_setup=skip_setup):
        print(line)
    patched_dec = dec_dir / f"BATRES.X.{tag_s}.dec"
    patched_dec.write_bytes(dec)
    new_bin = raw_dir / f"BATTLE_BATRES.X.{tag_s}"
    compress_gzipps(patched_dec, raw_path, new_bin)
    if new_bin.stat().st_size > raw_path.stat().st_size:
        raise SystemExit(f"compressed BATRES too big: {new_bin.stat().st_size}")
    img2 = bytearray(pristine.read_bytes())
    replace_file_padded(img2, "BATTLE/BATRES.X", new_bin.read_bytes())
    out = args.output or (ROOT / f"workspace/iso-extract/ff7_d1_batres_{tag_s}.bin")
    out = out if out.is_absolute() else ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img2)
    print(f"PLAY: {out}")


if __name__ == "__main__":
    main()
