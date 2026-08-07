#!/usr/bin/env python3
"""Build CD-sized single-disc image: endings + LOSLAKE1 CANONON.

Stack: CSR + single-disc core + manip-movies 0.1.2 + LASTMAP/LAS4_0
  + D3 ending streams at Disc 3 LBAs
  + Form2 CANONON punch at ISO LBA 250450 (LOSLAKE1 required path)

ENDING2E spans 197242..277346 and includes 250450. After placing endings we
overwrite that mid-window with CANONON so LOSLAKE1 works. Credits may glitch
for ~7359 sectors mid-ENDING2E; start of ENDING2E and other endings stay
intact. Image stays ~766340400 B (fits 80-min CD).

  python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "mods/single-disc/scripts"))

from alias_d2_seek_lba_on_d1 import D2_CANONON_LBA  # noqa: E402
from disc_sources import load_pristine_image  # noqa: E402
from psx_mode2_iso import (  # noqa: E402
    SECTOR,
    USER,
    extract_file,
    find_file,
    replace_file_padded,
)

CD80_SECTORS = 360000


def _punch_canonon(img: bytearray, d2: bytes) -> int:
    """Write D2 CANONON raw 2352 sectors at LBA 250450 (no file relocate)."""
    meta = find_file(d2, "MOVIE/CANONON.MOV")
    nsec = (meta.size + USER - 1) // USER
    raw = d2[meta.lba * SECTOR : (meta.lba + nsec) * SECTOR]
    off = D2_CANONON_LBA * SECTOR
    if off + len(raw) > len(img):
        raise RuntimeError("image too small for CANONON alias")
    img[off : off + len(raw)] = raw
    if img[off : off + SECTOR] != raw[:SECTOR]:
        raise RuntimeError("CANONON sector0 verify failed")
    if img[off + 18] != raw[18]:
        raise RuntimeError("CANONON submode mismatch")
    return nsec


def main() -> int:
    out_dir = _ROOT / "workspace/iso-extract"
    out_dir.mkdir(parents=True, exist_ok=True)
    base_bin = out_dir / "ff7_d1_playtest_csr_sd_movies.bin"
    out_bin = out_dir / "ff7_d1_playtest_ending_test.bin"
    out_cue = out_dir / "ff7_d1_playtest_ending_test.cue"
    lastmap_patch = _ROOT / "mods/single-disc/patches/ending-lastmap-v5.DAT"
    build = _ROOT / "mods/single-disc/scripts/build_playtest_bin.py"
    alias_end = _ROOT / "mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py"
    d2_path = _ROOT / "workspace/pristine/FINALFANTASY7_D2.bin"

    print("1/5 playtest stack (CSR + core + movies 0.1.2)...")
    r = subprocess.run([sys.executable, str(build)], cwd=str(_ROOT))
    if r.returncode:
        return r.returncode
    if not base_bin.is_file() or not lastmap_patch.is_file() or not d2_path.is_file():
        print("missing base, LASTMAP patch, or D2 pristine", file=sys.stderr)
        return 1

    print("2/5 LASTMAP v5 + pristine LAS4_0...")
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

    print("3/5 D3 ending streams at Disc 3 absolute LBAs...")
    r = subprocess.run(
        [sys.executable, str(alias_end), "--d1", str(out_bin), "--in-place"],
        cwd=str(_ROOT),
    )
    if r.returncode:
        return r.returncode

    print("4/5 restore CANONON Form2 @ LBA 250450 (LOSLAKE1)...")
    img = bytearray(out_bin.read_bytes())
    d2 = d2_path.read_bytes()
    nsec = _punch_canonon(img, d2)
    out_bin.write_bytes(img)
    c0 = d2[find_file(d2, "MOVIE/CANONON.MOV").lba * SECTOR :][:SECTOR]
    if img[D2_CANONON_LBA * SECTOR : (D2_CANONON_LBA + 1) * SECTOR] != c0:
        print("FAIL CANONON punch", file=sys.stderr)
        return 4
    print(f"   OK CANONON nsec={nsec} submode=0x{img[D2_CANONON_LBA * SECTOR + 18]:02x}")
    print(f"   NOTE: mid-ENDING2E LBA {D2_CANONON_LBA}..{D2_CANONON_LBA + nsec - 1} = CANONON")

    sz = out_bin.stat().st_size
    nsec_img = sz // SECTOR
    free = CD80_SECTORS - nsec_img
    print("5/5 CD budget")
    print(f"   size {sz}  sectors {nsec_img}  free80={free}")
    if nsec_img > CD80_SECTORS:
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
