#!/usr/bin/env python3
"""Overwrite D1 MOVIE slots by per-disc sorted id (PMVIE index).

Field scripts use a disc-local movie id (sorted MOVIE/ name order). Copying a
D2/D3 file onto D1 by filename would land at the wrong id. This tool copies
source disc file for id N into D1 existing id N file. Shrinks the ISO size
field to the source length so builder layers stay small.

  python3 mods/single-disc/scripts/inject_movies_by_disc_id.py \
    --d1 workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin \
    --manifest mods/single-disc/patches/csr-manip-movie-seed.txt \
    --in-place
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))

from psx_mode2_iso import (  # noqa: E402
    USER,
    _list_dir,
    _u32_le,
    _user,
    _write_user,
    extract_file,
    find_file,
    replace_file_padded,
)

PRISTINE = {
    2: _ROOT / "workspace/pristine/FINALFANTASY7_D2.bin",
    3: _ROOT / "workspace/pristine/FINALFANTASY7_D3.bin",
}


def _movie_entries(img: bytes):
    pvd = _user(img, 16)
    root = pvd[156:190]
    for name, lba, size, is_dir in _list_dir(img, _u32_le(root, 2), _u32_le(root, 10)):
        if name != "MOVIE" or not is_dir:
            continue
        ents = []
        for n, lb, sz, d in _list_dir(img, lba, size):
            if n in (".", "..") or d:
                continue
            ents.append((n, lb, sz))
        return sorted(ents, key=lambda x: x[0].upper())
    raise FileNotFoundError("MOVIE/")


def _id_for_name(entries, name: str) -> int:
    u = name.upper()
    for i, (n, _l, _s) in enumerate(entries):
        if n.upper() == u:
            return i
    raise KeyError(name)


def _find_dirent(img: bytes, path: str):
    parts = [p for p in path.replace("\\", "/").upper().split("/") if p]
    pvd = _user(img, 16)
    root = pvd[156:190]
    dir_lba = _u32_le(root, 2)
    dir_size = _u32_le(root, 10)
    for idx, part in enumerate(parts):
        data = bytearray()
        remaining = dir_size
        sector = dir_lba
        while remaining > 0:
            take = min(USER, remaining)
            data.extend(_user(img, sector)[:take])
            remaining -= take
            sector += 1
        pos = 0
        found = None
        while pos < len(data):
            rlen = data[pos]
            if rlen == 0:
                pos = ((pos // USER) + 1) * USER
                continue
            name_len = data[pos + 32]
            flags = data[pos + 25]
            raw = bytes(data[pos + 33 : pos + 33 + name_len])
            if b";" in raw:
                raw = raw.split(b";")[0]
            try:
                sname = raw.decode("ascii")
            except Exception:
                sname = ""
            is_dir = bool(flags & 2)
            flba = _u32_le(bytes(data[pos : pos + rlen]), 2)
            fsize = _u32_le(bytes(data[pos : pos + rlen]), 10)
            if sname.upper() == part and idx == len(parts) - 1 and not is_dir:
                found = (dir_lba, dir_size, pos, bytes(data))
                break
            if sname.upper() == part and is_dir:
                dir_lba, dir_size = flba, fsize
                break
            pos += rlen
        else:
            if found is None and idx < len(parts) - 1:
                raise FileNotFoundError(path)
        if idx == len(parts) - 1:
            if found is None:
                raise FileNotFoundError(path)
            return found
    raise FileNotFoundError(path)


def _set_file_size(img: bytearray, path: str, new_size: int) -> None:
    dir_lba, dir_size, pos, _ = _find_dirent(bytes(img), path)
    meta = find_file(img, path)
    old_sec = (meta.size + USER - 1) // USER
    new_sec = (new_size + USER - 1) // USER
    if new_sec > old_sec:
        raise ValueError("%s needs more sectors" % path)
    remaining = dir_size
    sector = dir_lba
    data = bytearray()
    secs = []
    while remaining > 0:
        take = min(USER, remaining)
        secs.append(sector)
        data.extend(_user(img, sector)[:take])
        remaining -= take
        sector += 1
    struct.pack_into("<I", data, pos + 10, new_size)
    struct.pack_into(">I", data, pos + 14, new_size)
    off = 0
    rem = dir_size
    for s in secs:
        take = min(USER, rem)
        chunk = bytes(data[off : off + take])
        if take < USER:
            user = bytearray(_user(img, s))
            user[:take] = chunk
            _write_user(img, s, bytes(user))
        else:
            _write_user(img, s, chunk)
        off += take
        rem -= take
    if find_file(img, path).size != new_size:
        raise RuntimeError("size patch failed for %s" % path)


def inject_one(d1: bytearray, src_img: bytes, movie: str, src_disc: int) -> dict:
    src_ents = _movie_entries(src_img)
    d1_ents = _movie_entries(bytes(d1))
    mid = _id_for_name(src_ents, movie)
    if mid >= len(d1_ents):
        raise SystemExit(
            "%s id %d on D%d but D1 only has %d movies"
            % (movie, mid, src_disc, len(d1_ents))
        )
    src_name, _slba, src_size = src_ents[mid]
    d1_name, _dlba, d1_size = d1_ents[mid]
    data = extract_file(src_img, "MOVIE/" + src_name)
    if len(data) != src_size:
        raise RuntimeError("extract size mismatch")
    if len(data) > d1_size:
        raise SystemExit(
            "%s (%d bytes) does not fit D1 id %d slot %s (%d bytes)"
            % (movie, len(data), mid, d1_name, d1_size)
        )
    path = "MOVIE/" + d1_name
    if len(data) != d1_size:
        _set_file_size(d1, path, len(data))
    replace_file_padded(d1, path, data)
    return {
        "movie": movie.upper(),
        "src_disc": src_disc,
        "id": mid,
        "d1_slot": d1_name,
        "src_bytes": len(data),
        "old_slot_bytes": d1_size,
    }


def parse_manifest(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) == 1:
            rows.append((None, parts[0]))
        elif len(parts) >= 2 and parts[0] in ("2", "3", "D2", "D3"):
            d = 2 if str(parts[0]).endswith("2") else 3
            rows.append((d, parts[1]))
        else:
            raise SystemExit("bad manifest line: %r" % line)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--d1", type=Path, required=True)
    ap.add_argument("--from-disc", type=int, choices=(2, 3))
    ap.add_argument("--movie", action="append", default=[])
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--d2", type=Path, default=PRISTINE[2])
    ap.add_argument("--d3", type=Path, default=PRISTINE[3])
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    jobs = []
    for m in args.movie:
        if not args.from_disc:
            raise SystemExit("--from-disc required with --movie")
        jobs.append((args.from_disc, m))
    if args.manifest:
        for d, m in parse_manifest(args.manifest):
            if d is None:
                if not args.from_disc:
                    raise SystemExit("manifest line without disc needs --from-disc")
                d = args.from_disc
            jobs.append((d, m))
    if not jobs:
        raise SystemExit("provide --movie and/or --manifest")

    if not args.d1.is_file():
        raise SystemExit("missing d1: %s" % args.d1)
    d1 = bytearray(args.d1.read_bytes())
    cache = {}
    for disc, movie in jobs:
        if disc not in cache:
            src_path = args.d2 if disc == 2 else args.d3
            if not src_path.is_file():
                raise SystemExit("missing D%d: %s" % (disc, src_path))
            cache[disc] = src_path.read_bytes()
        info = inject_one(d1, cache[disc], movie, disc)
        print(
            "OK id=%d %s <- D%d %s (%d bytes; was %d)"
            % (
                info["id"],
                info["d1_slot"],
                info["src_disc"],
                info["movie"],
                info["src_bytes"],
                info["old_slot_bytes"],
            )
        )

    out = args.d1 if args.in_place else args.output
    if out is None:
        raise SystemExit("pass --in-place or -o")
    out.write_bytes(bytes(d1))
    print("wrote %s (%d bytes)" % (out, len(d1)))
    print("injected %d movie(s)" % len(jobs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
