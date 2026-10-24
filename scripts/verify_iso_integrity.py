#!/usr/bin/env python3
"""Check a raw FF7 BIN against the ISO layout constraints used by ff7tk.

The input is one MODE2/2352 image. The command recursively sorts ISO9660 files
and directories by LBA, then reports duplicate LBAs, overlaps, oversized
padding gaps, and a PVD/image-size mismatch. Movie extents use their Form 2
payload size. This is read-only diagnostics; it does not repair tables, layout,
or sector EDC/ECC."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from psx_mode2_iso import SECTOR, USER, _list_dir, _u32_le, _user  # noqa: E402


FORM2_USER = 2336  # CD-XA Form 2 (e.g. MOVIE/*.STR, *.MOV) -- not 2048-byte Form 1

# CSR+ packs the game onto Disc 1. The ending movie's LBAs are hardcoded, so it
# sits where Disc 3 had it and MONITOR.STR is aliased to it. That lands on the
# tail of NVLMK.MOV, a non-ending movie CSR+ does not preserve.
EXPECTED_OVERLAPS = {("MOVIE/NVLMK.MOV", "MOVIE/MONITOR.STR")}


def sector_count(size: int, name: str = "") -> int:
    """Extent length in sectors: Form 2 movies use 2336-byte payloads, else 2048."""
    upper = name.upper()
    if upper.startswith("MOVIE/") or upper.endswith((".STR", ".MOV")):
        return (size + FORM2_USER - 1) // FORM2_USER
    return (size + USER - 1) // USER


def walk_tree(img: bytes, lba: int, size: int, path: str, out: list[tuple[str, int, int, bool]]) -> None:
    """Append every ISO9660 file and subdirectory under this directory extent."""
    entries = _list_dir(img, lba, size)
    for name, e_lba, e_size, is_dir in entries:
        full = f"{path}/{name}" if path else name
        out.append((full, e_lba, e_size, is_dir))
        if is_dir:
            walk_tree(img, e_lba, e_size, full, out)


def tree_entries(img: bytes) -> list[tuple[str, int, int, bool]]:
    """Every ISO9660 file and directory as (path, lba, size, is_dir), root first."""
    root = _user(img, 16)[156:190]
    entries: list[tuple[str, int, int, bool]] = [("[root]", _u32_le(root, 2), _u32_le(root, 10), True)]
    walk_tree(img, entries[0][1], entries[0][2], "", entries)
    return entries


def big_gaps(img: bytes) -> list[tuple[str, str, int, int]]:
    """(prev, next, prev_end, gap) for every gap > 255 sectors between LBA-sorted entries."""
    out = []
    ordered = sorted(tree_entries(img), key=lambda t: t[1])
    for (p_name, p_lba, p_size, _), (name, lba, _s, _d) in zip(ordered, ordered[1:]):
        p_end = p_lba + sector_count(p_size, p_name)
        if lba - p_end > 255:
            out.append((p_name, name, p_end, lba - p_end))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bin_path", type=Path)
    ap.add_argument("--pristine", type=Path, help="Retail BIN of the same disc; gaps it also has are not reported")
    args = ap.parse_args()

    img = args.bin_path.read_bytes()
    if len(img) % SECTOR != 0:
        raise SystemExit(f"image size {len(img)} is not a multiple of {SECTOR}")

    pvd = _user(img, 16)
    if pvd[0] != 1 or pvd[1:6] != b"CD001":
        raise SystemExit("Primary Volume Descriptor not found at LBA 16")

    root = pvd[156:190]
    root_lba = _u32_le(root, 2)
    root_size = _u32_le(root, 10)
    volume_sectors = _u32_le(pvd, 80)

    entries: list[tuple[str, int, int, bool]] = [("[root]", root_lba, root_size, True)]
    walk_tree(img, root_lba, root_size, "", entries)

    print(f"Total entries (files+dirs): {len(entries)}")
    print(f"Volume space size (sectors): {volume_sectors}, image sectors: {len(img) // SECTOR}")
    if volume_sectors != len(img) // SECTOR:
        print("  WARNING: PVD volume_space_size does not match actual image sector count")

    by_lba: dict[int, list[tuple[str, int, int, bool]]] = {}
    for name, lba, size, is_dir in entries:
        by_lba.setdefault(lba, []).append((name, lba, size, is_dir))

    dup_count = 0
    for lba, group in sorted(by_lba.items()):
        if len(group) > 1:
            dup_count += 1
            print(f"\nDUPLICATE LBA {lba} ({len(group)} entries -- QMap collision in ff7tk, only last survives):")
            for name, _lba, size, is_dir in group:
                print(f"    {'DIR ' if is_dir else 'FILE'} {name}  size={size}  sectors={sector_count(size, name)}")

    ordered = sorted(entries, key=lambda t: t[1])
    overlap_count = 0
    prev = None
    print("\nScanning LBA-sorted layout for overlaps (this.lba + sectorCount > next.lba)...")
    for name, lba, size, is_dir in ordered:
        if prev is not None:
            p_name, p_lba, p_size, _ = prev
            p_end = p_lba + sector_count(p_size, p_name)
            gap = lba - p_end
            if gap < 0 and (p_name, name) in EXPECTED_OVERLAPS:
                print(f"  expected overlap: {p_name} / {name} by {-gap} sector(s)")
            elif gap < 0:
                overlap_count += 1
                print(
                    f"  OVERLAP: {p_name} @{p_lba} (+{sector_count(p_size, p_name)} sec, end={p_end}) "
                    f"overlaps {name} @{lba} by {-gap} sector(s)"
                )
        prev = (name, lba, size, is_dir)

    print(f"\nDuplicate-LBA groups: {dup_count}")
    print(f"Overlaps: {overlap_count}")

    # ff7tk casts the file->file gap to quint8 (IsoArchive.cpp:1333) when
    # computing paddingAfter -- any real gap > 255 sectors silently
    # truncates (gap % 256), corrupting the padding table it uses in pack().
    # Retail has these gaps, so with --pristine only gaps retail lacks are reported.
    print("\nScanning for gaps > 255 sectors (quint8 paddingAfter truncation in ff7tk)...")
    known = {g[:2] + g[3:] for g in big_gaps(args.pristine.read_bytes())} if args.pristine else set()
    gaps = [g for g in big_gaps(img) if g[:2] + g[3:] not in known]
    for p_name, name, p_end, gap in gaps:
        print(f"  warning: {'new ' if args.pristine else ''}BIG GAP: {p_name} ends {p_end}, {name} starts {p_end + gap} -- gap={gap} sectors (truncates to {gap % 256})")
    print(f"Gaps > 255 sectors{' not in pristine' if args.pristine else ''}: {len(gaps)}")

    # Files keep their disc LBAs when CSR packs discs together, so any file whose
    # directory entry differs from retail deserves a look.
    warnings = len(gaps)
    if args.pristine:
        print("\nComparing directory entries against pristine...")
        ref = {n: (l, sz) for n, l, sz, _ in tree_entries(args.pristine.read_bytes())}
        cur = {n: (l, sz) for n, l, sz, _ in tree_entries(img)}
        for n in sorted(ref.keys() | cur.keys(), key=lambda n: (cur.get(n) or ref[n])[0]):
            if n not in cur:
                print(f"  warning: REMOVED {n} (retail LBA {ref[n][0]})")
            elif n not in ref:
                print(f"  warning: ADDED {n} @{cur[n][0]} size={cur[n][1]}")
            elif cur[n] != ref[n]:
                print(f"  warning: CHANGED {n}: LBA {ref[n][0]} -> {cur[n][0]}, size {ref[n][1]} -> {cur[n][1]}")
            else:
                continue
            warnings += 1
        print(f"Entries differing from pristine: {warnings - len(gaps)}")

    if dup_count or overlap_count:
        return 1
    print(f"OK: no duplicate LBAs or unexpected overlaps. {warnings} warning(s) to review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
