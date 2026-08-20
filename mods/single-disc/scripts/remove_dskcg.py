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

from field_dat import decode_ops, load_field_dat  # noqa: E402
from field_dat_write import write_field_dat  # noqa: E402
from psx_mode2_iso import extract_file, replace_file_within_sectors  # noqa: E402


def remove_dskcg_from_script(script_raw: bytes) -> tuple[bytes, int]:
    """Remove all DSKCG (0x0E) operations from a script slot.
    
    Returns (new_script_bytes, dskcg_count_removed).
    """
    ops = decode_ops(script_raw)
    removed = 0
    new_script = bytearray()
    
    for raw_bytes, name in ops:
        if raw_bytes[0] == 0x0E:  # DSKCG opcode
            removed += 1
            # Skip this operation entirely
            continue
        # Keep all other operations
        new_script.extend(raw_bytes)
    
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
