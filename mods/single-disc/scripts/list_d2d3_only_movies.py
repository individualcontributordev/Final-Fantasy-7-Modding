#!/usr/bin/env python3
"""List D2/D3-only MOVIE files vs D1; check names; sum whitelist includes.

  python3 mods/single-disc/scripts/list_d2d3_only_movies.py
  python3 mods/single-disc/scripts/list_d2d3_only_movies.py --check LASTFLOR.MOV
  python3 mods/single-disc/scripts/list_d2d3_only_movies.py --sum-whitelist
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))

from psx_mode2_iso import _list_dir, _u32_le, _user  # noqa: E402

SECTOR = 2352
USER = 2048
CAP_80 = 80 * 60 * 75 * SECTOR


def _movies(img: bytes):
    pvd = _user(img, 16)
    root = pvd[156:190]
    for name, lba, size, is_dir in _list_dir(img, _u32_le(root, 2), _u32_le(root, 10)):
        if name != "MOVIE" or not is_dir:
            continue
        out = {}
        for n, _l, sz, d in _list_dir(img, lba, size):
            if n in (".", "..") or d:
                continue
            out[n.upper()] = sz
        return out
    return {}


def _mb(n: int) -> float:
    return n / (1024 * 1024)


def _raw_bytes(user_bytes: int) -> int:
    nsec = (user_bytes + USER - 1) // USER
    return nsec * SECTOR


def _load_pristine():
    d1p = _ROOT / "workspace/pristine/FINALFANTASY7_D1.bin"
    d2p = _ROOT / "workspace/pristine/FINALFANTASY7_D2.bin"
    d3p = _ROOT / "workspace/pristine/FINALFANTASY7_D3.bin"
    for p in (d1p, d2p, d3p):
        if not p.is_file():
            raise SystemExit("missing %s" % p)
    d1 = d1p.read_bytes()
    m1 = _movies(d1)
    m2 = _movies(d2p.read_bytes())
    m3 = _movies(d3p.read_bytes())
    return m1, m2, m3, len(d1)


def _parse_whitelist(path: Path):
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        movie = cells[0]
        if not re.search(r"\.(MOV|STR|BIN|HTM)$", movie, re.I):
            continue
        status = ""
        for c in reversed(cells[1:]):
            cl = c.lower()
            if cl in ("seed", "candidate", "include", "deferred") or cl.startswith(
                "exclude"
            ):
                status = cl
                break
        if not status and len(cells) >= 6:
            status = cells[5].lower()
        rows.append((status, movie.upper()))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", metavar="NAME", help="Is this file D2/D3-only vs D1?")
    ap.add_argument(
        "--sum-whitelist",
        action="store_true",
        help="Sum seed/candidate/include rows from csr-manip-movie-whitelist.md",
    )
    ap.add_argument(
        "--whitelist",
        type=Path,
        default=_ROOT / "mods/single-disc/patches/csr-manip-movie-whitelist.md",
    )
    args = ap.parse_args()

    m1, m2, m3, d1_len = _load_pristine()
    only2 = {k: v for k, v in m2.items() if k not in m1}
    only3 = {k: v for k, v in m3.items() if k not in m1}
    snova_raw = 570 * SECTOR
    free_after_snova = CAP_80 - (d1_len + snova_raw)

    if args.check:
        name = args.check.upper()
        if "." not in name:
            hits = [k for k in list(only2) + list(only3) if k.startswith(name)]
            if len(hits) == 1:
                name = hits[0]
            elif hits:
                print("ambiguous:", ", ".join(hits))
                return 1
        on1 = name in m1
        on2 = name in m2
        on3 = name in m3
        sz = m2.get(name) or m3.get(name) or m1.get(name) or 0
        print("%s" % name)
        print("  on D1: %s  D2: %s  D3: %s" % (on1, on2, on3))
        print(
            "  user MB: %.2f  approx raw MB: %.2f" % (_mb(sz), _mb(_raw_bytes(sz)))
        )
        if on1:
            print("  -> already on D1 (no copy needed for presence)")
        elif on2 or on3:
            print("  -> D2/D3-only: whitelist candidate if CSR still Plays it")
        else:
            print("  -> not found on pristine MOVIE tables")
            return 1
        return 0

    if args.sum_whitelist:
        rows = _parse_whitelist(args.whitelist)
        if not rows:
            print("no movie rows parsed from %s" % args.whitelist)
            return 1
        want = ("seed", "candidate", "include")
        picked = [(st, m) for st, m in rows if st in want]
        print("whitelist rows counted (seed|candidate|include): %d" % len(picked))
        total_user = 0
        total_raw = 0
        missing = []
        for st, name in picked:
            sz = only2.get(name) or only3.get(name) or m1.get(name)
            if sz is None:
                missing.append(name)
                print("  %-10s %-16s  NOT FOUND" % (st, name))
                continue
            disc = "D2" if name in only2 else ("D3" if name in only3 else "D1")
            total_user += sz
            total_raw += _raw_bytes(sz)
            print(
                "  %-10s %-16s %s  user %6.2f MB  raw ~%6.2f MB"
                % (st, name, disc, _mb(sz), _mb(_raw_bytes(sz)))
            )
        print(
            "TOTAL user %.2f MB  approx raw %.2f MB"
            % (_mb(total_user), _mb(total_raw))
        )
        print(
            "Headroom after SNOVA (80-min, approx): %.2f MB raw"
            % _mb(free_after_snova)
        )
        print(
            "After these files (approx): %.2f MB raw free"
            % _mb(free_after_snova - total_raw)
        )
        if missing:
            print("WARNING missing names:", ", ".join(missing))
            return 1
        if total_raw > free_after_snova:
            print("OVER BUDGET vs 80-min free-after-SNOVA estimate")
            return 2
        return 0

    print(
        "D1 movies: %d  D2-only: %d  D3-only: %d"
        % (len(m1), len(only2), len(only3))
    )
    print(
        "Pristine D1 raw: %.2f MB  free 80-min after +SNOVA ~%.2f MB raw"
        % (_mb(d1_len), _mb(free_after_snova))
    )
    print("\n=== D2-only (largest first) ===")
    for name, sz in sorted(only2.items(), key=lambda x: -x[1]):
        print(
            "  %7.2f MB user  ~%6.2f MB raw  %s"
            % (_mb(sz), _mb(_raw_bytes(sz)), name)
        )
    print("\n=== D3-only (largest first) ===")
    for name, sz in sorted(only3.items(), key=lambda x: -x[1]):
        print(
            "  %7.2f MB user  ~%6.2f MB raw  %s"
            % (_mb(sz), _mb(_raw_bytes(sz)), name)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
