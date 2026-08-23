#!/usr/bin/env python3
"""Build the current CSR Disc 1 base image (pristine D1 + CSR's disc1.layer.json).

Used as the diff baseline for `bin_diff_to_layer.py` when rebuilding
`single-disc-on-csr`'s layer (see docs/INSTRUCTIONS.md). Writes to a
gitignored workspace path so nothing binary ends up staged.

  python3 scripts/build_csr_d1_base.py
  python3 scripts/build_csr_d1_base.py -o workspace/tmp/csr_d1_base.bin
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from disc_sources import load_csr_image  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "-o",
        "--output",
        default=str(ROOT / "workspace/tmp/csr_d1_base.bin"),
        help="Output path (default: workspace/tmp/csr_d1_base.bin)",
    )
    args = ap.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    img = load_csr_image(1)
    out.write_bytes(img)
    print("wrote", len(img), "->", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
