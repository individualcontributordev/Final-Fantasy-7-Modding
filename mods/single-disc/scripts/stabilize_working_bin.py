#!/usr/bin/env python3
"""Normalize a Makou-saved BIN before post-processing or release.

Makou can change compressed archive sizes and may leave raw-sector footers
stale. The shared stabilizer therefore re-synchronizes FIELD.BIN/WORLD.BIN
lookup tables, preserves or expands the known-safe FIELD.BIN reservation,
repairs Mode2 Form1 EDC/ECC, and rejects invalid ISO layouts.

--table-baseline is the unchanged working BIN opened in Makou. Its directory
layout records the intentional reservation and prevents a save from silently
shrinking that safety margin.

--edc-reference should be the retail image for this disc. It is used only to
identify changed sectors; EDC/ECC is calculated from the edited sector itself,
not copied from retail.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from build_csrplus_staged import stabilize_working_image


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--table-baseline", type=Path, required=True)
    parser.add_argument("--edc-reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    stabilize_working_image(
        input_image=args.input.expanduser().resolve(),
        table_baseline=args.table_baseline.expanduser().resolve(),
        edc_reference=args.edc_reference.expanduser().resolve(),
        output_image=args.output.expanduser().resolve(),
        report_path=args.report.expanduser().resolve(),
    )
    print(f"Stabilized image: {args.output}")


if __name__ == "__main__":
    main()
