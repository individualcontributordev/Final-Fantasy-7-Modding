#!/usr/bin/env python3
"""Turn a Makou-saved BIN into verified add-on release artifacts.

The working baseline supplies pre-edit table/allocation evidence, while the
layer base is the exact image a builder user receives before this add-on.
Outputs include a stabilized image, hardware-test BIN/CUE, ``ic-layer-v1``
pack, reports, and an independently rebuilt verification image. Existing output
directories are refused and at least one compatible base is required."""
from __future__ import annotations

import argparse
from pathlib import Path

from makou_workflow import (
    build_release_artifacts,
    stabilize_working_image,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edited-image", type=Path, required=True)
    parser.add_argument("--working-baseline", type=Path, required=True)
    parser.add_argument("--layer-base", type=Path, required=True)
    parser.add_argument("--edc-reference", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--compatible-base", action="append", default=[])
    parser.add_argument("--disc", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--blurb", default="")
    args = parser.parse_args()

    output_dir = args.output_dir.expanduser().resolve()
    if output_dir.exists():
        raise SystemExit(f"Output directory already exists: {output_dir}")

    # Stabilize first so table/EDC repair is part of the published layer, then
    # diff against --layer-base (builder parent), not the Makou working copy.
    stabilized = output_dir / "01-stabilized" / "disc1.bin"
    stabilize_working_image(
        input_image=args.edited_image.expanduser().resolve(),
        table_baseline=args.working_baseline.expanduser().resolve(),
        edc_reference=args.edc_reference.expanduser().resolve(),
        output_image=stabilized,
        report_path=output_dir / "01-stabilized" / "stage-report.json",
    )

    report = build_release_artifacts(
		input_image=stabilized,
        layer_base=args.layer_base.expanduser().resolve(),
        edc_reference=args.edc_reference.expanduser().resolve(),
		output_dir=output_dir / "02-release",
        pack_id=args.pack_id,
        name=args.name,
        version=args.version,
        compatible_bases=args.compatible_base,
        disc=args.disc,
        blurb=args.blurb,
    )
    print(f"Layer: {report['layer']}")
    print(f"Builder reconstruction: {report['builderRebuildImage']}")
    print(f"Hardware-test image: {report['releaseImage']}")


if __name__ == "__main__":
    main()
