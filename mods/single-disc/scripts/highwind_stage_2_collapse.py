#!/usr/bin/env python3
"""Collapse staged Highwind Disc 2/3 field changes into Disc 1."""
from __future__ import annotations

import argparse
from pathlib import Path

from build_csrplus_staged import configure_sources
from highwind_pipeline import collapse_highwind_disc1, default_csr


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--csr-root", type=Path, default=default_csr())
    args = parser.parse_args()

    configure_sources(args.csr_root.expanduser().resolve())
    output, report = collapse_highwind_disc1(args.sources_dir, args.output_dir)
    print(f"Table-fixed Highwind image: {output}")
    print(f"Unambiguous Disc 2/3 merges: {report['unambiguousMerges']}")
    retained_count = len(report["collisionsKeptFromDisc1"])
    print(f"Fields retained from Disc 1 for review: {retained_count}")


if __name__ == "__main__":
    main()
