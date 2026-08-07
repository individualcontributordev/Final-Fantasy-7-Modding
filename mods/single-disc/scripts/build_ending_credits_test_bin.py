#!/usr/bin/env python3
"""Build CD-sized single-disc image with ending credits (D3 absolute LBAs).

Stack: CSR + single-disc core + manip-movies 0.1.2 + LASTMAP/LAS4_0 + D3
ending streams at Disc 3 LBAs (same layout as DuckStation-verified v6).

Output ~766340400 bytes (~731 MiB, ~325825 sectors) — fits typical 80-min
CD (~360000 sectors). Not a GitHub layer pack (delta ~200 MiB too large).

  python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
  # workspace/iso-extract/ff7_d1_playtest_ending_test.{bin,cue}
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "mods/single-disc/scripts"))

from disc_sources import load_pristine_image  # noqa: E402
from psx_mode2_iso import extract_file, find_file, replace_file_padded  # noqa: E402

# 80-min MODE2/2352 budget (same order as ImgBurn / blank CD-R)
CD80_SECTORS = 360000
SECTOR = 2352


def main() -> int:
    out_dir = _ROOT / "workspace/iso-extract"
    out_dir.mkdir(parents=True, exist_ok=True)
    base_bin = out_dir / "ff7_d1_playtest_csr_sd_movies.bin"
    out_bin = out_dir / "ff7_d1_playtest_ending_test.bin"
    out_cue = out_dir / "ff7_d1_playtest_ending_test.cue"
    lastmap_patch = _ROOT / "mods/single-disc/patches/ending-lastmap-v5.DAT"
    build = _ROOT / "mods/single-disc/scripts/build_playtest_bin.py"
    alias = _ROOT / "mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py"

    print("1/4 playtest stack (CSR + core + movies 0.1.2)...")
    r = subprocess.run([sys.executable, str(build)], cwd=str(_ROOT))
    if r.returncode:
        return r.returncode
    if not base_bin.is_file() or not lastmap_patch.is_file():
        print("missing base or ending-lastmap-v5.DAT", file=sys.stderr)
        return 1

    print("2/4 LASTMAP v5 + pristine LAS4_0...")
    img = bytearray(base_bin.read_bytes())
    d1p = bytes(load_pristine_image(1))
    las4 = extract_file(d1p, "FIELD/LAS4_0.DAT")
    for name, data in (
        ("LASTMAP.DAT", lastmap_patch.read_bytes()),
        ("LAS4_0.DAT", las4),
    ):
        meta = find_file(img, f"FIELD/{name}")
        if len(data) > meta.size:
            print(name, "too big for slot", file=sys.stderr)
            return 2
        replace_file_padded(img, f"FIELD/{name}", data)
        print(f"   FIELD/{name}")
    out_bin.write_bytes(img)

    print("3/4 D3 ending streams at Disc 3 absolute LBAs...")
    r = subprocess.run(
        [sys.executable, str(alias), "--d1", str(out_bin), "--in-place"],
        cwd=str(_ROOT),
    )
    if r.returncode:
        return r.returncode

    sz = out_bin.stat().st_size
    nsec = sz // SECTOR
    free = CD80_SECTORS - nsec
    print("4/4 CD budget check")
    print(f"   size {sz} bytes  sectors {nsec}  ({sz / 1024 / 1024:.1f} MiB)")
    print(f"   80-min free sectors {free} ({free * SECTOR / 1024 / 1024:.1f} MiB)")
    if nsec > CD80_SECTORS:
        print("FAIL: over 80-min sector budget", file=sys.stderr)
        return 3

    out_cue.write_text(
        'FILE "ff7_d1_playtest_ending_test.bin" BINARY\n'
        "  TRACK 01 MODE2/2352\n"
        "    INDEX 01 00:00:00\n",
        encoding="utf-8",
    )
    print("WROTE", out_bin)
    print("WROTE", out_cue)
    print("Burn MODE2/2352 (raw); ImgBurn / CDRWIN style from the .cue.")
    print("NOTE: ENDING2E continuum overwrites LBA 250450 (LOSLAKE1/CANONON alias).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
