#!/usr/bin/env python3
"""Put the truncated Disc 3 ENDING2E stream into a collapsed Disc 1 image."""
from __future__ import annotations

import argparse
from pathlib import Path

from build_csrplus_staged import inject_ending_alias_image


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--disc3", type=Path, required=True)
    parser.add_argument("--edc-reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    report = inject_ending_alias_image(
        input_image=args.input.expanduser().resolve(),
        disc3=args.disc3.expanduser().resolve(),
        edc_reference=args.edc_reference.expanduser().resolve(),
        output_image=args.output.expanduser().resolve(),
        report_path=args.report.expanduser().resolve(),
    )
    print(f"Ending-included image: {report['output']}")


if __name__ == "__main__":
    main()
