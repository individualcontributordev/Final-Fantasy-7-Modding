#!/usr/bin/env python3
"""Apply optional layers, then produce a Makou-safe working BIN.

The base image must be the exact image the first layer targets. For a mod,
this is usually a reconstructed CSR/CSR+/Highwind image, not retail.

Two checkpoints are kept for different reasons:

* 01-layer-stack.bin is the exact builder-side parent for a new mod layer.
* 02-working.bin has synchronized FIELD/WORLD tables, spare FIELD.BIN
  capacity, and repaired EDC/ECC; this is the image opened in Makou.

Do not use 02-working.bin as a mod's layer base unless players really receive
that exact image before the mod is applied. The safety changes between the two
checkpoints belong in the new layer and are reproduced by the final round-trip.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_csrplus_staged import (
    apply_layer,
    stabilize_working_image,
    write_new,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-image", type=Path, required=True)
    parser.add_argument("--layer", type=Path, action="append", default=[])
    parser.add_argument("--table-baseline", type=Path)
    parser.add_argument("--edc-reference", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    base_image = args.base_image.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    if not base_image.is_file():
        raise SystemExit(f"Missing base image: {base_image}")
    if output_dir.exists():
        raise SystemExit(f"Output directory already exists: {output_dir}")

    image = bytearray(base_image.read_bytes())
    for layer_path in args.layer:
        layer_path = layer_path.expanduser().resolve()
        if not layer_path.is_file():
            raise SystemExit(f"Missing layer: {layer_path}")
        apply_layer(image, json.loads(layer_path.read_text(encoding="utf-8")))

    # Preserve the pre-normalization stack because it represents the bytes the
    # browser has immediately before applying the layer being developed.
    stacked = output_dir / "01-layer-stack.bin"
    write_new(stacked, bytes(image))
    table_baseline = (args.table_baseline or base_image).expanduser().resolve()
    working = output_dir / "02-working.bin"
    stabilize_working_image(
        input_image=stacked,
        table_baseline=table_baseline,
        edc_reference=args.edc_reference.expanduser().resolve(),
        output_image=working,
        report_path=output_dir / "stage-report.json",
    )
    print(f"Makou working image: {working}")
    print("Keep 01-layer-stack.bin unchanged; save Makou edits to a new file.")


if __name__ == "__main__":
    main()
