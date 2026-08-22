#!/usr/bin/env python3
"""Remove DSKCG operations from field files using proper opcode parsing.

This script properly parses FF7 field structure to identify and remove
DSKCG (Ask for disc) operations without corrupting the field scripts.

Usage:
  python3 mods/single-disc/scripts/remove_dskcg.py \\
    --bin workspace/iso-extract/work.bin \\
    --field BLACKBGB \\
    --in-place
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from field_dat import OPCODE_NAMES, load_field_dat, op_size  # noqa: E402
from field_dat_write import write_field_dat  # noqa: E402
from psx_mode2_iso import extract_file, replace_file_within_sectors  # noqa: E402

# (byte offset of the jump field within the opcode's raw bytes, field width in
# bytes, jumpShift, is_backward) -- verified against Makou Reactor's
# Opcode.h struct layouts and Opcode::jumpShift()/Opcode::jump().
JUMP_INFO: dict[str, tuple[int, int, int, bool]] = {
    "JMPF": (1, 1, 1, False),
    "JMPFL": (1, 2, 1, False),
    "JMPB": (1, 1, 0, True),
    "JMPBL": (1, 2, 0, True),
    "IFUB": (5, 1, 5, False),
    "IFUBL": (5, 2, 5, False),
    "IFSW": (7, 1, 7, False),
    "IFSWL": (7, 2, 7, False),
    "IFUW": (7, 1, 7, False),
    "IFUWL": (7, 2, 7, False),
    "IFKEY": (3, 1, 3, False),
    "IFKEYON": (3, 1, 3, False),
    "IFKEYOFF": (3, 1, 3, False),
    "IFPRTYQ": (2, 1, 2, False),
    "IFMEMBQ": (2, 1, 2, False),
}


def _read_jump_raw(raw: bytes, offset: int, width: int) -> int:
    return raw[offset] if width == 1 else int.from_bytes(raw[offset : offset + width], "little")


def _write_jump_raw(raw: bytearray, offset: int, width: int, value: int) -> None:
    if width == 1:
        raw[offset] = value
    else:
        raw[offset : offset + width] = value.to_bytes(width, "little")


def remove_dskcg_from_script(script_raw: bytes) -> tuple[bytes, int]:
    """Remove all DSKCG (0x0E) operations from a script slot, fixing up any
    JMPF/JMPFL/JMPB/JMPBL/IFxx jump targets whose relative byte offset would
    otherwise be broken by the deleted bytes.

    Deleting an opcode shifts the byte position of everything after it, so a
    jump instruction whose target lies past a removed DSKCG (or whose own
    position moved) must have its relative offset re-encoded -- otherwise it
    silently points at the wrong byte and Makou shows a raw "Forward N
    byte(s)"/"Back N byte(s)" instead of "Goto label X".

    Returns (new_script_bytes, dskcg_count_removed).
    """
    # Decode ops with their absolute start offset in the original script.
    ops: list[tuple[int, bytes, str]] = []
    pos = 0
    while pos < len(script_raw):
        op = script_raw[pos]
        sz = max(op_size(script_raw, pos), 1)
        raw = script_raw[pos : pos + sz]
        name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else f"OP{op:02X}"
        ops.append((pos, raw, name))
        pos += sz
    end = pos

    if not any(raw[0] == 0x0E for _, raw, _ in ops):
        return script_raw, 0

    # Debug/isolation mode (per user request): just strip DSKCG bytes,
    # do NOT recalculate any jump offsets. Jumps that pointed past a removed
    # DSKCG will be off by the removed bytes -- this is intentionally wrong
    # and only for isolating whether jump-fixup math itself was the bug.
    survivors: list[tuple[int, bytearray, str]] = []
    removed = 0
    for start, raw, name in ops:
        if raw[0] == 0x0E:  # DSKCG opcode
            removed += 1
            continue
        survivors.append((start, bytearray(raw), name))

    new_script = bytearray()
    for _, raw, _ in survivors:
        new_script.extend(raw)

    return bytes(new_script), removed


def remove_dskcg_from_field(field_raw: bytes, field_name: str) -> tuple[bytes, int]:
    """Remove all DSKCG operations from a field file.

    Returns (new_field_raw, total_dskcg_removed).
    """
    # Parse field structure
    field_dat = load_field_dat(field_raw, field_name)

    # Get all script slots
    total_removed = 0
    modified_scripts: dict[tuple[str, int], bytes] = {}

    for script in field_dat.scripts:
        new_raw, removed = remove_dskcg_from_script(script.raw)
        if removed > 0:
            total_removed += removed
            modified_scripts[(script.entity, script.slot)] = new_raw
            print(f"    {script.entity} slot {script.slot}: Removed {removed} DSKCG")

    if total_removed == 0:
        return field_raw, 0

    # Rebuild the field file (recomputes offset tables, AKAO pointers, header,
    # and recompresses to LZS) via the generic splicer.
    new_field_raw = write_field_dat(field_dat, modified_scripts)
    return new_field_raw, total_removed


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--bin", type=Path, required=True, help="ISO image path")
    ap.add_argument("--field", required=True, help="Field name (e.g., BLACKBGB)")
    ap.add_argument("--in-place", action="store_true", help="Modify bin in place")
    ap.add_argument("-o", "--output", type=Path, help="Output bin path")
    args = ap.parse_args()
    
    if not args.in_place and not args.output:
        ap.error("--in-place or --output required")
    
    # Load bin
    img = bytearray(args.bin.read_bytes())
    
    # Extract field
    field_path = f"FIELD/{args.field}.DAT"
    field_raw = extract_file(img, field_path)
    
    # Remove DSKCG
    print(f"Processing {args.field}...")
    try:
        new_field, removed = remove_dskcg_from_field(field_raw, args.field)
        print(f"  Total DSKCG removed: {removed}")
        
        if removed > 0:
            # Replace in ISO
            replace_file_within_sectors(img, field_path, new_field)
            
            # Save
            out_path = args.bin if args.in_place else args.output
            out_path.write_bytes(img)
            print(f"  Saved: {out_path}")
    except NotImplementedError as e:
        print(f"  ERROR: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
