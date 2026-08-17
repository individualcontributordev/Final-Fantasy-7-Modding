#!/usr/bin/env python3
"""Check LOST2 for the disc 2 break scene IFUW patch.

The fix changes IFUW else-jump from 0x0B → 0x00 so the MAPJUMP to cos_btm2
is always executed on single-disc builds (no disc flags to check).

Usage:
  python3 mods/single-disc/scripts/check_lost2_break_scene.py --bin path/to/image.bin
  python3 mods/single-disc/scripts/check_lost2_break_scene.py --from csr:2
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from disc_sources import field_iso_path, load_csr_image, load_pristine_image  # noqa: E402
from field_dat import decode_ops, load_field_dat  # noqa: E402
from psx_mode2_iso import extract_file  # noqa: E402


def check_lost2_ifuw(field_raw: bytes, label: str):
    """Check LOST2 for the IFUW break scene patch."""
    
    print(f"\n{'=' * 70}")
    print(f"LOST2 Break Scene Check: {label}")
    print(f"{'=' * 70}\n")
    
    lost2_dat = load_field_dat(field_raw, f"LOST2-{label}")
    
    # Search all scripts for IFUW operations
    ifuw_found = []
    for script in lost2_dat.scripts:
        ops = decode_ops(script.raw)
        for i, (raw_bytes, name) in enumerate(ops):
            if name == "IFUW":
                ifuw_found.append((script.entity, script.slot, i, raw_bytes, ops))

    print(f"Found {len(ifuw_found)} IFUW operations in LOST2\n")

    # Show ALL IFUW operations to find the break scene one
    for entity, slot, pos, raw_bytes, ops in ifuw_found:
        # IFUW: opcode 0x18 + 5-byte argument
        # byte[5] (index 5) is the else-jump offset
        if len(raw_bytes) >= 6:
            else_jump = raw_bytes[5]

            # Show ALL IFUW operations
            print(f"{entity} / Slot {slot}, opcode position {pos}:")
            print(f"  IFUW bytes: {raw_bytes.hex()}")
            print(f"  Else-jump: 0x{else_jump:02X}")

            # Show what comes after
            if pos + 1 < len(ops):
                next_raw, next_name = ops[pos + 1]
                print(f"  Next op: {next_name} {next_raw.hex()}")

                # Check if next is MAPJUMP to cos_btm2 (field 526 = 0x020e)
                if next_name == "MAPJUMP" and len(next_raw) >= 3:
                    field_id = next_raw[1] | (next_raw[2] << 8)
                    print(f"    → MAPJUMP to field {field_id} (0x{field_id:04X})")
                    if field_id == 526:
                        print(f"    → ✅ This is cos_btm2 (the break scene!)")

            # Interpret the fix
            if else_jump == 0x00:
                print(f"  ✅ FIXED: else-jump=0x00 means always execute next op")
                if pos + 1 < len(ops) and ops[pos + 1][1] == "MAPJUMP":
                    print(f"     → Single-disc will always MAPJUMP to break scene")
            elif else_jump == 0x0B:
                print(f"  ❌ BROKEN: else-jump=0x0B means skip 11 bytes")
                print(f"     → On single-disc, IFUW condition fails and skips MAPJUMP")
                print(f"     → NO BREAK SCENE AT START OF DISC 2!")

            print()


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--bin", type=Path, help="Disc image to check")
    ap.add_argument("--from", dest="source", 
                    help="pristine:N | csr:N (N=1,2,3)")
    args = ap.parse_args()
    
    if not args.bin and not args.source:
        ap.error("--bin or --from required")
    
    # Load image
    if args.bin:
        img = args.bin.read_bytes()
        label = args.bin.name
    elif args.source.startswith("pristine:"):
        disc = int(args.source.split(":")[1])
        img = load_pristine_image(disc)
        label = f"Pristine D{disc}"
    elif args.source.startswith("csr:"):
        disc = int(args.source.split(":")[1])
        img = load_csr_image(disc)
        label = f"CSR D{disc}"
    else:
        ap.error("--from must be pristine:N or csr:N")
    
    # Extract LOST2
    iso_path = field_iso_path("LOST2")
    try:
        lost2_raw = extract_file(img, iso_path)
        check_lost2_ifuw(lost2_raw, label)
    except FileNotFoundError:
        print(f"LOST2 not found in {label}")
        return 1
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
