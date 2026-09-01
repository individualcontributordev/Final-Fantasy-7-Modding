#!/usr/bin/env python3
"""Build and verify a distributable pack from one finalized disc image.

The command writes:

* an ic-layer-v1 JSON diff and pack.json for publication;
* a release BIN/CUE for emulator and physical-media testing;
* a second BIN rebuilt from --layer-base plus the new layer.

The rebuilt image must be byte-identical to the release image. This is the
local proof that the browser builder can reconstruct the candidate; it does
not replace boot, gameplay, drive verification, or console testing.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from build_csrplus_staged import ENDING_ALIAS_OVERLAPS, build_release_artifacts


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
    parser.add_argument(
        "--ending-alias-included",
        action="store_true",
        help="Allow the one intentional MOVIE extent overlap created by ENDING2E",
    )
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
        allowed_overlaps=(
            ENDING_ALIAS_OVERLAPS if args.ending_alias_included else frozenset()
        ),
    )
    print(f"Layer: {report['layer']}")
    print(f"Builder reconstruction: {report['builderRebuildImage']}")
    print(f"Hardware-test image: {report['releaseImage']}")


if __name__ == "__main__":
    main()
