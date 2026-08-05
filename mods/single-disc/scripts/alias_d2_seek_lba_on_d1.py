#!/usr/bin/env python3
"""Alias D2 FMV seek LBA onto D1 by copying raw MODE2/2352 sectors.

LOSLAKE1 seeks ISO LBA 250450 (DS sector 250600) on both discs. That is
CANONON on D2; mid-RCKTFAIL on stock D1. MOVIE_ID[47] inject is not used.

FMV is Mode2 Form2 (submode 0x42, 2324-byte payload). Writing only 2048-byte
ISO user data breaks the stream head/audio. This tool copies full 2352-byte
sectors from pristine D2 CANONON into D1 at LBA 250450.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "mods/single-disc/scripts"))

from inject_movies_by_disc_id import _patch_dirent_lba_size, _patch_movie_id_bin  # noqa: E402
from psx_mode2_iso import (  # noqa: E402
    SECTOR,
    USER,
    extract_file,
    find_file,
    _user,
    _list_dir,
    _u32_le,
)

D2_CANONON_LBA = 250450


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


def _raw_slice(img: bytes | bytearray, lba: int, nsec: int) -> bytes:
    off = lba * SECTOR
    return bytes(img[off : off + nsec * SECTOR])


def _append_raw_sectors(img: bytearray, raw: bytes) -> int:
    if len(raw) % SECTOR:
        raise ValueError("raw length not multiple of 2352")
    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    new_lba = len(img) // SECTOR
    img.extend(raw)
    return new_lba


def _write_raw_sectors(img: bytearray, dest_lba: int, raw: bytes) -> None:
    if len(raw) % SECTOR:
        raise ValueError("raw length not multiple of 2352")
    nsec = len(raw) // SECTOR
    need = (dest_lba + nsec) * SECTOR
    if need > len(img):
        if len(img) % SECTOR:
            img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
        img.extend(b"\x00" * (need - len(img)))
    off = dest_lba * SECTOR
    img[off : off + len(raw)] = raw


def apply_alias(img: bytearray, d2_img: bytes) -> list[str]:
    notes = []
    meta = find_file(d2_img, "MOVIE/CANONON.MOV")
    nsec = (meta.size + USER - 1) // USER
    end = D2_CANONON_LBA + nsec - 1
    raw = _raw_slice(d2_img, meta.lba, nsec)
    notes.append(
        "raw-copy CANONON %d sectors (%d bytes ISO) D2 LBA %d -> D1 LBA %d..%d"
        % (nsec, meta.size, meta.lba, D2_CANONON_LBA, end)
    )
    if raw[24:40] != extract_file(d2_img, "MOVIE/CANONON.MOV")[:16]:
        raise RuntimeError("D2 raw sector payload mismatch")

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
        old = find_file(img, path)
        file_nsec = (old.size + USER - 1) // USER
        body_raw = _raw_slice(img, old.lba, file_nsec)
        notes.append("relocate raw %s LBA %d (%d sec) -> EOF" % (name, old.lba, file_nsec))
        new_lba = _append_raw_sectors(img, body_raw)
        _patch_dirent_lba_size(img, path, new_lba, old.size)
        n = _patch_movie_id_bin(img, old.lba, old.size, new_lba, old.size)
        notes.append("  new LBA %d MOVIE_ID patches %d" % (new_lba, n))

    _write_raw_sectors(img, D2_CANONON_LBA, raw)
    got = bytes(img[D2_CANONON_LBA * SECTOR : (D2_CANONON_LBA + 1) * SECTOR])
    if got != raw[:SECTOR]:
        raise RuntimeError("alias raw write verify failed")
    submode = img[D2_CANONON_LBA * SECTOR + 18]
    if submode != raw[18]:
        raise RuntimeError("submode mismatch after write: %r vs %r" % (submode, raw[18]))
    notes.append("sector0 submode=0x%02x (Form2 expected 0x42)" % submode)
    return notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--d1", type=Path, required=True)
    ap.add_argument("--d2", type=Path, default=_ROOT / "workspace/pristine/FINALFANTASY7_D2.bin")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("-o", type=Path)
    args = ap.parse_args()
    d2p = args.d2 if args.d2.is_file() else _ROOT / "workspace/pristine/Final Fantasy VII (Disc 2).bin"
    img = bytearray(args.d1.read_bytes())
    d2_img = d2p.read_bytes()
    for n in apply_alias(img, d2_img):
        print(n)
    out = args.d1 if args.in_place else args.o
    if not out:
        raise SystemExit("pass --in-place or -o")
    out.write_bytes(img)
    print("wrote", out, len(img))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
