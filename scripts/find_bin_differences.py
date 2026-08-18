#!/usr/bin/env python3
"""Find specific byte differences between two disc images.

Focuses on finding the root cause of runtime behavior differences.
Checks:
1. Byte-by-byte comparison with detailed diff map
2. SLUS executable comparison
3. Critical system files (SYSTEM.CNF, etc.)
4. First N sectors comparison (boot area)

Usage:
    python3 scripts/find_bin_differences.py bin1.bin bin2.bin
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from psx_mode2_iso import extract_file


def compare_bins(bin1_path: Path, bin2_path: Path):
    """Compare two bins and identify differences."""
    
    if not bin1_path.exists():
        print(f"❌ Bin 1 not found: {bin1_path}")
        return 1
    
    if not bin2_path.exists():
        print(f"❌ Bin 2 not found: {bin2_path}")
        return 1
    
    print(f"=== Comparing Disc Images ===\n")
    print(f"Bin 1: {bin1_path}")
    print(f"Bin 2: {bin2_path}\n")
    
    bin1_data = bin1_path.read_bytes()
    bin2_data = bin2_path.read_bytes()
    
    # Size check
    print(f"Size check:")
    print(f"  Bin 1: {len(bin1_data):,} bytes")
    print(f"  Bin 2: {len(bin2_data):,} bytes")
    
    if len(bin1_data) != len(bin2_data):
        print(f"  ❌ Different sizes!")
        return 2
    else:
        print(f"  ✅ Same size\n")
    
    # Byte-by-byte comparison
    print("Byte-by-byte comparison...")
    diffs = []
    for i in range(len(bin1_data)):
        if bin1_data[i] != bin2_data[i]:
            diffs.append(i)
    
    if not diffs:
        print("✅ PERFECT MATCH - Files are identical!\n")
        return 0
    
    print(f"❌ Found {len(diffs):,} different bytes\n")
    
    # Analyze difference distribution
    print("=== Difference Distribution ===\n")
    
    # Group differences by sector
    sector_diffs = {}
    for offset in diffs:
        sector = offset // 2352
        if sector not in sector_diffs:
            sector_diffs[sector] = []
        sector_diffs[sector].append(offset % 2352)
    
    print(f"Affected sectors: {len(sector_diffs):,}\n")
    
    # Show first 10 different sectors
    print("First 10 affected sectors:")
    for i, (sector, offsets) in enumerate(sorted(sector_diffs.items())[:10]):
        lba_offset = sector * 2048
        file_offset = sector * 2352
        print(f"  Sector {sector:6} (LBA offset {lba_offset:10}, file offset {file_offset:10}): {len(offsets):3} bytes differ")
        
        # Show if differences are in data or EDC/ECC area
        data_diffs = [o for o in offsets if o < 2048]
        edc_ecc_diffs = [o for o in offsets if o >= 2048]
        
        if data_diffs and edc_ecc_diffs:
            print(f"           Data: {len(data_diffs)} bytes, EDC/ECC: {len(edc_ecc_diffs)} bytes")
        elif data_diffs:
            print(f"           ⚠️  Data only: {len(data_diffs)} bytes")
        else:
            print(f"           EDC/ECC only: {len(edc_ecc_diffs)} bytes")
    
    print()
    
    # Check if differences are EDC/ECC only
    edc_ecc_only = all(
        all(offset % 2352 >= 2048 for offset in offsets)
        for offsets in sector_diffs.values()
    )
    
    if edc_ecc_only:
        print("✅ All differences are in EDC/ECC area (bytes 2048-2351 of each sector)")
        print("   This is expected if bins were built with different EDC/ECC calculators")
        print("   EDC/ECC differences should NOT affect gameplay\n")
    else:
        print("⚠️  Some differences are in DATA area (bytes 0-2047 of sectors)")
        print("   This WILL affect gameplay!\n")
    
    # Compare critical files
    print("=== Critical File Comparison ===\n")
    
    files_to_check = [
        "SYSTEM.CNF",
        "SLUS_009.42;1",
    ]
    
    for file_path in files_to_check:
        try:
            file1 = extract_file(bin1_data, file_path)
            file2 = extract_file(bin2_data, file_path)
            
            if file1 == file2:
                print(f"✅ {file_path}: identical ({len(file1)} bytes)")
            else:
                file_diffs = sum(1 for i in range(min(len(file1), len(file2))) if file1[i] != file2[i])
                print(f"❌ {file_path}: {file_diffs} bytes differ")
        except Exception as e:
            print(f"⚠️  {file_path}: {e}")
    
    print()
    
    # Show sample of data differences
    if not edc_ecc_only:
        print("=== Sample Data Differences ===\n")
        
        data_diff_count = 0
        for sector, offsets in sorted(sector_diffs.items())[:5]:
            data_offsets = [o for o in offsets if o < 2048]
            if not data_offsets:
                continue
            
            data_diff_count += 1
            sector_start = sector * 2352
            
            print(f"Sector {sector} (file offset {sector_start}):")
            for offset in data_offsets[:3]:  # Show first 3 per sector
                absolute_offset = sector_start + offset
                b1 = bin1_data[absolute_offset]
                b2 = bin2_data[absolute_offset]
                print(f"  Offset {absolute_offset:10} (+{offset:4} in sector): {b1:02x} vs {b2:02x}")
            
            if len(data_offsets) > 3:
                print(f"  ... and {len(data_offsets) - 3} more in this sector")
            print()
            
            if data_diff_count >= 5:
                break
    
    return 2


def main():
    import argparse
    
    ap = argparse.ArgumentParser(description="Find differences between two disc images")
    ap.add_argument("bin1", type=Path, help="First disc image")
    ap.add_argument("bin2", type=Path, help="Second disc image")
    
    args = ap.parse_args()
    
    return compare_bins(args.bin1, args.bin2)


if __name__ == "__main__":
    sys.exit(main())
