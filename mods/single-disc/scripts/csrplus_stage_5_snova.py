#!/usr/bin/env python3
"""Inject the Disc 3 SNOVA files after all Makou editing is finished.

The filename is historical: both collapsed CSR+ and Highwind use this stage.
SNOVA is deliberately appended after editing because Makou owns the normal ISO
filesystem, while this injector also remaps hard-coded BATTLE.X sector values.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from build_csrplus_staged import inject_snova_image


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--disc3", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    inject_snova_image(
        input_image=args.input.expanduser().resolve(),
        disc3=args.disc3.expanduser().resolve(),
        output_image=args.output.expanduser().resolve(),
        report_path=args.report.expanduser().resolve(),
    )
    print(f"SNOVA-injected image: {args.output}")


if __name__ == "__main__":
    main()
