#!/usr/bin/env python3
"""Build oversize DuckStation bin: endings + restored LASTMAP/LAS4_0 scripts.

Not for CD burn or builder packs. See docs/findings/2026-08-07-ending-credits-test-inject.md

  python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))

from apply_layer import apply_layer  # noqa: E402
from disc_sources import load_pristine_image  # noqa: E402
from psx_mode2_iso import extract_file, find_file, replace_file_padded  # noqa: E402


def main() -> int:
    out_dir = _ROOT / "workspace/iso-extract"
    out_dir.mkdir(parents=True, exist_ok=True)
    base_bin = out_dir / "ff7_d1_playtest_csr_sd_movies.bin"
    out_bin = out_dir / "ff7_d1_playtest_ending_test.bin"
    out_cue = out_dir / "ff7_d1_playtest_ending_test.cue"
    manifest = _ROOT / "mods/single-disc/patches/ending-credits-test-manifest.txt"
    inject = _ROOT / "mods/single-disc/scripts/inject_movies_by_disc_id.py"
    build = _ROOT / "mods/single-disc/scripts/build_playtest_bin.py"

    print("1/4 normal playtest stack...")
    r = subprocess.run([sys.executable, str(build)], cwd=str(_ROOT))
    if r.returncode != 0:
        return r.returncode
    if not base_bin.is_file():
        print("missing", base_bin, file=sys.stderr)
        return 1

    print("2/4 copy + restore pristine LASTMAP / LAS4_0...")
    img = bytearray(base_bin.read_bytes())
    d1p = bytes(load_pristine_image(1))
    for name in ("LASTMAP.DAT", "LAS4_0.DAT"):
        pris = extract_file(d1p, f"FIELD/{name}")
        meta = find_file(img, f"FIELD/{name}")
        if len(pris) > meta.size:
            print(f"{name} pris {len(pris)} > slot {meta.size}", file=sys.stderr)
            return 2
        replace_file_padded(img, f"FIELD/{name}", pris)
        print(f"   restored FIELD/{name} ({len(pris)} bytes)")
    out_bin.write_bytes(img)

    print("3/4 inject D3 ending streams (grow + MOVIE_ID)...")
    r = subprocess.run(
        [
            sys.executable,
            str(inject),
            "--d1",
            str(out_bin),
            "--manifest",
            str(manifest),
            "--in-place",
        ],
        cwd=str(_ROOT),
    )
    if r.returncode != 0:
        return r.returncode

    out_cue.write_text(
        'FILE "ff7_d1_playtest_ending_test.bin" BINARY\n'
        "  TRACK 01 MODE2/2352\n"
        "    INDEX 01 00:00:00\n",
        encoding="utf-8",
    )
    sz = out_bin.stat().st_size
    print("4/4 done")
    print("WROTE", out_bin, sz, "bytes")
    print("WROTE", out_cue)
    print("Open the ending_test .cue in DuckStation (oversize; not for burn).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
