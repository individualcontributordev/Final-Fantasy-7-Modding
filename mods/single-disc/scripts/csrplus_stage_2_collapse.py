#!/usr/bin/env python3
"""Collapse staged CSR Disc 2/3 FIELD changes into a Disc 1 image."""
from __future__ import annotations

import argparse
from pathlib import Path

from build_csrplus_staged import (
    collapse_to_disc1,
    configure_sources,
    default_csr_root,
    sha256,
    write_json,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--csr-root", type=Path, default=default_csr_root())
    args = parser.parse_args()

    configure_sources(args.csr_root.expanduser().resolve())
    output = collapse_to_disc1(
        args.sources_dir.expanduser().resolve(),
        args.output_dir.expanduser().resolve(),
    )
    report = {
        "stage": "csrplus-collapse",
        "sourcesDir": str(args.sources_dir),
        "output": str(output),
        "outputSha256": sha256(output),
    }
    report_path = args.output_dir / "stage-report.json"
    write_json(report_path, report)
    print(f"Table-fixed collapsed image: {output}")


if __name__ == "__main__":
    main()
