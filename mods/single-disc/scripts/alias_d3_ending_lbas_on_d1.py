#!/usr/bin/env python3
"""Place Disc 3 ending streams at Disc 3 absolute LBAs on a D1 image.

Post-final-battle LAS4_0 seeks ENDING01 at MSF 36:23:33 = ISO LBA 163608
(the Disc 3 file start). Grown end-of-disc LBAs in MOVIE_ID alone are ignored
for this path (seek fails → black silence). Same class of fix as CANONON @250450.

Writes full MODE2/2352 sectors from pristine D3, retargets chosen D1 MOVIE/
dirents, and sets MINT/MOVIE_ID.BIN rows to Disc 3 LBA + size/aux.

  python3 mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py \\
    --d1 workspace/iso-extract/ff7_d1_playtest_ending_test.bin --in-place
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "mods/single-disc/scripts"))

from inject_movies_by_disc_id import _patch_dirent_lba_size  # noqa: E402
from psx_mode2_iso import (  # noqa: E402
    SECTOR,
    USER,
    extract_file,
    find_file,
    replace_file_padded,
)

# (MOVIE_ID row, D3 MOVIE name, D1 slot to retarget)
JOBS = (
    (23, "LASTMAP.BIN", "ONTRAIN.MOV"),
    (24, "LASTFLOR.MOV", "MAINPLR.MOV"),
    (25, "ENDING01.MOV", "SMK.STR"),
    (26, "ENDING3E.MOV", "SOUTHMK.MOV"),
    (29, "ENDING2E.MOV", "MONITOR.STR"),
)

PRISTINE_D3 = _ROOT / "workspace/pristine/FINALFANTASY7_D3.bin"


def _raw(src: bytes, lba: int, nsec: int) -> bytes:
    off = lba * SECTOR
    return src[off : off + nsec * SECTOR]


def _write_raw(img: bytearray, lba: int, raw: bytes) -> None:
    if len(raw) % SECTOR:
        raise ValueError("raw length not multiple of 2352")
    nsec = len(raw) // SECTOR
    need = (lba + nsec) * SECTOR
    if need > len(img):
        if len(img) % SECTOR:
            img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
        img.extend(b"\x00" * (need - len(img)))
    off = lba * SECTOR
    img[off : off + len(raw)] = raw


def apply(img: bytearray, d3: bytes) -> list[str]:
    blob3 = extract_file(d3, "MINT/MOVIE_ID.BIN")
    blob = bytearray(extract_file(img, "MINT/MOVIE_ID.BIN"))
    notes: list[str] = []
    for mid, d3name, d1name in JOBS:
        m3 = find_file(d3, f"MOVIE/{d3name}")
        nsec = (m3.size + USER - 1) // USER
        r3 = struct.unpack_from("<IIIII", blob3, mid * 20)
        d3_lba = m3.lba
        if r3[0] != d3_lba:
            notes.append(
                f"WARN id{mid}: MOVIE_ID LBA {r3[0]} != file {d3_lba}; using file"
            )
        raw = _raw(d3, d3_lba, nsec)
        _write_raw(img, d3_lba, raw)
        _patch_dirent_lba_size(img, f"MOVIE/{d1name}", d3_lba, m3.size)
        struct.pack_into(
            "<IIIII", blob, mid * 20, d3_lba, r3[1], r3[2], r3[3], r3[4]
        )
        notes.append(
            f"OK id{mid} {d3name} -> {d1name} LBA={d3_lba} nsec={nsec} eng={r3[1]}"
        )
    replace_file_padded(img, "MINT/MOVIE_ID.BIN", bytes(blob))
    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    return notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--d1", type=Path, required=True)
    ap.add_argument("--d3", type=Path, default=PRISTINE_D3)
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()
    if not args.d1.is_file():
        print("missing", args.d1, file=sys.stderr)
        return 1
    if not args.d3.is_file():
        print("missing", args.d3, file=sys.stderr)
        return 1
    img = bytearray(args.d1.read_bytes())
    d3 = args.d3.read_bytes()
    for line in apply(img, d3):
        print(line)
    out = args.d1 if args.in_place else args.output
    if out is None:
        print("pass --in-place or -o", file=sys.stderr)
        return 2
    out.write_bytes(img)
    print("wrote", out, len(img), "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
