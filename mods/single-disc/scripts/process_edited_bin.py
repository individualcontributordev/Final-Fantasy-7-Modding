#!/usr/bin/env python3
"""Turn a Makou-saved BIN into release artifacts in one safe command.

Use --snova-disc3 only for the collapsed CSR+ base. Other bases and mods omit
it and go directly from the stabilized edit to layer creation.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from build_csrplus_staged import (
    build_release_artifacts,
    inject_snova_image,
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
    parser.add_argument("--kind", choices=("base", "mod"), required=True)
    parser.add_argument("--compatible-base", action="append", default=[])
    parser.add_argument("--disc", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--blurb", default="")
    parser.add_argument("--snova-disc3", type=Path)
    args = parser.parse_args()

    output_dir = args.output_dir.expanduser().resolve()
    if output_dir.exists():
        raise SystemExit(f"Output directory already exists: {output_dir}")

    stabilized = output_dir / "01-stabilized" / "disc1.bin"
    stabilize_working_image(
        input_image=args.edited_image.expanduser().resolve(),
        table_baseline=args.working_baseline.expanduser().resolve(),
        edc_reference=args.edc_reference.expanduser().resolve(),
        output_image=stabilized,
        report_path=output_dir / "01-stabilized" / "stage-report.json",
    )

    release_input = stabilized
    if args.snova_disc3:
        release_input = output_dir / "02-postprocess" / "disc1-snova.bin"
        inject_snova_image(
            input_image=stabilized,
            disc3=args.snova_disc3.expanduser().resolve(),
            output_image=release_input,
            report_path=output_dir / "02-postprocess" / "stage-report.json",
        )

    report = build_release_artifacts(
        input_image=release_input,
        layer_base=args.layer_base.expanduser().resolve(),
        edc_reference=args.edc_reference.expanduser().resolve(),
        output_dir=output_dir / "03-release",
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
