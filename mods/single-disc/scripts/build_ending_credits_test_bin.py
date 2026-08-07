#!/usr/bin/env python3
"""Build DuckStation ending-credits test bin (v6 — D3 absolute LBAs).

  python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))

from disc_sources import load_pristine_image  # noqa: E402
from psx_mode2_iso import extract_file, find_file, replace_file_padded  # noqa: E402


def main() -> int:
    out_dir = _ROOT / "workspace/iso-extract"
    out_dir.mkdir(parents=True, exist_ok=True)
    base_bin = out_dir / "ff7_d1_playtest_csr_sd_movies.bin"
    out_bin = out_dir / "ff7_d1_playtest_ending_test.bin"
    out_cue = out_dir / "ff7_d1_playtest_ending_test.cue"
    lastmap_patch = _ROOT / "mods/single-disc/patches/ending-lastmap-v5.DAT"
    build = _ROOT / "mods/single-disc/scripts/build_playtest_bin.py"
    alias = _ROOT / "mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py"

    print("1/4 playtest stack...")
    r = subprocess.run([sys.executable, str(build)], cwd=str(_ROOT))
    if r.returncode:
        return r.returncode
    if not base_bin.is_file() or not lastmap_patch.is_file():
        print("missing base or LASTMAP patch", file=sys.stderr)
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
            print(name, "too big", file=sys.stderr)
            return 2
        replace_file_padded(img, f"FIELD/{name}", data)
        print(f"   FIELD/{name}")
    out_bin.write_bytes(img)

    print("3/4 alias D3 ending LBAs (raw Form2 + MOVIE_ID)...")
    r = subprocess.run(
        [sys.executable, str(alias), "--d1", str(out_bin), "--in-place"],
        cwd=str(_ROOT),
    )
    if r.returncode:
        return r.returncode

    out_cue.write_text(
        'FILE "ff7_d1_playtest_ending_test.bin" BINARY\n'
        "  TRACK 01 MODE2/2352\n"
        "    INDEX 01 00:00:00\n",
        encoding="utf-8",
    )
    print("4/4 done", out_bin, out_bin.stat().st_size)
    print("Open", out_cue)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
