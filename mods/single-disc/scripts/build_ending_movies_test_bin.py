#!/usr/bin/env python3
"""Build CSR + single-disc core .bin + D3 ending streams ONLY.

Isolated ending-movie test: no manip-movies content (CANONON/LOSLAKE1,
LAST4_3->GOLD7_2, etc.) is included. This base (single-disc core, no
manip-movies) is also what "highwind" will use, so keep this script and
its output free of anything manip-movies-specific.

Stack:
  CSR D1 + single-disc-on-csr core (build_singledisc_core_bin.py)
  + D3 ending streams at Disc 3 absolute LBAs (alias_d3_ending_lbas_on_d1.py)

Does NOT replace LAS4_0/LASTMAP with pristine — CSR/SD Play skips stay.

  python3 mods/single-disc/scripts/build_ending_movies_test_bin.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "mods/single-disc/scripts"))

CD80_SECTORS = 360000


def main() -> int:
    from psx_mode2_iso import SECTOR  # noqa: E402

    out_dir = _ROOT / "workspace/iso-extract"
    out_dir.mkdir(parents=True, exist_ok=True)
    core_bin = out_dir / "ff7_d1_singledisc_core.bin"
    out_bin = out_dir / "ff7_d1_singledisc_endings_test.bin"
    out_cue = out_dir / "ff7_d1_singledisc_endings_test.cue"
    build_core = _ROOT / "mods/single-disc/scripts/build_singledisc_core_bin.py"
    alias_end = _ROOT / "mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py"
    d3_path = _ROOT / "workspace/pristine/FINALFANTASY7_D3.bin"

    print("1/2 single-disc core (CSR + single-disc-on-csr, no manip-movies)...")
    r = subprocess.run([sys.executable, str(build_core)], cwd=str(_ROOT))
    if r.returncode:
        return r.returncode
    if not core_bin.is_file() or not d3_path.is_file():
        print("missing core bin or pristine D3", file=sys.stderr)
        return 1

    print("2/2 D3 ending streams at Disc 3 absolute LBAs...")
    import shutil

    shutil.copyfile(core_bin, out_bin)
    r = subprocess.run(
        [sys.executable, str(alias_end), "--d1", str(out_bin), "--in-place"],
        cwd=str(_ROOT),
    )
    if r.returncode:
        return r.returncode

    sz = out_bin.stat().st_size
    nsec_img = sz // SECTOR
    free = CD80_SECTORS - nsec_img
    print(f"CD budget size={sz} sectors={nsec_img} free80={free}")
    if nsec_img > CD80_SECTORS:
        print("FAIL: over 80-min sector budget", file=sys.stderr)
        return 3

    out_cue.write_text(
        'FILE "%s" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'
        % out_bin.name,
        encoding="utf-8",
    )
    print("WROTE", out_bin)
    print("WROTE", out_cue)
    print("Fields: CSR/SD only (no manip-movies). Ending streams at D3 LBAs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
