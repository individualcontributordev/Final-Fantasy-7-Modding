#!/usr/bin/env python3
"""Put D2 stream bytes at the absolute LBA D2 uses so D1 seeks hit the right FMV.

LOSLAKE1 CD logs (2026-08-05): both discs setloc MSF -> DS sector 250600
(= ISO LBA 250450). On D2 that is CANONON. On D1 MOVIE_ID[47] is correct
(JAIROFAL@318357 with CANONON bytes) but the player still seeks 250450, which
is mid-RCKTFAIL on D1.

Fix: write CANONON at LBA 250450. Relocate any D1 files that would be clobbered
(JAIROFLY after shrink/LASTMAP) to EOF and patch MOVIE_ID.
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "mods/single-disc/scripts"))

from inject_movies_by_disc_id import (  # noqa: E402
    _append_file_grow,
    _patch_movie_id_bin,
)
from psx_mode2_iso import (  # noqa: E402
    SECTOR,
    USER,
    USER_OFF,
    extract_file,
    find_file,
    _user,
    _write_user,
    _list_dir,
    _u32_le,
)

D2_CANONON_LBA = 250450  # DS Read sector 250600 - 150


def _movie_files(img: bytes):
    pvd = _user(img, 16)
    root = pvd[156:190]
    for n, lba, sz, d in _list_dir(img, _u32_le(root, 2), _u32_le(root, 10)):
        if n == "MOVIE" and d:
            return [
                (nn, lb, ss)
                for nn, lb, ss, dd in _list_dir(img, lba, sz)
                if nn not in (".", "..") and not dd
            ]
    raise FileNotFoundError("MOVIE/")


def _write_raw_at_lba(img: bytearray, lba: int, data: bytes) -> int:
    nsec = (len(data) + USER - 1) // USER
    need_end = (lba + nsec) * SECTOR
    if need_end > len(img):
        if len(img) % SECTOR:
            img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
        template = bytes(img[0:SECTOR])
        while len(img) < need_end:
            img.extend(template)
    for i in range(nsec):
        chunk = data[i * USER : (i + 1) * USER]
        if len(chunk) < USER:
            chunk = chunk + b"\x00" * (USER - len(chunk))
        _write_user(img, lba + i, chunk)
    return nsec


def apply_alias(img: bytearray, canonon: bytes) -> list[str]:
    notes = []
    nsec = (len(canonon) + USER - 1) // USER
    end = D2_CANONON_LBA + nsec - 1
    notes.append(
        "alias CANONON (%d bytes, %d sectors) at LBA %d..%d"
        % (len(canonon), nsec, D2_CANONON_LBA, end)
    )

    # Relocate movies whose ISO range overlaps the alias window.
    for name, lba, size in sorted(_movie_files(bytes(img)), key=lambda x: x[1]):
        file_end = lba + (size + USER - 1) // USER - 1
        if file_end < D2_CANONON_LBA or lba > end:
            continue
        if name.upper() == "RCKTFAIL.MOV":
            notes.append(
                "overlap RCKTFAIL LBA %d..%d (tail clobbered; CSR manip tradeoff)"
                % (lba, file_end)
            )
            continue
        path = "MOVIE/" + name
        body = extract_file(bytes(img), path)
        old = find_file(img, path)
        notes.append(
            "relocate %s LBA %d -> EOF (was size %d)" % (name, old.lba, old.size)
        )
        new_lba = _append_file_grow(img, path, body)
        n = _patch_movie_id_bin(img, old.lba, old.size, new_lba, len(body))
        notes.append("  new LBA %d MOVIE_ID patches %d" % (new_lba, n))

    _write_raw_at_lba(img, D2_CANONON_LBA, canonon)
    # Smoke: first sector payload matches
    if _user(img, D2_CANONON_LBA)[:16] != canonon[:16]:
        raise RuntimeError("alias write verify failed")
    return notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--d1", type=Path, required=True)
    ap.add_argument("--d2", type=Path, default=_ROOT / "workspace/pristine/FINALFANTASY7_D2.bin")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("-o", type=Path)
    args = ap.parse_args()
    d2p = args.d2
    if not d2p.is_file():
        d2p = _ROOT / "workspace/pristine/Final Fantasy VII (Disc 2).bin"
    img = bytearray(args.d1.read_bytes())
    canonon = extract_file(d2p.read_bytes(), "MOVIE/CANONON.MOV")
    for n in apply_alias(img, canonon):
        print(n)
    out = args.d1 if args.in_place else args.o
    if not out:
        raise SystemExit("pass --in-place or -o")
    out.write_bytes(img)
    print("wrote", out, len(img))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
