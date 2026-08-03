#!/usr/bin/env python3
"""FIELD no-swap stubs.

Default (v6): **DSKCG only** — force-complete disc-change opcode.
MOVIE left vanilla (entry stubs softlocked intro).

DSKCG v6:
  - stack frame
  - entity* = *(u32*)0x8009C6E0; if non-null: clear byte@1 (leave wait state)
  - script PC[index] += 2
  - return 0
Does NOT start disc UI / fade (skips that path entirely).

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
DSKCG_OFF = 0x2523C


def _I(op, rs, rt, rd=0, sh=0, fn=0, imm=0):
    if op == 0:
        w = (op << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (sh << 6) | fn
    else:
        w = (op << 26) | (rs << 21) | (rt << 16) | (imm & 0xFFFF)
    return w & 0xFFFFFFFF


def _B(ws):
    return b"".join((w & 0xFFFFFFFF).to_bytes(4, "little") for w in ws)


def dskcg_v6() -> bytes:
    """Force-complete DSKCG without disc UI."""
    # beq encoding: relative in instructions from delay slot
    # Sequence:
    #   addiu sp,sp,-24
    #   sw ra,16(sp)
    #   lui t0,0x800a
    #   lw t0,-14624(t0)     # entity*
    #   nop
    #   beq t0,zero, +3      # skip sb if null (to after sb)
    #   nop
    #   sb zero,1(t0)
    #   lui t1,0x8007
    #   lbu t1,0x22C4(t1)
    #   sll t1,t1,1
    #   lui t2,0x8008
    #   addiu t2,t2,0x31FC
    #   addu t2,t2,t1
    #   lhu t3,0(t2)
    #   addiu t3,t3,2
    #   sh t3,0(t2)
    #   or v0,zero,zero
    #   lw ra,16(sp)
    #   addiu sp,sp,24
    #   jr ra
    #   nop
    R0, V0, SP, RA = 0, 2, 29, 31
    T0, T1, T2, T3 = 8, 9, 10, 11
    # beq t0, zero, +3  means skip 3 insns after delay: nop, sb, then land on lui t1
    # From beq at index 5, delay=6, target offset = 5+1+3 = 9 → lui t1
    # relative = 3 from instruction after delay (index 7 is sb, 8 would be next)
    # standard: target = (pc_of_beq + 4) + (rel<<2); rel counted in words from delay slot
    # we want to branch to lui t1 which is 2 words after beq+delay (skip nop and sb)
    # delay is nop; after delay is sb; after sb is lui. rel=+2 from delay slot.
    beq_rel = 2
    return _B(
        [
            _I(9, SP, SP, imm=-24),
            _I(0x2B, SP, RA, imm=16),
            _I(0xF, 0, T0, imm=0x800A),
            _I(0x23, T0, T0, imm=-14624),
            0,  # nop
            _I(4, T0, R0, imm=beq_rel),  # beq t0, zero, +2
            0,  # delay nop
            _I(0x28, T0, R0, imm=1),  # sb zero, 1(t0)
            _I(0xF, 0, T1, imm=0x8007),
            _I(0x24, T1, T1, imm=0x22C4),
            _I(0, 0, T1, T1, sh=1, fn=0),
            _I(0xF, 0, T2, imm=0x8008),
            _I(9, T2, T2, imm=0x31FC),
            _I(0, T2, T1, T2, fn=0x21),
            _I(0x25, T2, T3, imm=0),
            _I(9, T3, T3, imm=2),
            _I(0x29, T2, T3, imm=0),
            _I(0, 0, 0, V0, fn=0x25),
            _I(0x23, SP, RA, imm=16),
            _I(9, SP, SP, imm=24),
            _I(0, RA, 0, 0, fn=8),
            0,
        ]
    )


def decompress_field(comp: bytes) -> bytes:
    return gzip.decompress(comp[GZIPPS_HEADER_SIZE:])


def compress_field(dec: bytes, template_header: bytes) -> bytes:
    return struct.pack("<I", len(dec)) + template_header[4:8] + gzip.compress(
        dec, compresslevel=9, mtime=0
    )


def apply(dec: bytearray) -> list[str]:
    stub = dskcg_v6()
    old = bytes(dec[DSKCG_OFF : DSKCG_OFF + 8])
    dec[DSKCG_OFF : DSKCG_OFF + len(stub)] = stub
    return [
        f"DSKCG @ 0x{DSKCG_OFF:X}: {len(stub)}B v6 force-complete (was {old.hex()})",
        "MOVIE: left vanilla",
    ]


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
    for n in apply(dec):
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
