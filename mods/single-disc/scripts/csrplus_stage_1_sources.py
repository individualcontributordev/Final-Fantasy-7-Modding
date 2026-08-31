#!/usr/bin/env python3
"""Reconstruct CSR and CSR+ trim source discs into one artifact directory."""
from __future__ import annotations

import argparse
from pathlib import Path

from build_csrplus_staged import build_source_artifacts, default_csr_root


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--csr-root", type=Path, default=default_csr_root())
    args = parser.parse_args()

    report = build_source_artifacts(args.csr_root, args.output_dir)
    print(f"Current CSR discs: {report['currentCsrDiscs']}")
    print(f"Current trimmed discs: {report['currentTrimmedDiscs']}")
    print(f"Trim layers: {report['trimLayers']}")


if __name__ == "__main__":
    main()
