#!/usr/bin/env python3
"""Analyze the working v0.1.2 single-disc bin to understand what makes it correct.

This script compares a known-working single-disc build against:
- Pristine D1 (to see all changes)
- CSR D1/D2/D3 (to see which disc's changes are used)
- Current build attempts (to see what's missing)

Usage:
  python3 mods/single-disc/scripts/analyze_working_v012.py \\
    --bin path/to/csr-single-disc-v0.1.2-working.bin
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from disc_sources import field_iso_path, load_csr_image, load_pristine_image  # noqa: E402
from field_dat import load_field_dat  # noqa: E402
from psx_mode2_iso import extract_file  # noqa: E402


def analyze_field_against_sources(bin_path: Path, field_name: str):
    """Compare a field in the working bin against pristine and CSR D1/D2/D3."""
    
    print(f"\n{'=' * 70}")
    print(f"Analyzing {field_name}")
    print(f"{'=' * 70}")
    
    # Load working bin
    work_img = bin_path.read_bytes()
    iso_path = field_iso_path(field_name)
    
    try:
        work_field = extract_file(work_img, iso_path)
    except FileNotFoundError:
        print(f"  {field_name} not found in working bin")
        return
    
    work_dat = load_field_dat(work_field, f"{field_name}-work")
    
    # Load pristine D1
    pris_img = load_pristine_image(1)
    pris_field = extract_file(pris_img, iso_path)
    pris_dat = load_field_dat(pris_field, f"{field_name}-pristine")
    
    # Load CSR D1, D2, D3
    csr1_img = load_csr_image(1)
    csr1_field = extract_file(csr1_img, iso_path)
    csr1_dat = load_field_dat(csr1_field, f"{field_name}-csr-d1")
    
    try:
        csr2_img = load_csr_image(2)
        csr2_field = extract_file(csr2_img, iso_path)
        csr2_dat = load_field_dat(csr2_field, f"{field_name}-csr-d2")
    except FileNotFoundError:
        csr2_dat = None
    
    try:
        csr3_img = load_csr_image(3)
        csr3_field = extract_file(csr3_img, iso_path)
        csr3_dat = load_field_dat(csr3_field, f"{field_name}-csr-d3")
    except FileNotFoundError:
        csr3_dat = None
    
    # Compare
    print(f"\nSize comparison:")
    print(f"  Pristine D1:  {len(pris_field):,} bytes")
    print(f"  CSR D1:       {len(csr1_field):,} bytes")
    if csr2_dat:
        print(f"  CSR D2:       {len(csr2_field):,} bytes")
    if csr3_dat:
        print(f"  CSR D3:       {len(csr3_field):,} bytes")
    print(f"  Working v0.1.2: {len(work_field):,} bytes")
    
    # Check which source matches working
    print(f"\nExact match check:")
    if work_field == pris_field:
        print(f"  ✅ Working == Pristine D1 (no changes!)")
    elif work_field == csr1_field:
        print(f"  ✅ Working == CSR D1")
    elif csr2_dat and work_field == csr2_field:
        print(f"  ✅ Working == CSR D2")
    elif csr3_dat and work_field == csr3_field:
        print(f"  ✅ Working == CSR D3")
    else:
        print(f"  ⚠️  Working is a custom merge/modification")
        
        # Check script counts
        print(f"\nScript slot comparison:")
        print(f"  Pristine D1:  {len(pris_dat.scripts)} slots")
        print(f"  CSR D1:       {len(csr1_dat.scripts)} slots")
        if csr2_dat:
            print(f"  CSR D2:       {len(csr2_dat.scripts)} slots")
        print(f"  Working:      {len(work_dat.scripts)} slots")
        
        # Check for DSKCG
        print(f"\nDSKCG check (opcode 0x0E):")
        for dat, label in [(pris_dat, "Pristine"), (csr1_dat, "CSR D1"), (work_dat, "Working")]:
            dskcg_count = 0
            for script in dat.scripts:
                for raw, name in script.raw:
                    if len(raw) > 0 and raw[0] == 0x0E:
                        dskcg_count += 1
            print(f"  {label}: {dskcg_count} DSKCG operations")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--bin", type=Path, required=True,
                    help="Path to working v0.1.2 bin")
    ap.add_argument("--fields", default="BLACKBGB,LOST2,DEL1,BLACKBGE,BLACKBG3",
                    help="Comma-separated field names to analyze")
    args = ap.parse_args()
    
    if not args.bin.is_file():
        ap.error(f"Bin not found: {args.bin}")
    
    print(f"Analyzing working v0.1.2 bin: {args.bin}")
    print(f"Size: {args.bin.stat().st_size:,} bytes")
    
    fields = [f.strip() for f in args.fields.split(",")]
    for field in fields:
        try:
            analyze_field_against_sources(args.bin, field)
        except Exception as e:
            print(f"\nERROR analyzing {field}: {e}")
            import traceback
            traceback.print_exc()
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
