#!/usr/bin/env python3
"""Write a FIELD/<NAME>.DAT into a MODE2/2352 disc image (in place or new file).

When to use:
  - Install a chosen CSR disc's map onto a single-disc D1 work image.
  - Must fit existing ISO slot size (padded shorter; refuses longer).

Not for: comparing maps (compare_field_dat.py) or building full packs
(bin_diff_to_layer.py after your work bin is ready).

Examples:
  python3 scripts/put_field_dat.py --bin work.bin --field DEL1 --dat DEL1.DAT
  python3 scripts/put_field_dat.py --bin work.bin --field DEL1 --dat DEL1.DAT -o out.bin
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from disc_sources import field_iso_path, normalize_field_name  # noqa: E402
from psx_mode2_iso import extract_file, replace_file_padded  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--bin", type=Path, required=True, help="input disc image")
    ap.add_argument("--field", "-f", required=True, help="map name, e.g. DEL1")
    ap.add_argument("--dat", type=Path, required=True, help="source .DAT bytes")
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write image here (default: overwrite --bin)",
    )
    ap.add_argument(
        "--check-same-as",
        type=Path,
        help="after put, require extracted DAT == this file",
    )
    args = ap.parse_args()

    if not args.bin.is_file():
        raise SystemExit(f"missing image: {args.bin}")
    if not args.dat.is_file():
        raise SystemExit(f"missing DAT: {args.dat}")

    data = args.dat.read_bytes()
    iso = field_iso_path(args.field)
    img = bytearray(args.bin.read_bytes())
    try:
        replace_file_padded(img, iso, data)
    except ValueError as e:
        raise SystemExit(str(e)) from e

    got = extract_file(bytes(img), iso)
    if got != data:
        # trailing ISO pad may make file size larger than payload; compare prefix
        if not got.startswith(data):
            raise SystemExit("put failed: extracted bytes do not start with source DAT")
        if got[len(data) :] != b"\x00" * (len(got) - len(data)):
            raise SystemExit("put failed: non-zero padding after DAT payload")

    out = args.output or args.bin
    out.write_bytes(img)
    print(f"OK wrote {iso} ({len(data)} bytes payload) → {out}")

    if args.check_same_as:
        ref = args.check_same_as.read_bytes()
        # compare LZS payload intent: full source file equality if same length
        if data != ref:
            raise SystemExit("--check-same-as does not match --dat")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
