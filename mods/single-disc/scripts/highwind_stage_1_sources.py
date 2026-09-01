#!/usr/bin/env python3
"""Reconstruct Highwind's three source discs and pinned shared-field source."""
from __future__ import annotations

import argparse
from pathlib import Path

from highwind_pipeline import build_highwind_source_artifacts, default_csr


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--csr-root", type=Path, default=default_csr())
    args = parser.parse_args()

    report = build_highwind_source_artifacts(args.csr_root, args.output_dir)
    print(f"Highwind source discs: {report['highwindDiscs']}")
    print(f"Pinned shared-field source: {report['sharedFieldsImage']}")


if __name__ == "__main__":
    main()
