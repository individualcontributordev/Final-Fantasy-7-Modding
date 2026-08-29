#!/usr/bin/env python3
"""Build CSR + single-disc core + manip-movies playtest .bin (and .cue).

Always writes:
  workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin

Fails unless JAIROFAL.MOV body == pristine D2 CANONON.MOV.

  python3 mods/single-disc/scripts/build_playtest_bin.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_layer import apply_layer  # noqa: E402
from psx_mode2_iso import extract_file, find_file  # noqa: E402


def main() -> int:
    pristine = ROOT / "workspace/pristine/FINALFANTASY7_D1.bin"
    d2 = ROOT / "workspace/pristine/FINALFANTASY7_D2.bin"
    csr_layer = ROOT.parent / "Final-Fantasy-7-CSR/builder/csr-v0.14.2/layers/disc1.layer.json"
    if not csr_layer.is_file():
        csr_layer = ROOT / "../Final-Fantasy-7-CSR/builder/csr-v0.14.2/layers/disc1.layer.json"
    csr_layer = csr_layer.resolve()
    core_layer = ROOT / "builder/single-disc-on-csr/layers/disc1.layer.json"
    # v0.1.5 is a DELTA pack: its stored diff is computed against v0.1.4's
    # output (766340400 bytes), not the core layer's output (748775664
    # bytes) -- see builder/manifest.json blurb ("applies after manip-movies
    # v0.1.4"). Both must be applied in order or v0.1.5's byte patches land
    # at the wrong offsets against undersized base content (confirmed
    # 2026-08-24: applying v0.1.5 alone left JAIROFAL == vanilla D1, not
    # CANONON, because v0.1.4's LBA-250450 alias never landed first).
    movie_layer_v4 = ROOT / "builder/single-disc-csr-manip-movies-v0.1.4/layers/disc1.layer.json"
    movie_layer_v5 = ROOT / "builder/single-disc-csr-manip-movies-v0.1.5/layers/disc1.layer.json"
    # v0.1.6 was originally FSHIP_12 ad/3 CANONHT1/CANONHT2/CANONH1P
    # repoint+grow (~16.6MB); that content was removed 2026-08-29 as
    # confirmed dead code (ad/3 is never REQ'd, never an autorun slot for
    # its detected entity type, and not a line-trigger slot either -- see
    # csr-manip-movie-whitelist.md's CANONHT "exclude-dead" entries). The
    # v0.1.6 slot was then reused for an unrelated real bug fix: MD8_5
    # (#731) dir/Main PMVIE id 53's LBA collision with OPENINGE.MOV's
    # EOF-appended block, which broke the 67->731 transition movie.
    movie_layer_v6 = ROOT / "builder/single-disc-csr-manip-movies-v0.1.6/layers/disc1.layer.json"
    out_dir = ROOT / "workspace/iso-extract"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_bin = out_dir / "ff7_d1_playtest_csr_sd_movies.bin"
    out_cue = out_dir / "ff7_d1_playtest_csr_sd_movies.cue"

    import time

    for p, label in [
        (pristine, "pristine D1"),
        (d2, "pristine D2"),
        (csr_layer, "CSR layer"),
        (core_layer, "single-disc main pack"),
        (movie_layer_v4, "manip-movies v0.1.4"),
        (movie_layer_v5, "manip-movies v0.1.5 (delta on v0.1.4)"),
        (movie_layer_v6, "manip-movies v0.1.6 (delta on v0.1.5: MD8_5 id53 fix)"),
    ]:
        if not p.is_file():
            print("MISSING", label, p, file=sys.stderr)
            return 1
        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.stat().st_mtime))
        print(f"USING [{label}] {p}  (mtime {mtime})")

    print("1/5 CSR base...")
    img = bytearray(pristine.read_bytes())
    apply_layer(img, json.loads(csr_layer.read_text(encoding="utf-8")))
    print("   ", len(img), "bytes")

    print("2/5 single-disc main pack...")
    apply_layer(img, json.loads(core_layer.read_text(encoding="utf-8")))
    print("   ", len(img), "bytes")
    j_core = extract_file(bytes(img), "MOVIE/JAIROFAL.MOV")
    van = extract_file(pristine.read_bytes(), "MOVIE/JAIROFAL.MOV")
    print("   JAIROFAL after main size", len(j_core), "(still D1-family until movies)")

    print("3/5 manip-movies v0.1.4 (seed + LBA 250450 alias)...")
    apply_layer(img, json.loads(movie_layer_v4.read_text(encoding="utf-8")))
    print("   ", len(img), "bytes")

    print("4/5 manip-movies v0.1.5 (delta: NRCRLB/NRCRL/PARASHOT/METEOFIX/METEOSKY)...")
    apply_layer(img, json.loads(movie_layer_v5.read_text(encoding="utf-8")))
    print("   ", len(img), "bytes")

    print("5/5 manip-movies v0.1.6 (delta: MD8_5 id53 -> fresh NRCRLB.MOV, fixes OPENINGE collision)...")
    apply_layer(img, json.loads(movie_layer_v6.read_text(encoding="utf-8")))
    print("   ", len(img), "bytes")

    j = extract_file(bytes(img), "MOVIE/JAIROFAL.MOV")
    c = extract_file(d2.read_bytes(), "MOVIE/CANONON.MOV")
    meta = find_file(bytes(img), "MOVIE/JAIROFAL.MOV")
    print("JAIROFAL ISO", meta)
    print("size", len(j), "CANONON", len(c), "vanilla_d1", len(van))
    print("==CANONON", j == c)
    print("==vanilla_jairofal", j == van)
    print("sha", hashlib.sha256(j).hexdigest()[:16], "canon", hashlib.sha256(c).hexdigest()[:16])
    if j != c:
        print("FAIL: movies layer did not install CANONON into JAIROFAL", file=sys.stderr)
        return 2

    # LOSLAKE1 CD path seeks ISO LBA 250450 (D2 CANONON); alias must match.
    from psx_mode2_iso import SECTOR  # noqa: E402

    raw0 = bytes(img[250450 * SECTOR : (250450 + 1) * SECTOR])
    d2meta = find_file(d2.read_bytes(), "MOVIE/CANONON.MOV")
    d2raw0 = d2.read_bytes()[d2meta.lba * SECTOR : (d2meta.lba + 1) * SECTOR]
    if raw0 != d2raw0:
        print("FAIL: LBA 250450 raw sector != D2 CANONON sector0 (need Form2 2352 copy)", file=sys.stderr)
        return 3
    if raw0[18] != 0x42:
        print("FAIL: LBA 250450 submode 0x%02x want Form2 0x42" % raw0[18], file=sys.stderr)
        return 3
    print("LBA250450 raw Form2 sector0 == D2 CANONON OK")


    out_bin.write_bytes(img)
    out_cue.write_text(
        'FILE "%s" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' % out_bin.name,
        encoding="utf-8",
    )
    print("WROTE", out_bin)
    print("WROTE", out_cue)
    print("Open the .cue in DuckStation.")
    print("Do NOT open other ff7_d1_*_work.bin files in iso-extract (many are core-only ~714MB).")
    print("actual", out_bin.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
