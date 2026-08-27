#!/usr/bin/env python3
"""Diff ISO9660 directory metadata (LBA/size) between two disc images.

Purpose: find structural differences (wrong LBA, wrong size, wrong PVD
volume-space-size) introduced by the single-disc merge, as opposed to
content differences inside file bodies (which we've already ruled out for
JUNAIR.DAT specifically).

Usage:
  python3 scripts/diff_iso_metadata.py <good.bin> <bad.bin> [--only PREFIX]

Prints:
  - PVD volume space size (total LBA count) for both images.
  - Any path present in one image but not the other.
  - Any path whose LBA or size differs, with byte deltas.
  - Sorted by absolute size delta (most suspicious first).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from psx_mode2_iso import SECTOR, pvd_volume_space_size, walk_tree  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("good", type=Path, help="known-working image (e.g. stock CSR D2)")
    ap.add_argument("bad", type=Path, help="failing image (single-disc merge)")
    ap.add_argument("--only", default=None, help="only show paths starting with this prefix")
    args = ap.parse_args()

    good = args.good.read_bytes()
    bad = args.bad.read_bytes()

    print(f"good: {args.good}  ({len(good)} bytes, {len(good)//SECTOR} sectors)")
    print(f"bad : {args.bad}  ({len(bad)} bytes, {len(bad)//SECTOR} sectors)")

    good_vss = pvd_volume_space_size(good)
    bad_vss = pvd_volume_space_size(bad)
    print(f"PVD volume_space_size: good={good_vss} bad={bad_vss} delta={bad_vss - good_vss}")
    if good_vss != len(good) // SECTOR:
        print(f"  NOTE: good PVD size ({good_vss}) != actual sector count ({len(good)//SECTOR})")
    if bad_vss != len(bad) // SECTOR:
        print(f"  WARNING: bad PVD size ({bad_vss}) != actual sector count ({len(bad)//SECTOR})")
    print()

    print("Walking good tree...")
    good_tree = walk_tree(good)
    print(f"  {len(good_tree)} entries")
    print("Walking bad tree...")
    bad_tree = walk_tree(bad)
    print(f"  {len(bad_tree)} entries")
    print()

    if args.only:
        prefix = args.only.upper()
        good_tree = {k: v for k, v in good_tree.items() if k.upper().startswith(prefix)}
        bad_tree = {k: v for k, v in bad_tree.items() if k.upper().startswith(prefix)}

    only_good = sorted(set(good_tree) - set(bad_tree))
    only_bad = sorted(set(bad_tree) - set(good_tree))
    common = sorted(set(good_tree) & set(bad_tree))

    if only_good:
        print(f"=== {len(only_good)} paths only in GOOD ===")
        for p in only_good[:50]:
            print(f"  - {p}  {good_tree[p]}")
        if len(only_good) > 50:
            print(f"  ... and {len(only_good) - 50} more")
        print()

    if only_bad:
        print(f"=== {len(only_bad)} paths only in BAD ===")
        for p in only_bad[:50]:
            print(f"  + {p}  {bad_tree[p]}")
        if len(only_bad) > 50:
            print(f"  ... and {len(only_bad) - 50} more")
        print()

    diffs = []
    for p in common:
        g, b = good_tree[p], bad_tree[p]
        if g.size != b.size or g.lba != b.lba:
            diffs.append((p, g, b, abs(b.size - g.size)))

    diffs.sort(key=lambda t: -t[3])
    print(f"=== {len(diffs)} paths with differing LBA/size (common to both) ===")
    for p, g, b, _ in diffs[:200]:
        size_delta = b.size - g.size
        lba_delta = b.lba - g.lba
        print(
            f"  {p}\n"
            f"    good: lba={g.lba:8d} size={g.size:10d}\n"
            f"    bad : lba={b.lba:8d} size={b.size:10d}  "
            f"(lba_delta={lba_delta:+d}, size_delta={size_delta:+d})"
        )
    if len(diffs) > 200:
        print(f"  ... and {len(diffs) - 200} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
