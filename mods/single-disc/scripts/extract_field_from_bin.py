#!/usr/bin/env python3
"""Extract a single FIELD/*.DAT file verbatim (still LZS-compressed) out of a
.bin disc image, so it can be fed back into build_work_bin.py's
--blackbgb-manual-bin (or similar) flag on another machine.

Usage (from repo root):
  python3 mods/single-disc/scripts/extract_field_from_bin.py \
      path/to/your-manual-edit.bin \
      --field BLACKBGB \
      -o workspace/iso-extract/BLACKBGB.manual.dat

Then, back on the machine building the release, either:
  a) pass the whole manual-edit .bin straight to build_work_bin.py:
       python3 mods/single-disc/scripts/build_work_bin.py \
           -o OUT.bin --blackbgb-manual-bin path/to/your-manual-edit.bin
  b) or hand the extracted .dat to whoever is diffing it.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from psx_mode2_iso import extract_file  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bin_path", type=Path, help="Path to the .bin disc image to extract from")
    ap.add_argument("--field", default="BLACKBGB", help="Field name (default: BLACKBGB)")
    ap.add_argument("-o", "--output", type=Path, required=True, help="Where to write the extracted .DAT")
    args = ap.parse_args()

    if not args.bin_path.is_file():
        print(f"Missing bin: {args.bin_path}", file=sys.stderr)
        return 1

    img = args.bin_path.read_bytes()
    path = f"FIELD/{args.field}.DAT"
    data = extract_file(img, path)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print(f"Extracted {path} from {args.bin_path.name}: {len(data)} bytes -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
