#!/usr/bin/env python3
"""Apply an ``ic-layer-v1`` JSON patch to a disc-image byte buffer.

Inputs are a raw image and ordered records containing absolute byte offsets and
hex payloads; the optional output is a patched BIN, and ``--expect`` verifies
the exact result. Records may grow an image, but growth is zero-filled and
rounded to a 2352-byte raw-sector boundary. This is a byte-layer tool: it does
not interpret ISO9660 files or repair sector EDC/ECC."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def apply_layer(image: bytearray, layer: dict) -> None:
    """Apply ordered replacement records in place, preserving declared image growth."""
    if layer.get("format") != "ic-layer-v1":
        raise SystemExit("expected format ic-layer-v1")
    if layer.get("target") not in (None, "disc-image"):
        raise SystemExit(f"unsupported target: {layer.get('target')}")
    # Capture size before records — growth pad check must use this, not post-apply len.
    baseline_len = len(image)
    # Records are applied in file order. This permits overlap intentionally,
    # with later bytes winning, and matches the browser builder's layer model.
    for rec in layer["records"]:
        offset = int(rec["offset"])
        data = bytes.fromhex(rec["hex"])
        end = offset + len(data)
        if end > len(image):
            image.extend(b"\x00" * (end - len(image)))
        image[offset:end] = data
    # Grown images: trailing zeros often match zero-pad of a shorter original and
    # are omitted from records. Honor stats.modifiedBytes when this layer was
    # built against an image the same size as our baseline (before records).
    # Always finish on a 2352-byte boundary if we grew (Mode2 safety).
    stats = layer.get("stats") or {}
    original = stats.get("originalBytes")
    target = stats.get("modifiedBytes")
    if (
        isinstance(target, int)
        and target > len(image)
        and isinstance(original, int)
        and original == baseline_len
    ):
        image.extend(b"\x00" * (target - len(image)))
    SECTOR = 2352
    if len(image) > baseline_len and len(image) % SECTOR:
        image.extend(b"\x00" * (SECTOR - (len(image) % SECTOR)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("layer", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--expect", type=Path, help="Patched image that must match after apply")
    args = ap.parse_args()

    image = bytearray(args.image.read_bytes())
    layer = json.loads(args.layer.read_text(encoding="utf-8"))
    apply_layer(image, layer)

    if args.expect:
        expect = args.expect.read_bytes()
        # Compare overlapping length; allow trailing pad differences only if sizes match
        if bytes(image) != expect:
            # find first mismatch
            lim = min(len(image), len(expect))
            for i in range(lim):
                if image[i] != expect[i]:
                    print(f"MISMATCH at offset {i} (0x{i:X})", file=sys.stderr)
                    return 1
            if len(image) != len(expect):
                print(
                    f"MISMATCH size {len(image)} vs {len(expect)}",
                    file=sys.stderr,
                )
                return 1
            print("MISMATCH (unknown)", file=sys.stderr)
            return 1
        print("OK — layer apply matches --expect")
    if args.output:
        args.output.write_bytes(image)
        print(f"Wrote {args.output} ({len(image)} bytes)")
    elif not args.expect:
        print(f"Applied OK ({len(layer['records'])} records, {len(image)} bytes) — pass -o to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
