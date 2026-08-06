#!/usr/bin/env python3
"""Extract one FIELD/<NAME>.DAT from a disc image or CSR-stacked image.

When to use:
  - You need the raw CSR or pristine map file on disk before inject/compare.
  - Prefer this over hand-carving ISOs.

Not for: opcode diffs (use compare_field_dat.py) or writing files back
(use put_field_dat.py).

Examples:
  python3 scripts/extract_field_dat.py --from csr:1 --field DEL1 -o /tmp/DEL1.DAT
  python3 scripts/extract_field_dat.py --from pristine:2 --field LOST2 -o out.DAT
  python3 scripts/extract_field_dat.py --bin path/to/work.bin --field DEL1 -o out.DAT
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from disc_sources import (  # noqa: E402
    field_iso_path,
    load_csr_image,
    load_pristine_image,
    normalize_field_name,
)
from psx_mode2_iso import extract_file  # noqa: E402


def load_source(spec: str) -> bytes:
    if spec.startswith("pristine:"):
        return bytes(load_pristine_image(int(spec.split(":", 1)[1])))
    if spec.startswith("csr:"):
        return bytes(load_csr_image(int(spec.split(":", 1)[1])))
    path = Path(spec).expanduser()
    if not path.is_file():
        raise SystemExit(f"missing image: {path}")
    return path.read_bytes()


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--from",
        dest="source",
        metavar="SPEC",
        help="pristine:N | csr:N  (N = 1|2|3)",
    )
    src.add_argument("--bin", type=Path, help="path to a MODE2/2352 .bin image")
    ap.add_argument("--field", "-f", required=True, help="map name, e.g. DEL1")
    ap.add_argument("-o", "--output", type=Path, required=True, help="write .DAT here")
    args = ap.parse_args()

    if args.bin is not None:
        img = args.bin.read_bytes()
        label = str(args.bin)
    else:
        img = load_source(args.source)
        label = args.source

    name = normalize_field_name(args.field)
    iso = field_iso_path(name)
    try:
        data = extract_file(img, iso)
    except FileNotFoundError as e:
        raise SystemExit(f"{label}: {e}") from e

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print(f"OK {label} {iso} → {args.output} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
