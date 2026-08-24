#!/usr/bin/env python3
"""Build CSR + single-disc core .bin — NO manip-movies.

This is the base used by isolated feature tests (e.g. ending movies) that
also need to apply cleanly to other bases (e.g. "highwind") where none of
the manip-movies fixes are relevant. Keep this script free of anything
specific to the manip-movies pack (CANONON/LOSLAKE1, LAST4_3->GOLD7_2,
etc.) — those live in build_playtest_bin.py / build_manip_movies_test_bin.py.

Always writes:
  workspace/iso-extract/ff7_d1_singledisc_core.bin

  python3 mods/single-disc/scripts/build_singledisc_core_bin.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_layer import apply_layer  # noqa: E402


def main() -> int:
    pristine = ROOT / "workspace/pristine/FINALFANTASY7_D1.bin"
    csr_layer = ROOT.parent / "Final-Fantasy-7-CSR/builder/csr-v0.14.2/layers/disc1.layer.json"
    if not csr_layer.is_file():
        csr_layer = ROOT / "../Final-Fantasy-7-CSR/builder/csr-v0.14.2/layers/disc1.layer.json"
    csr_layer = csr_layer.resolve()
    core_layer = ROOT / "builder/single-disc-on-csr/layers/disc1.layer.json"
    out_dir = ROOT / "workspace/iso-extract"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_bin = out_dir / "ff7_d1_singledisc_core.bin"

    for p, label in [
        (pristine, "pristine D1"),
        (csr_layer, "CSR layer"),
        (core_layer, "single-disc-on-csr layer"),
    ]:
        if not p.is_file():
            print("MISSING", label, p, file=sys.stderr)
            return 1
        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.stat().st_mtime))
        print(f"USING [{label}] {p}  (mtime {mtime})")

    print("1/2 CSR base...")
    img = bytearray(pristine.read_bytes())
    apply_layer(img, json.loads(csr_layer.read_text(encoding="utf-8")))
    print("   ", len(img), "bytes")

    print("2/2 single-disc-on-csr core layer...")
    apply_layer(img, json.loads(core_layer.read_text(encoding="utf-8")))
    print("   ", len(img), "bytes")

    out_bin.write_bytes(img)
    print("WROTE", out_bin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
