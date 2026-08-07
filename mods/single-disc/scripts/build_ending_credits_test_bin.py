#!/usr/bin/env python3
"""Build CD-sized single-disc image: ending streams + LOSLAKE1 CANONON.

Stack (fields untouched after manip-movies):
  CSR D1 + single-disc core + manip-movies 0.1.2
  + D3 ending streams at Disc 3 absolute LBAs
  + Form2 CANONON punch at ISO LBA 250450 (LOSLAKE1)
  + LAST4_3 re-punch into GOLD7_2 (stomped by ENDING2E)

Does NOT replace LAS4_0/LASTMAP with pristine — CSR/SD Play skips stay.

ENDING2E spans 197242..277346 and includes 250450. After endings we rewrite
that mid-window with CANONON so the lake works; long credits may glitch there.
Image stays ~766340400 B (80-min CD).

  python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "mods/single-disc/scripts"))

from alias_d2_seek_lba_on_d1 import D2_CANONON_LBA  # noqa: E402
from psx_mode2_iso import SECTOR, USER, extract_file, find_file  # noqa: E402

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
    build = _ROOT / "mods/single-disc/scripts/build_playtest_bin.py"
    alias_end = _ROOT / "mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py"
    d2_path = _ROOT / "workspace/pristine/FINALFANTASY7_D2.bin"
    d3_path = _ROOT / "workspace/pristine/FINALFANTASY7_D3.bin"

    print("1/5 playtest stack (CSR + core + movies 0.1.2)...")
    r = subprocess.run([sys.executable, str(build)], cwd=str(_ROOT))
    if r.returncode:
        return r.returncode
    if not base_bin.is_file() or not d2_path.is_file() or not d3_path.is_file():
        print("missing playtest bin or pristine D2/D3", file=sys.stderr)
        return 1

    print("2/5 copy playtest -> ending bin (keep CSR/SD fields)...")
    shutil.copyfile(base_bin, out_bin)
    print(f"   {out_bin.name} = {base_bin.name} (no LAS4_0/LASTMAP overwrite)")

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
    c0 = d2[find_file(d2, "MOVIE/CANONON.MOV").lba * SECTOR :][:SECTOR]
    if img[D2_CANONON_LBA * SECTOR : (D2_CANONON_LBA + 1) * SECTOR] != c0:
        print("FAIL CANONON punch", file=sys.stderr)
        return 4
    print(f"   OK CANONON nsec={nsec} submode=0x{img[D2_CANONON_LBA * SECTOR + 18]:02x}")
    print(f"   NOTE: mid-ENDING2E LBA {D2_CANONON_LBA}..{D2_CANONON_LBA + nsec - 1} = CANONON")

    print("5/5 restore LAST4_3 -> GOLD7_2 (manip seed under ENDING2E)...")
    d3 = d3_path.read_bytes()
    from inject_movies_by_disc_id import (  # noqa: E402
        _movie_id_meta_by_lba,
        _patch_dirent_lba_size,
        _patch_movie_id_bin,
    )

    m3 = find_file(d3, "MOVIE/LAST4_3.BIN")
    gmeta = find_file(img, "MOVIE/GOLD7_2.MOV")
    nsec_g = (m3.size + USER - 1) // USER
    raw_g = d3[m3.lba * SECTOR : (m3.lba + nsec_g) * SECTOR]
    if m3.size > gmeta.size:
        print("GOLD7_2 slot too small for LAST4_3", file=sys.stderr)
        return 5
    off_g = gmeta.lba * SECTOR
    img[off_g : off_g + len(raw_g)] = raw_g
    _patch_dirent_lba_size(img, "MOVIE/GOLD7_2.MOV", gmeta.lba, m3.size)
    sm = _movie_id_meta_by_lba(d3, m3.lba)
    if sm:
        eng, a, b, c = sm
        _patch_movie_id_bin(img, gmeta.lba, gmeta.lba, eng, aux=(a, b, c))
    else:
        _patch_movie_id_bin(img, gmeta.lba, gmeta.lba, m3.size)
    out_bin.write_bytes(img)
    if extract_file(bytes(img), "MOVIE/GOLD7_2.MOV") != extract_file(d3, "MOVIE/LAST4_3.BIN"):
        print("FAIL LAST4_3 restore", file=sys.stderr)
        return 5
    print(f"   OK GOLD7_2 LBA={gmeta.lba} = LAST4_3 ({m3.size} bytes)")

    sz = out_bin.stat().st_size
    nsec_img = sz // SECTOR
    free = CD80_SECTORS - nsec_img
    print(f"CD budget size={sz} sectors={nsec_img} free80={free}")
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
    print("Fields: CSR/SD (ENDING01 still JMPF-skipped on LAS4_0). Streams at D3 LBAs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
