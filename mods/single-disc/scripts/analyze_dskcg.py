#!/usr/bin/env python3
"""Analyze DSKCG operations in field files to understand exactly what needs removal.

This script identifies all DSKCG (Ask for disc) operations and their context,
showing exactly which scripts contain them and what surrounds them.

Usage:
  python3 mods/single-disc/scripts/analyze_dskcg.py \\
    --from csr:1 \\
    --fields BLACKBGB,BLACKBGE,BLACKBG3
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from disc_sources import field_iso_path, load_csr_image, load_pristine_image, normalize_field_name  # noqa: E402
from field_dat import decode_ops, load_field_dat  # noqa: E402
from psx_mode2_iso import extract_file  # noqa: E402


def analyze_field(field_raw: bytes, field_name: str, source_label: str):
    """Analyze a field file for DSKCG operations."""
    field_dat = load_field_dat(field_raw, field_name)
    
    print(f"\n{'=' * 70}")
    print(f"{field_name} ({source_label})")
    print(f"{'=' * 70}")
    
    total_dskcg = 0
    
    for script in field_dat.scripts:
        ops = decode_ops(script.raw)
        
        # Find DSKCG operations in this script
        dskcg_positions = []
        for i, (raw_bytes, name) in enumerate(ops):
            if raw_bytes[0] == 0x0E:  # DSKCG
                dskcg_positions.append(i)
        
        if not dskcg_positions:
            continue
        
        # Print script info
        print(f"\n{script.entity} / Slot {script.slot} ({len(ops)} opcodes)")
        print(f"  {len(dskcg_positions)} DSKCG operations found at positions: {dskcg_positions}")
        
        # Show context around each DSKCG
        for pos in dskcg_positions:
            total_dskcg += 1
            print(f"\n  DSKCG #{total_dskcg} at opcode position {pos}:")
            
            # Show context: 3 ops before, the DSKCG, 3 ops after
            start = max(0, pos - 3)
            end = min(len(ops), pos + 4)
            
            for i in range(start, end):
                raw_bytes, name = ops[i]
                marker = " >>> " if i == pos else "     "
                # For DSKCG, show the disc number argument
                if raw_bytes[0] == 0x0E and len(raw_bytes) >= 2:
                    disc_num = raw_bytes[1]
                    print(f"{marker}[{i:3d}] {name} (disc {disc_num}) {raw_bytes.hex()}")
                else:
                    print(f"{marker}[{i:3d}] {name} {raw_bytes.hex()}")
    
    print(f"\nTotal DSKCG in {field_name}: {total_dskcg}")
    return total_dskcg


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--from", dest="source", required=True,
                    help="pristine:N | csr:N (N=1,2,3)")
    ap.add_argument("--fields", required=True,
                    help="Comma-separated field names (e.g., BLACKBGB,BLACKBGE,BLACKBG3)")
    args = ap.parse_args()
    
    # Parse source
    if args.source.startswith("pristine:"):
        disc = int(args.source.split(":")[1])
        img = load_pristine_image(disc)
        label = f"Pristine D{disc}"
    elif args.source.startswith("csr:"):
        disc = int(args.source.split(":")[1])
        img = load_csr_image(disc)
        label = f"CSR D{disc}"
    else:
        ap.error("--from must be pristine:N or csr:N")
        return 1
    
    # Parse fields
    field_names = [f.strip() for f in args.fields.split(",")]
    
    grand_total = 0
    for field_name in field_names:
        norm_name = normalize_field_name(field_name)
        iso_path = field_iso_path(norm_name)
        try:
            field_raw = extract_file(img, iso_path)
            count = analyze_field(field_raw, norm_name, label)
            grand_total += count
        except FileNotFoundError:
            print(f"\nWARNING: {norm_name} not found in {label}")
    
    print(f"\n{'=' * 70}")
    print(f"GRAND TOTAL DSKCG: {grand_total}")
    print(f"{'=' * 70}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
