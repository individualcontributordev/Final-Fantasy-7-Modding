#!/usr/bin/env python3
"""Force COS_BTM2 disc-id IFUW gates open on a single-disc work image.

On multi-disc CSR, after the D2 swap savemap disc==2 so IFUW 18 20 00 00 55 a4
falls through into the break choreography. On single-disc disc stays 1, so the
else branch skips the break (black + music). LOST2 MAPJUMP to cos_btm2 was
forced in v0.1.6; this clears the large else-jumps inside COS_BTM2 itself.

  python3 mods/single-disc/scripts/force_cos_btm2_break_ifuw.py \\
    --bin workspace/iso-extract/sd_v016_lost2_break.bin --in-place
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from field_dat import load_field_dat, decode_ops  # noqa: E402
from lzs import compress_all_with_header, decompress_all_with_header  # noqa: E402
from psx_mode2_iso import extract_file, find_file, replace_file_within_sectors  # noqa: E402

FIELD = "FIELD/COS_BTM2.DAT"
# Disc-id style gate used on Cosmo / LOST break path
PAT = bytes.fromhex("1820000055a4")
# Only clear else-jumps that skip real content (leave tiny +3 music taps)
MIN_ELSE = 0x08


def force_ifuw(dec: bytearray) -> list[tuple[int, int]]:
    forced: list[tuple[int, int]] = []
    i = 0
    while True:
        j = bytes(dec).find(PAT, i)
        if j < 0:
            break
        ej = dec[j + 7]
        if ej >= MIN_ELSE:
            dec[j + 7] = 0
            forced.append((j, ej))
        i = j + 1
    return forced


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bin", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()

    img = bytearray(args.bin.read_bytes())
    raw = extract_file(bytes(img), FIELD)
    meta = find_file(img, FIELD)
    nsec = max(1, (meta.size + 2047) // 2048)
    max_bytes = nsec * 2048

    dec = bytearray(decompress_all_with_header(raw))
    forced = force_ifuw(dec)
    if not forced:
        print("no IFUW else-jumps cleared (already open?)")
    for off, ej in forced:
        print(f"  force IFUW @{off:#x} else 0x{ej:02x} -> 0")

    new_raw = compress_all_with_header(bytes(dec))
    print(f"recompressed {len(raw)} -> {len(new_raw)} (sector cap {max_bytes})")
    if len(new_raw) > max_bytes:
        raise SystemExit(f"too large for ISO slot {len(new_raw)} > {max_bytes}")

    # Sanity: scripts still parse and gates are open
    f = load_field_dat(new_raw)
    for s in f.scripts:
        pos = 0
        for rawop, name in decode_ops(s.raw):
            if name == "IFUW" and "55a4" in rawop.hex() and rawop[-1] >= MIN_ELSE:
                raise SystemExit(f"gate still closed {s.entity}/{s.slot} @{pos:#x}")
            pos += len(rawop)

    replace_file_within_sectors(img, FIELD, new_raw)
    out = args.bin if args.in_place or not args.output else args.output
    if not args.in_place and not args.output:
        raise SystemExit("pass --in-place or -o")
    out.write_bytes(img)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
