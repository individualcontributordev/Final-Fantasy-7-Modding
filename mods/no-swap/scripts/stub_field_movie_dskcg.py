#!/usr/bin/env python3
"""Stub FIELD DSKCG + MOVIE (no-swap / no-FMV) — v4.

History:
  v1 jr-ra only → black screen (no PC++)
  v2 PC++ only → audio, still stuck (incomplete)
  v3 PC++ + entity* writes → still stuck (likely bad entity ptr at intro)
  v4 PC++ + flag clears, **no entity dereference** (match original fast path)

  python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \\
    --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin --in-place
"""
from __future__ import annotations

import argparse
import gzip
import struct
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(_SCRIPTS))
from decompress_gzipps import GZIPPS_HEADER_SIZE  # noqa: E402
from psx_mode2_iso import extract_file, replace_file_padded  # noqa: E402

FIELD_PATH = "FIELD/FIELD.BIN"


def _I(op, rs, rt, rd=0, sh=0, fn=0, imm=0):
    if op == 0:
        w = (op << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (sh << 6) | fn
    else:
        w = (op << 26) | (rs << 21) | (rt << 16) | (imm & 0xFFFF)
    return w & 0xFFFFFFFF


def _B(ws):
    return b"".join(w.to_bytes(4, "little") for w in ws)


def stub_pc(delta: int) -> bytes:
    R0, V0, AT, RA = 0, 2, 1, 31
    T0, T1, T2 = 8, 9, 10
    return _B(
        [
            _I(0xF, 0, T0, imm=0x8007),
            _I(0x24, T0, T0, imm=0x22C4),
            _I(0, 0, T0, T0, sh=1, fn=0),
            _I(0xF, 0, T1, imm=0x8008),
            _I(9, T1, T1, imm=0x31FC),
            _I(0, T1, T0, T1, fn=0x21),
            _I(0x25, T1, T2, imm=0),
            _I(9, T2, T2, imm=delta),
            _I(0x29, T1, T2, imm=0),
            _I(0xF, 0, AT, imm=0x8007),
            _I(0x28, AT, R0, imm=0x1C1C),
            _I(0xF, 0, AT, imm=0x8011),
            _I(0x29, AT, R0, imm=17620),
            _I(0, 0, 0, V0, fn=0x25),
            _I(0, RA, 0, 0, fn=8),
            0,
        ]
    )


STUBS = {"DSKCG": (0x2523C, stub_pc(2)), "MOVIE": (0x2CE94, stub_pc(1))}


def decompress_field(comp: bytes) -> bytes:
    return gzip.decompress(comp[GZIPPS_HEADER_SIZE:])


def compress_field(dec: bytes, template_header: bytes) -> bytes:
    return struct.pack("<I", len(dec)) + template_header[4:8] + gzip.compress(
        dec, compresslevel=9, mtime=0
    )


def apply_stubs(dec: bytearray) -> list[str]:
    notes = []
    for name, (off, stub) in STUBS.items():
        old = bytes(dec[off : off + 8])
        dec[off : off + len(stub)] = stub
        notes.append(f"{name} @ 0x{off:X}: {len(stub)}B v4 no-entity (was {old.hex()})")
    return notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--disc-image", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("--dec-out", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    img = bytearray(args.disc_image.read_bytes())
    comp = extract_file(bytes(img), FIELD_PATH)
    dec = bytearray(decompress_field(comp))
    for n in apply_stubs(dec):
        print(n)
    if args.dec_out:
        args.dec_out.write_bytes(dec)
    if args.dry_run:
        print("dry-run: no disc write")
        return 0
    new_comp = compress_field(bytes(dec), comp[:8])
    print(f"recompressed FIELD.BIN {len(comp)} -> {len(new_comp)} (slot {len(comp)})")
    if len(new_comp) > len(comp):
        raise SystemExit(f"too large {len(new_comp)} > {len(comp)}")
    replace_file_padded(img, FIELD_PATH, new_comp)
    out = args.disc_image if args.in_place or not args.output else args.output
    if not args.in_place and not args.output:
        raise SystemExit("pass --in-place or -o")
    out.write_bytes(img)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
