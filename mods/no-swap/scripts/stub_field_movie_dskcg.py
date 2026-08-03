#!/usr/bin/env python3
"""Stub FF7 PSX FIELD.BIN movie + disc-change opcodes (no-swap / no-FMV).

Patches decompressed FIELD overlay then optionally recompresses + injects
into a disc image.

  python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \\
    --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin \\
    --in-place

Stubs (FILE offsets in FIELD.dec, VA base 0x800A0000):
  DSKCG (0x0E Ask/change disc) @ 0x2523C → jr ra; nop
  MOVIE (0xF9 Play movie)      @ 0x2CE94 → jr ra; nop

Does not touch battle Supernova (SNOVA) — separate follow-up.
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
# jr $ra ; nop
STUB = bytes.fromhex("0800e00300000000")
PATCHES = {
    "DSKCG": 0x2523C,
    "MOVIE": 0x2CE94,
}


def decompress_field(comp: bytes) -> bytes:
    if len(comp) <= GZIPPS_HEADER_SIZE:
        raise ValueError("FIELD.BIN too small")
    return gzip.decompress(comp[GZIPPS_HEADER_SIZE:])


def compress_field(dec: bytes, template_header: bytes) -> bytes:
    """GZIPPS: 4-byte dec size LE + 4-byte subheader + gzip payload."""
    if len(template_header) < 8:
        raise ValueError("bad template")
    sub = template_header[4:8]
    payload = gzip.compress(dec, compresslevel=9, mtime=0)
    return struct.pack("<I", len(dec)) + sub + payload


def apply_stubs(dec: bytearray) -> list[str]:
    notes = []
    for name, off in PATCHES.items():
        old = bytes(dec[off : off + 8])
        dec[off : off + 8] = STUB
        notes.append(f"{name} @ 0x{off:X}: {old.hex()} -> {STUB.hex()}")
    return notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--disc-image", type=Path, help="Mode2 .bin to patch in place or to -o")
    ap.add_argument("-o", "--output", type=Path, help="Write new disc image (default: --in-place)")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("--dec-out", type=Path, help="Also write patched FIELD.dec")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.disc_image:
        ap.error("need --disc-image")

    img = bytearray(args.disc_image.read_bytes())
    comp = extract_file(bytes(img), FIELD_PATH)
    dec = bytearray(decompress_field(comp))
    notes = apply_stubs(dec)
    for n in notes:
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
        raise SystemExit(
            f"compressed stub FIELD larger than ISO slot ({len(new_comp)} > {len(comp)}). "
            "Try different gzip settings or cave patch."
        )

    replace_file_padded(img, FIELD_PATH, new_comp)
    out = args.disc_image if args.in_place or not args.output else args.output
    if not args.in_place and not args.output:
        raise SystemExit("pass --in-place or -o OUT.bin")
    out.write_bytes(img)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
