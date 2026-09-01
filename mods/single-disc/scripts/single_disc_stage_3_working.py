#!/usr/bin/env python3
"""Turn one collapsed Disc 1 image into the unchanged Makou checkpoint."""
from __future__ import annotations

import argparse
from pathlib import Path

from build_csrplus_staged import stabilize_working_image


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--edc-reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    collapsed = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    stabilize_working_image(
        input_image=collapsed,
        table_baseline=collapsed,
        edc_reference=args.edc_reference.expanduser().resolve(),
        output_image=output,
        report_path=args.report.expanduser().resolve(),
    )
    print(f"Makou-safe working checkpoint: {output}")
    print("Keep this file unchanged; save Makou edits to a new filename.")


if __name__ == "__main__":
    main()
