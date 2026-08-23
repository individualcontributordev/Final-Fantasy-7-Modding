#!/usr/bin/env python3
"""Extract a single FIELD/*.DAT file verbatim (still LZS-compressed) out of a
.bin disc image, e.g. to diff a manual Makou Reactor edit into a new
ic-layer-v1 JSON diff via scripts/bin_diff_to_layer.py (see
build_work_bin.py's --blackbgb-manual-bin flag, which applies such a diff --
NOT a raw extracted .dat -- against the CSR D1 base at build time).

Usage (from repo root):
  python3 mods/single-disc/scripts/extract_field_from_bin.py \
      path/to/your-manual-edit.bin \
      --field BLACKBGB \
      -o workspace/iso-extract/BLACKBGB.manual.dat

Then diff the extracted .dat against the CSR D1 base's own extracted
FIELD/BLACKBGB.DAT using scripts/bin_diff_to_layer.py's build_layer() to
produce a new ic-layer-v1 JSON diff -- do not commit the raw .dat itself.
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
