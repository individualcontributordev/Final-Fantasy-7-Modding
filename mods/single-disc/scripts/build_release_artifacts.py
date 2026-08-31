#!/usr/bin/env python3
"""Build a layer, pack metadata, and hardware-test BIN/CUE from one image."""
from __future__ import annotations

import argparse
from pathlib import Path

from build_csrplus_staged import build_release_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--layer-base",
        type=Path,
        required=True,
        help="Exact image this layer will be applied to",
    )
    parser.add_argument("--edc-reference", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--kind", choices=("base", "mod"), required=True)
    parser.add_argument("--compatible-base", action="append", default=[])
    parser.add_argument("--disc", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--blurb", default="")
    args = parser.parse_args()

    report = build_release_artifacts(
        input_image=args.input.expanduser().resolve(),
        layer_base=args.layer_base.expanduser().resolve(),
        edc_reference=args.edc_reference.expanduser().resolve(),
        output_dir=args.output_dir.expanduser().resolve(),
        pack_id=args.pack_id,
        name=args.name,
        version=args.version,
        kind=args.kind,
        compatible_bases=args.compatible_base,
        disc=args.disc,
        blurb=args.blurb,
    )
    print(f"Layer: {report['layer']}")
    print(f"Hardware-test image: {report['releaseImage']}")


if __name__ == "__main__":
    main()
