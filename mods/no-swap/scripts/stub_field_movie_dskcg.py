#!/usr/bin/env python3
"""Stub FF7 PSX FIELD.BIN movie + disc-change opcodes (no-swap / no-FMV).

Patches decompressed FIELD overlay then optionally recompresses + injects
into a disc image.

  python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \\
    --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin \\
    --in-place

Stubs (FILE offsets in FIELD.dec, VA base 0x800A0000):
  DSKCG (0x0E) @ 0x2523C — complete opcode (PC+=2), no disc wait
  MOVIE (0xF9) @ 0x2CE94 — complete opcode (PC+=1), no FMV

IMPORTANT: bare jr-ra is WRONG — field ops must advance script PC or the
same op re-runs every frame (new-game black screen).

Does not touch battle Supernova (SNOVA).
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

# Script PC advance stubs (see finding). Uses:
#   index = *(u8*)0x800722C4
#   pc    = (u16*)0x800831FC + index
#   *pc  += delta  (1=MOVIE, 2=DSKCG)
#   return 0

def _stub(pc_delta: int) -> bytes:
    def I(op, rs, rt, rd=0, sh=0, fn=0, imm=0):
        if op == 0:
            w = (op << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (sh << 6) | fn
        else:
            w = (op << 26) | (rs << 21) | (rt << 16) | (imm & 0xFFFF)
        return w & 0xFFFFFFFF

    R0, V0, SP, RA = 0, 2, 29, 31
    T0, T1, T2 = 8, 9, 10
    words = [
        I(9, SP, SP, imm=-24),
        I(0x2B, SP, RA, imm=16),
        I(0xF, 0, T0, imm=0x8007),
        I(0x24, T0, T0, imm=0x22C4),
        I(0, 0, T0, T0, sh=1, fn=0),
        I(0xF, 0, T1, imm=0x8008),
        I(9, T1, T1, imm=0x31FC),
        I(0, T1, T0, T1, fn=0x21),
        I(0x25, T1, T2, imm=0),
        I(9, T2, T2, imm=pc_delta),
        I(0x29, T1, T2, imm=0),
        I(0, 0, 0, V0, fn=0x25),
        I(0x23, SP, RA, imm=16),
        I(9, SP, SP, imm=24),
        I(0, RA, 0, 0, fn=8),
        0,
    ]
    return b"".join(w.to_bytes(4, "little") for w in words)


STUBS = {
    "DSKCG": (0x2523C, _stub(2)),
    "MOVIE": (0x2CE94, _stub(1)),
}


def decompress_field(comp: bytes) -> bytes:
    if len(comp) <= GZIPPS_HEADER_SIZE:
        raise ValueError("FIELD.BIN too small")
    return gzip.decompress(comp[GZIPPS_HEADER_SIZE:])


def compress_field(dec: bytes, template_header: bytes) -> bytes:
    sub = template_header[4:8]
    payload = gzip.compress(dec, compresslevel=9, mtime=0)
    return struct.pack("<I", len(dec)) + sub + payload


def apply_stubs(dec: bytearray) -> list[str]:
    notes = []
    for name, (off, stub) in STUBS.items():
        old = bytes(dec[off : off + len(stub)])
        dec[off : off + len(stub)] = stub
        notes.append(f"{name} @ 0x{off:X}: {len(stub)} bytes (PC+{2 if name=='DSKCG' else 1})")
        notes.append(f"  was {old[:16].hex()}...")
        notes.append(f"  now {stub[:16].hex()}...")
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
        raise SystemExit(f"compressed stub FIELD too large: {len(new_comp)} > {len(comp)}")

    replace_file_padded(img, FIELD_PATH, new_comp)
    out = args.disc_image if args.in_place or not args.output else args.output
    if not args.in_place and not args.output:
        raise SystemExit("pass --in-place or -o OUT.bin")
    out.write_bytes(img)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
