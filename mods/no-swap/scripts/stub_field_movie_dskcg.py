#!/usr/bin/env python3
"""Stub FF7 PSX FIELD DSKCG + MOVIE with full completion (no wait / no FMV).

v1 bare jr-ra → black screen (no PC advance).
v2 PC-only → audio can still play; field may not resume (state/flags).
v3 clear entity movie state + flags + PC advance + return 0.

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


def _bytes(ws):
    return b"".join(w.to_bytes(4, "little") for w in ws)


def movie_stub():
    R0, V0, AT, RA, A0, T0, T1, T2 = 0, 2, 1, 31, 4, 8, 9, 10
    return _bytes(
        [
            _I(0xF, 0, A0, imm=0x800A),
            _I(0x23, A0, A0, imm=-14624),
            _I(0x28, A0, R0, imm=1),
            _I(0x29, A0, R0, imm=38),
            _I(0xF, 0, T0, imm=0x8007),
            _I(0x24, T0, T0, imm=0x22C4),
            _I(0, 0, T0, T0, sh=1, fn=0),
            _I(0xF, 0, T1, imm=0x8008),
            _I(9, T1, T1, imm=0x31FC),
            _I(0, T1, T0, T1, fn=0x21),
            _I(0x25, T1, T2, imm=0),
            _I(9, T2, T2, imm=1),
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


def dskcg_stub():
    R0, V0, RA, A0, T0, T1, T2 = 0, 2, 31, 4, 8, 9, 10
    return _bytes(
        [
            _I(0xF, 0, A0, imm=0x800A),
            _I(0x23, A0, A0, imm=-14624),
            _I(0x28, A0, R0, imm=1),
            _I(0x29, A0, R0, imm=38),
            _I(0xF, 0, T0, imm=0x8007),
            _I(0x24, T0, T0, imm=0x22C4),
            _I(0, 0, T0, T0, sh=1, fn=0),
            _I(0xF, 0, T1, imm=0x8008),
            _I(9, T1, T1, imm=0x31FC),
            _I(0, T1, T0, T1, fn=0x21),
            _I(0x25, T1, T2, imm=0),
            _I(9, T2, T2, imm=2),
            _I(0x29, T1, T2, imm=0),
            _I(0, 0, 0, V0, fn=0x25),
            _I(0, RA, 0, 0, fn=8),
            0,
        ]
    )


STUBS = {"DSKCG": (0x2523C, dskcg_stub()), "MOVIE": (0x2CE94, movie_stub())}


def decompress_field(comp: bytes) -> bytes:
    return gzip.decompress(comp[GZIPPS_HEADER_SIZE:])


def compress_field(dec: bytes, template_header: bytes) -> bytes:
    sub = template_header[4:8]
    payload = gzip.compress(dec, compresslevel=9, mtime=0)
    return struct.pack("<I", len(dec)) + sub + payload


def apply_stubs(dec: bytearray) -> list[str]:
    notes = []
    for name, (off, stub) in STUBS.items():
        old = bytes(dec[off : off + 8])
        dec[off : off + len(stub)] = stub
        notes.append(f"{name} @ 0x{off:X}: {len(stub)}B complete-stub (was {old.hex()})")
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
        print("wrote", args.dec_out)
    if args.dry_run:
        print("dry-run: no disc write")
        return 0
    new_comp = compress_field(bytes(dec), comp[:8])
    print(f"recompressed FIELD.BIN {len(comp)} -> {len(new_comp)} (slot {len(comp)})")
    if len(new_comp) > len(comp):
        raise SystemExit(f"compressed too large {len(new_comp)} > {len(comp)}")
    replace_file_padded(img, FIELD_PATH, new_comp)
    out = args.disc_image if args.in_place or not args.output else args.output
    if not args.in_place and not args.output:
        raise SystemExit("pass --in-place or -o")
    out.write_bytes(img)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
