#!/usr/bin/env python3
"""Compare field scripts between two disc images.

Extracts and compares FIELD/*.DAT scripts to identify differences at the script level,
not just raw bytes. Useful for debugging why two bins behave differently.

Usage:
    python3 scripts/compare_bins_field_scripts.py bin1.bin bin2.bin
    python3 scripts/compare_bins_field_scripts.py bin1.bin bin2.bin --field COS_BTM2
    python3 scripts/compare_bins_field_scripts.py bin1.bin bin2.bin --all-collisions
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from psx_mode2_iso import extract_file
from field_compare import compare_bytes, format_diff_report
from disc_sources import field_iso_path, normalize_field_name

# Critical fields for single-disc (disc 1→2 transition and break scene)
CRITICAL_FIELDS = ["COS_BTM2", "COS_BTM", "DEL1"]

# All collision maps (fields that exist on multiple discs)
COLLISION_MAPS = [
    "BLACKBGB", "BUGIN1A", "COS_BTM", "COS_BTM2", "DEL1",
    "JUNAIR2", "LOST2", "NIVGATE", "RCKTIN2", "RCKTIN7",
]


def compare_field(bin1_data: bytes, bin2_data: bytes, field_name: str) -> dict:
    """Compare a single field between two bins."""
    name = normalize_field_name(field_name)
    path = field_iso_path(name)
    
    try:
        dat1 = extract_file(bin1_data, path)
        dat2 = extract_file(bin2_data, path)
    except Exception as e:
        return {
            "field": field_name,
            "status": "ERROR",
            "error": str(e)
        }
    
    if dat1 == dat2:
        return {
            "field": field_name,
            "status": "IDENTICAL"
        }
    
    diff = compare_bytes(dat1, dat2, a_label=f"{field_name} (bin1)", b_label=f"{field_name} (bin2)")
    
    return {
        "field": field_name,
        "status": "DIFFERENT",
        "diff": diff
    }


def main():
    import argparse
    
    ap = argparse.ArgumentParser(description="Compare field scripts between two disc images")
    ap.add_argument("bin1", type=Path, help="First disc image")
    ap.add_argument("bin2", type=Path, help="Second disc image")
    ap.add_argument("--field", help="Specific field to compare (e.g., COS_BTM2)")
    ap.add_argument("--all-collisions", action="store_true", help="Compare all collision maps")
    ap.add_argument("--critical-only", action="store_true", help="Compare only critical fields for disc transition")
    ap.add_argument("-o", "--output", type=Path, help="Write diff report to file")
    
    args = ap.parse_args()
    
    if not args.bin1.exists():
        print(f"❌ Bin 1 not found: {args.bin1}")
        return 1
    
    if not args.bin2.exists():
        print(f"❌ Bin 2 not found: {args.bin2}")
        return 1
    
    print(f"=== Field Script Comparison ===\n")
    print(f"Bin 1: {args.bin1}")
    print(f"Bin 2: {args.bin2}\n")
    
    bin1_data = args.bin1.read_bytes()
    bin2_data = args.bin2.read_bytes()
    
    # Determine which fields to compare
    if args.field:
        fields = [args.field]
    elif args.all_collisions:
        fields = COLLISION_MAPS
    elif args.critical_only:
        fields = CRITICAL_FIELDS
    else:
        # Default: critical fields only
        fields = CRITICAL_FIELDS
    
    print(f"Comparing {len(fields)} field(s)...\n")
    
    results = []
    for field in fields:
        result = compare_field(bin1_data, bin2_data, field)
        results.append(result)
        
        if result["status"] == "IDENTICAL":
            print(f"✅ {result['field']:12} - IDENTICAL")
        elif result["status"] == "ERROR":
            print(f"❌ {result['field']:12} - ERROR: {result['error']}")
        else:
            print(f"⚠️  {result['field']:12} - DIFFERENT")
    
    # Show detailed diffs
    print("\n=== Detailed Differences ===\n")
    
    has_diffs = False
    for result in results:
        if result["status"] == "DIFFERENT":
            has_diffs = True
            print(f"Field: {result['field']}")
            print("-" * 60)
            report = format_diff_report(result['diff'])
            print(report)
            print()
    
    if not has_diffs:
        print("✅ No differences found in field scripts!")
    
    # Write to file if requested
    if args.output and has_diffs:
        with open(args.output, 'w') as f:
            for result in results:
                if result["status"] == "DIFFERENT":
                    f.write(f"# Field: {result['field']}\n\n")
                    f.write(format_diff_report(result['diff']))
                    f.write("\n\n")
        print(f"\n📝 Detailed diff written to: {args.output}")
    
    # Exit code
    return 0 if not has_diffs else 2


if __name__ == "__main__":
    sys.exit(main())
