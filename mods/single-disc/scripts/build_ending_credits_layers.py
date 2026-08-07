#!/usr/bin/env python3
"""Diff playtest+endings bin into multi-part ic-layer packs (GitHub size safe).

Base (original): ff7_d1_playtest_csr_sd_movies.bin
Modified:        ff7_d1_playtest_ending_test.bin

Writes builder/single-disc-endings-v0.1.0-partN/layers/disc1.layer.json
Each part keeps changed payload under ~32 MiB (~JSON under ~100 MiB).

  python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
  python3 mods/single-disc/scripts/build_ending_credits_layers.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))

from bin_diff_to_layer import MAX_RECORD_BYTES, iter_runs  # noqa: E402

# Keep JSON file under GitHub hard limit (100 MiB); hex ~2x + quotes.
MAX_CHANGED_PER_PART = 30 * 1024 * 1024
PACK_PREFIX = "single-disc-endings-v0.1.0"


def _flush_part(
    part_idx: int,
    records: list[dict],
    changed: int,
    orig_size: int,
    mod_size: int,
) -> Path:
    pack_id = f"{PACK_PREFIX}-part{part_idx}"
    out = _ROOT / "builder" / pack_id / "layers" / "disc1.layer.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    layer = {
        "format": "ic-layer-v1",
        "id": f"{pack_id}-disc1",
        "description": (
            f"Single-disc ending/credits movies on D1 (part {part_idx}). "
            "Stack after Single-disc (+ CSR movies when auto)."
        ),
        "target": "disc-image",
        "stats": {
            "originalBytes": orig_size,
            "modifiedBytes": mod_size,
            "changedBytes": changed,
            "records": len(records),
        },
        "records": records,
    }
    text = json.dumps(layer, indent=2) + "\n"
    out.write_text(text, encoding="utf-8")
    mb = out.stat().st_size / (1024 * 1024)
    print(f"WROTE {out.relative_to(_ROOT)}  json={mb:.1f}MiB  changed={changed/1024/1024:.1f}MiB  recs={len(records)}")
    if out.stat().st_size >= 100 * 1024 * 1024:
        raise SystemExit(f"part {part_idx} still >= 100 MiB")
    return out


def main() -> int:
    base = _ROOT / "workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin"
    end = _ROOT / "workspace/iso-extract/ff7_d1_playtest_ending_test.bin"
    if not base.is_file() or not end.is_file():
        print("missing playtest or ending bin — run build_ending_credits_test_bin.py", file=sys.stderr)
        return 1
    orig_size = base.stat().st_size
    mod_size = end.stat().st_size

    part = 1
    records: list[dict] = []
    changed = 0
    paths: list[Path] = []

    for off, data in iter_runs(base, end):
        # split long run into MAX_RECORD_BYTES pieces already in iter_runs
        piece = len(data)
        if records and changed + piece > MAX_CHANGED_PER_PART:
            paths.append(_flush_part(part, records, changed, orig_size, mod_size))
            part += 1
            records, changed = [], 0
        records.append({"offset": off, "hex": data.hex()})
        changed += piece

    if records:
        paths.append(_flush_part(part, records, changed, orig_size, mod_size))

    print(f"parts={len(paths)}")
    meta = _ROOT / "builder" / f"{PACK_PREFIX}-PARTS.txt"
    meta.write_text("\n".join(str(p.relative_to(_ROOT)) for p in paths) + "\n", encoding="utf-8")
    print("WROTE", meta.relative_to(_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
