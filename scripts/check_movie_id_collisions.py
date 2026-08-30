#!/usr/bin/env python3
"""Check a built .bin for MINT/MOVIE_ID.BIN LBA collisions.

Parses every row of MINT/MOVIE_ID.BIN (20-byte records: lba, engine_size,
auxA, auxB, auxC — see inject_movies_by_disc_id.py's _movie_id_meta_by_lba
docstring), resolves each id's occupied LBA range, and flags overlaps:

  1. Between two different movie ids (two PMVIE ids reading overlapping
     sectors — one will play the wrong / corrupted clip).
  2. Between a movie id's range and any other ISO9660 file's byte range,
     movie or non-movie (e.g. the MD8_5 id-53 bug: id 53 aliased onto
     OPENINGE.MOV's EOF-appended block — OPENINGE.MOV itself has no
     MOVIE_ID row, so this only ever surfaces as an id-vs-file overlap).

Two ranges starting at the SAME LBA with sector counts within 1.5x of each
other are treated as the same underlying file/id pairing, not a collision:
MOVIE_ID.BIN's engine size and the ISO9660 dirent size use different
sector-payload conventions (Form2 header/subheader overhead), so a
legitimate own-id/own-file pairing typically differs by ~10-20% in sector
count, never more. A stale collision — e.g. the MD8_5 id-53 bug, where id
53's row pointed at the exact start of OPENINGE.MOV's dirent but claimed
roughly half its sector span — shows up as an outsized (>1.5x) size
mismatch at an otherwise-matching start LBA. Any overlap where the start
LBAs *don't* match at all is always flagged (the engine would read into an
unrelated file's middle, which is unambiguously wrong).

This is the standing version of the ad-hoc check written for the id-53 fix
(ship_movie_relocation_v017_mid53.py) — run it against any built .bin to get
an automatic sanity net for future movie-relocation work.

Usage:
  python3 scripts/check_movie_id_collisions.py path/to/disc1.bin
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from psx_mode2_iso import USER, extract_file, walk_tree  # noqa: E402

ROW_SIZE = 20


def _movie_id_rows(img: bytes) -> list[tuple[int, int, int]]:
    """Return [(id, lba, nsec), ...] for every non-empty MOVIE_ID.BIN row.

    nsec is derived from engine size (usually sectors*2336, Form2); id 0 /
    lba 0 rows (unused slots) are skipped.
    """
    blob = extract_file(img, "MINT/MOVIE_ID.BIN")
    rows = []
    for i in range(len(blob) // ROW_SIZE):
        lba, eng_size = struct.unpack_from("<II", blob, i * ROW_SIZE)
        if lba == 0 and eng_size == 0:
            continue
        nsec = max(1, (eng_size + 2335) // 2336)
        rows.append((i, lba, nsec))
    return rows


SIZE_RATIO_LIMIT = 1.5  # same-start ranges within this ratio = same file/id


def _overlaps(lba1: int, ns1: int, lba2: int, ns2: int) -> bool:
    return lba1 < lba2 + ns2 and lba2 < lba1 + ns1


def _same_start_size_ok(lba1: int, ns1: int, lba2: int, ns2: int) -> bool:
    """True if ranges start together and sizes agree within SIZE_RATIO_LIMIT."""
    if lba1 != lba2:
        return False
    lo, hi = sorted((ns1, ns2))
    return hi <= lo * SIZE_RATIO_LIMIT


def check(img: bytes) -> list[str]:
    """Return a list of collision-description strings; empty = no collisions."""
    errors: list[str] = []

    movie_rows = _movie_id_rows(img)
    by_lba = sorted(movie_rows, key=lambda r: r[1])
    for a, b in zip(by_lba, by_lba[1:]):
        aid, albas, ans = a
        bid, blba, bns = b
        if _overlaps(albas, ans, blba, bns) and not _same_start_size_ok(albas, ans, blba, bns):
            errors.append(
                f"movie id {aid} (lba {albas}..{albas + ans - 1}) overlaps "
                f"movie id {bid} (lba {blba}..{blba + bns - 1}) with mismatched size"
            )

    # Cross-check against every known ISO9660 file's byte range (movie and
    # non-movie). A range starting at the same LBA with a sector count
    # within SIZE_RATIO_LIMIT is treated as the id's own file (Form2
    # header/rounding noise); anything else that overlaps is a bug.
    files = walk_tree(img)
    file_ranges = []
    for path, f in files.items():
        # MOVIE/ dirents are Form2 FMV streams: 2336 payload bytes/sector,
        # not the ISO9660-generic 2048 (see inject_movies_by_disc_id.py's
        # _movie_id_meta_by_lba docstring).
        divisor = 2336 if path.upper().lstrip("/").startswith("MOVIE/") else USER
        nsec = max(1, (f.size + divisor - 1) // divisor)
        file_ranges.append((path, f.lba, nsec))
    file_ranges.sort(key=lambda r: r[1])

    for mid, mlba, mns in movie_rows:
        for path, flba, fns in file_ranges:
            if _overlaps(mlba, mns, flba, fns) and not _same_start_size_ok(mlba, mns, flba, fns):
                errors.append(
                    f"movie id {mid} (lba {mlba}..{mlba + mns - 1}) collides "
                    f"with file {path} (lba {flba}..{flba + fns - 1})"
                )

    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(f"usage: {argv[0]} path/to/disc.bin", file=sys.stderr)
        return 2
    bin_path = Path(argv[1])
    if not bin_path.is_file():
        print(f"missing file: {bin_path}", file=sys.stderr)
        return 2
    img = bin_path.read_bytes()

    rows = _movie_id_rows(img)
    print(f"{bin_path}: {len(rows)} movie id(s) in MINT/MOVIE_ID.BIN")

    errors = check(img)
    if errors:
        print(f"COLLISIONS FOUND ({len(errors)}):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK: no LBA collisions between movie ids or against known files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
