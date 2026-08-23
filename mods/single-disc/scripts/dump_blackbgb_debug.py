#!/usr/bin/env python3
"""Dump BLACKBGB init-slot-0 script + FIELD.BIN table entry from any .bin.

Use this to compare a manually-edited (Makou Reactor) .bin against an
auto-generated one. Run it against both and diff the output.

Usage:
  python3 mods/single-disc/scripts/dump_blackbgb_debug.py path/to/some.bin
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from field_dat import OPCODE_NAMES, load_field_dat, op_size  # noqa: E402
from psx_mode2_iso import extract_file, find_file  # noqa: E402


def dump_script(sr: bytes, label: str) -> None:
    print(f"--- {label} ({len(sr)} bytes) ---")
    pos = 0
    while pos < len(sr):
        op = sr[pos]
        sz = max(op_size(sr, pos), 1)
        name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else f"OP{op:02X}"
        print(f"{pos:4d} {name:12s} {sr[pos:pos+sz].hex()}")
        pos += sz
    print(f"total len {pos}")


def dump_field_bin_table_entry(img: bytes, field_lba: int, field_size: int) -> None:
    """FIELD.BIN begins with a table of (LBA, size) pairs, one per field file,
    in the same order as FIELD.BIN's own internal directory. Find the entry
    whose LBA matches BLACKBGB.DAT's ISO LBA and print it."""
    try:
        fmeta = find_file(bytearray(img), "FIELD/FIELD.BIN")
    except Exception as e:  # noqa: BLE001
        print(f"(could not locate FIELD.BIN to check table: {e})")
        return
    fb = extract_file(bytearray(img), "FIELD/FIELD.BIN")
    # Table format: repeated 8-byte (u32 LBA, u32 size) entries at start of
    # FIELD.BIN, count-prefixed. Just scan first N entries for a match on LBA
    # relative offset from FIELD.BIN's own LBA (BLACKBGB LBA - FIELD.BIN LBA).
    rel_lba = field_lba - fmeta.lba
    count = struct.unpack_from("<H", fb, 0)[0]
    print(f"FIELD.BIN table: {count} entries, looking for rel_lba={rel_lba}")
    base = 2
    for i in range(count):
        off = base + i * 8
        if off + 8 > len(fb):
            break
        lba, size = struct.unpack_from("<II", fb, off)
        if lba == rel_lba:
            print(f"  entry[{i}] @0x{off:x}: lba={lba} size={size} (dirent size={field_size})")
            if size != field_size:
                print("  *** MISMATCH: table size != ISO dirent size ***")
            return
    print("  (no matching table entry found by rel_lba scan)")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    bin_path = Path(sys.argv[1])
    img = bin_path.read_bytes()

    meta = find_file(bytearray(img), "FIELD/BLACKBGB.DAT")
    print(f"BLACKBGB.DAT: lba={meta.lba} size={meta.size}")
    field_raw = extract_file(bytearray(img), "FIELD/BLACKBGB.DAT")

    dump_field_bin_table_entry(img, meta.lba, meta.size)

    field_dat = load_field_dat(field_raw, "BLACKBGB")
    for script in field_dat.scripts:
        if script.entity == "init" and script.slot == 0:
            dump_script(script.raw, f"{bin_path.name}: init slot 0")
            break
    else:
        print("init slot 0 not found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
