#!/usr/bin/env python3
"""Bisect the single-disc-on-csr core layer by LOGICAL FILE, not raw byte
position. Groups the core layer's byte-diff records by which ISO file
(FIELD/*.DAT, SNOVA/*, BATTLE.X, etc.) they land in, using the merged
CSR+core image's own directory tree, then lets you build CSR + only a
chosen subset of files' edits.

Rationale: slicing by raw record index (offset order) can cut a single
file's compressed data or directory table mid-way, producing an internally
inconsistent build that could freeze for a DIFFERENT reason than the real
bug. Grouping by whole file keeps every applied file self-consistent.

A small number of records ("__GAP__", ISO9660 directory-table entries for
grown files) don't belong to any single file's data extent. These are
always included in every build (they're structural, not content, and tiny).

  python3 mods/single-disc/scripts/bisect_core_layer.py --list
      # show every logical file group and its record/byte counts

  python3 mods/single-disc/scripts/bisect_core_layer.py --files FIELD/BLACKBGB.DAT,SNOVA/SNOVA0.LZS
      # apply CSR + only those files' edits (+ always-on __GAP__ records)

  python3 mods/single-disc/scripts/bisect_core_layer.py --half 1
      # apply CSR + the first half of file groups (alphabetical), for bisection
  python3 mods/single-disc/scripts/bisect_core_layer.py --half 2
      # apply CSR + the second half of file groups

  python3 mods/single-disc/scripts/bisect_core_layer.py --none   # CSR only, baseline
  python3 mods/single-disc/scripts/bisect_core_layer.py --all    # full core layer

Writes workspace/iso-extract/bisect_core_<tag>.bin and a matching .cue.
"""
from __future__ import annotations

import argparse
import bisect
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_layer import apply_layer  # noqa: E402
from psx_mode2_iso import SECTOR, USER, _list_dir, _u32_le, _user  # noqa: E402

GAP_KEY = "__GAP__"


def _walk_tree(img, lba: int, size: int, path: str, out: list) -> None:
    for name, e_lba, e_size, is_dir in _list_dir(img, lba, size):
        full = f"{path}/{name}" if path else name
        out.append((full, e_lba, e_size, is_dir))
        if is_dir:
            _walk_tree(img, e_lba, e_size, full, out)


def group_records_by_file(img: bytearray, records: list[dict]) -> dict[str, list[dict]]:
    """Group layer records by the ISO file whose sector range contains them.

    `img` must already have every record applied (post-merge image), so
    files that only exist after the merge (e.g. grown SNOVA entries) are
    present in the directory tree.
    """
    pvd = _user(img, 16)
    root = pvd[156:190]
    root_lba = _u32_le(root, 2)
    root_size = _u32_le(root, 10)
    entries: list = [("[root]", root_lba, root_size, True)]
    _walk_tree(img, root_lba, root_size, "", entries)
    files = [e for e in entries if not e[3]]
    by_lba = sorted(((lba, name, size) for name, lba, size, _ in files), key=lambda t: t[0])
    lbas = [b[0] for b in by_lba]

    groups: dict[str, list[dict]] = {}
    for rec in records:
        lba = int(rec["offset"]) // SECTOR
        idx = bisect.bisect_right(lbas, lba) - 1
        key = GAP_KEY
        if idx >= 0:
            flba, fname, fsize = by_lba[idx]
            nsec = (fsize + USER - 1) // USER
            if lba < flba + nsec:
                key = fname
        groups.setdefault(key, []).append(rec)
    return groups


def _resolve_paths(root: Path):
    pristine = root / "workspace/pristine/FINALFANTASY7_D1.bin"
    csr_layer = root.parent / "Final-Fantasy-7-CSR/builder/csr-v0.14.2/layers/disc1.layer.json"
    if not csr_layer.is_file():
        csr_layer = root / "../Final-Fantasy-7-CSR/builder/csr-v0.14.2/layers/disc1.layer.json"
    csr_layer = csr_layer.resolve()
    core_layer_path = root / "builder/single-disc-on-csr/layers/disc1.layer.json"
    return pristine, csr_layer, core_layer_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list logical file groups and exit (no build)")
    ap.add_argument("--files", help="comma-separated list of file group keys to apply (see --list)")
    ap.add_argument("--half", type=int, choices=(1, 2), help="apply the first (1) or second (2) half of file groups, alphabetically")
    ap.add_argument("--none", action="store_true", help="CSR only, no core-layer files applied (baseline)")
    ap.add_argument("--all", action="store_true", help="apply every file group (equivalent to the full core build)")
    args = ap.parse_args()

    pristine, csr_layer, core_layer_path = _resolve_paths(ROOT)
    out_dir = ROOT / "workspace/iso-extract"
    out_dir.mkdir(parents=True, exist_ok=True)

    for p, label in [(pristine, "pristine D1"), (csr_layer, "CSR layer"), (core_layer_path, "core layer")]:
        if not p.is_file():
            print("MISSING", label, p, file=sys.stderr)
            return 1

    core_layer = json.loads(core_layer_path.read_text(encoding="utf-8"))

    # Build the fully-merged image once, purely to walk its directory tree
    # for grouping (never written out for --list/--files/--half decisions).
    merged = bytearray(pristine.read_bytes())
    apply_layer(merged, json.loads(csr_layer.read_text(encoding="utf-8")))
    apply_layer(merged, core_layer)
    groups = group_records_by_file(merged, core_layer["records"])

    # __GAP__ (ISO9660 directory-table entries for grown files) always ships;
    # it's structural bookkeeping, not a toggle-able content unit.
    content_keys = sorted(k for k in groups if k != GAP_KEY)

    if args.list:
        total_bytes = sum(len(bytes.fromhex(r["hex"])) for recs in groups.values() for r in recs)
        print(f"{len(content_keys)} logical file groups (+ {GAP_KEY}, always included)")
        for key in content_keys:
            recs = groups[key]
            nbytes = sum(len(bytes.fromhex(r["hex"])) for r in recs)
            print(f"  {len(recs):5d} records  {nbytes:7d} bytes  {key}")
        gap_recs = groups.get(GAP_KEY, [])
        print(f"  {len(gap_recs):5d} records  (structural, always included)  {GAP_KEY}")
        print(f"total changed bytes across all groups: {total_bytes}")
        return 0

    if args.none:
        selected: list[str] = []
    elif args.all:
        selected = content_keys
    elif args.half is not None:
        mid = (len(content_keys) + 1) // 2
        selected = content_keys[:mid] if args.half == 1 else content_keys[mid:]
    elif args.files:
        wanted = [f.strip() for f in args.files.split(",") if f.strip()]
        unknown = [f for f in wanted if f not in groups]
        if unknown:
            print(f"unknown file group(s): {unknown}\nrun --list to see valid keys", file=sys.stderr)
            return 1
        selected = [f for f in wanted if f != GAP_KEY]
    else:
        print("pass one of --list / --files / --half / --none / --all", file=sys.stderr)
        return 1

    records: list[dict] = list(groups.get(GAP_KEY, []))
    for key in selected:
        records.extend(groups[key])

    mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(core_layer_path.stat().st_mtime))
    print(f"USING [core layer] {core_layer_path}  (mtime {mtime})")
    print(f"Applying {len(selected)}/{len(content_keys)} file groups + {GAP_KEY} ({len(records)} records total)")
    for key in selected:
        print(f"  + {key}")

    img = bytearray(pristine.read_bytes())
    apply_layer(img, json.loads(csr_layer.read_text(encoding="utf-8")))
    print("   after CSR:", len(img), "bytes")

    partial_layer = dict(core_layer)
    partial_layer["records"] = records
    apply_layer(img, partial_layer)
    print("   after partial core layer:", len(img), "bytes")

    if args.none:
        tag = "none"
    elif args.all:
        tag = "all"
    elif args.half is not None:
        tag = f"half{args.half}"
    else:
        tag = f"n{len(selected)}"
    stem = f"bisect_core_{tag}"
    out_bin = out_dir / f"{stem}.bin"
    out_cue = out_dir / f"{stem}.cue"
    out_bin.write_bytes(img)
    out_cue.write_text(f'FILE "{out_bin.name}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    print("WROTE", out_bin)
    print("WROTE", out_cue)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
