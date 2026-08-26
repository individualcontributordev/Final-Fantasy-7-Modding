#!/usr/bin/env python3
"""Bisect the single-disc-on-csr core layer by applying only the first N
records (sorted by disc offset, which is how the layer JSON already stores
them) on top of pristine D1 + CSR. Used to binary-search which slice of the
single-disc merge introduces the JUNAIR battle-return freeze, since the
freeze is confirmed pre-existing in the full core layer and absent with
just CSR alone.

  python3 mods/single-disc/scripts/bisect_core_layer.py --count 31725
  python3 mods/single-disc/scripts/bisect_core_layer.py --count 0        # CSR only, baseline
  python3 mods/single-disc/scripts/bisect_core_layer.py --all            # full core layer

Writes workspace/iso-extract/bisect_core_N<count>.bin and a matching .cue.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_layer import apply_layer  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, help="number of leading records to apply from the core layer")
    ap.add_argument("--all", action="store_true", help="apply every record (equivalent to the full core build)")
    args = ap.parse_args()

    pristine = ROOT / "workspace/pristine/FINALFANTASY7_D1.bin"
    csr_layer = ROOT.parent / "Final-Fantasy-7-CSR/builder/csr-v0.14.2/layers/disc1.layer.json"
    if not csr_layer.is_file():
        csr_layer = ROOT / "../Final-Fantasy-7-CSR/builder/csr-v0.14.2/layers/disc1.layer.json"
    csr_layer = csr_layer.resolve()
    core_layer_path = ROOT / "builder/single-disc-on-csr/layers/disc1.layer.json"
    out_dir = ROOT / "workspace/iso-extract"
    out_dir.mkdir(parents=True, exist_ok=True)

    for p, label in [(pristine, "pristine D1"), (csr_layer, "CSR layer"), (core_layer_path, "core layer")]:
        if not p.is_file():
            print("MISSING", label, p, file=sys.stderr)
            return 1

    core_layer = json.loads(core_layer_path.read_text(encoding="utf-8"))
    total = len(core_layer["records"])

    if args.all:
        count = total
    elif args.count is None:
        print(f"core layer has {total} records total; pass --count N (0..{total}) or --all", file=sys.stderr)
        return 1
    else:
        count = max(0, min(args.count, total))

    mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(core_layer_path.stat().st_mtime))
    print(f"USING [core layer] {core_layer_path}  (mtime {mtime}, {total} records)")
    print(f"Applying first {count}/{total} records ({count / total:.1%})")

    img = bytearray(pristine.read_bytes())
    apply_layer(img, json.loads(csr_layer.read_text(encoding="utf-8")))
    print("   after CSR:", len(img), "bytes")

    partial_layer = dict(core_layer)
    partial_layer["records"] = core_layer["records"][:count]
    apply_layer(img, partial_layer)
    print("   after partial core layer:", len(img), "bytes")

    stem = f"bisect_core_N{count}"
    out_bin = out_dir / f"{stem}.bin"
    out_cue = out_dir / f"{stem}.cue"
    out_bin.write_bytes(img)
    out_cue.write_text(f'FILE "{out_bin.name}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    print("WROTE", out_bin)
    print("WROTE", out_cue)
    if count < total:
        last = core_layer["records"][count - 1] if count > 0 else None
        nxt = core_layer["records"][count] if count < total else None
        print(f"last applied record offset:  {last['offset'] if last else 'none'}")
        print(f"next unapplied record offset: {nxt['offset'] if nxt else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
