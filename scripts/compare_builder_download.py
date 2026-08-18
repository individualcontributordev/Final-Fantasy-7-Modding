#!/usr/bin/env python3
"""Compare builder-downloaded bin to working reference bin."""

import sys
from pathlib import Path

def compare_bins(builder_bin_path: str, working_bin_path: str):
    """Compare builder download to working bin and report differences."""
    
    builder_bin = Path(builder_bin_path)
    working_bin = Path(working_bin_path)
    
    if not builder_bin.exists():
        print(f"❌ Builder bin not found: {builder_bin}")
        return
    
    if not working_bin.exists():
        print(f"❌ Working bin not found: {working_bin}")
        return
    
    print("=== Builder Download vs Working Bin Analysis ===\n")
    
    builder_data = builder_bin.read_bytes()
    working_data = working_bin.read_bytes()
    
    print(f"Builder bin: {builder_bin}")
    print(f"  Size: {len(builder_data):,} bytes ({len(builder_data)//2352:,} sectors)")
    print()
    print(f"Working bin: {working_bin}")
    print(f"  Size: {len(working_data):,} bytes ({len(working_data)//2352:,} sectors)")
    print()
    
    if len(builder_data) != len(working_data):
        print("❌ SIZE MISMATCH!")
        print(f"   Difference: {abs(len(builder_data)-len(working_data)):,} bytes")
        return
    
    print("✅ Sizes match\n")
    
    # Byte-by-byte comparison
    print("Comparing byte-by-byte...")
    total_diffs = sum(1 for i in range(len(builder_data)) if builder_data[i] != working_data[i])
    
    if total_diffs == 0:
        print("✅ PERFECT MATCH - Files are identical!")
        return
    
    print(f"\n❌ Differences: {total_diffs:,} bytes ({100*total_diffs/len(builder_data):.4f}%)\n")
    
    # Sector-level analysis
    sector_size = 2352
    total_sectors = len(builder_data) // sector_size
    
    data_diff_sectors = []
    edc_diff_sectors = []
    
    for sector_num in range(total_sectors):
        offset = sector_num * sector_size
        
        if builder_data[offset:offset+sector_size] == working_data[offset:offset+sector_size]:
            continue
        
        # Check if only EDC/ECC differs
        builder_data_region = builder_data[offset+24:offset+2072]
        working_data_region = working_data[offset+24:offset+2072]
        
        if builder_data_region != working_data_region:
            data_diff_sectors.append(sector_num)
        else:
            edc_diff_sectors.append(sector_num)
    
    print(f"Sector analysis:")
    print(f"  Data differences     : {len(data_diff_sectors):>6,} sectors")
    print(f"  EDC/ECC only         : {len(edc_diff_sectors):>6,} sectors")
    print()
    
    if data_diff_sectors:
        print(f"❌ DATA DIFFERENCES FOUND!")
        print(f"   First 10 sectors with data differences:")
        for sector_num in data_diff_sectors[:10]:
            offset = sector_num * sector_size
            lba = sector_num - 16
            print(f"     Sector {sector_num} (LBA {lba})")
        print()
    
    # Check transition area (around sector 126959)
    transition_sector = 126959
    if transition_sector in data_diff_sectors or transition_sector in edc_diff_sectors:
        print(f"⚠️  CRITICAL: Sector {transition_sector} (disc transition area) differs!")
        offset = transition_sector * 2352
        
        print(f"\n  Data region:")
        print(f"    Builder: {builder_data[offset+24:offset+56].hex()}")
        print(f"    Working: {working_data[offset+24:offset+56].hex()}")
        
        if builder_data[offset+24:offset+2072] == working_data[offset+24:offset+2072]:
            print(f"    Data: ✅ MATCH")
        else:
            print(f"    Data: ❌ DIFFER")
        
        print(f"\n  EDC/ECC region:")
        print(f"    Builder: {builder_data[offset+2072:offset+2104].hex()}")
        print(f"    Working: {working_data[offset+2072:offset+2104].hex()}")
        
        if builder_data[offset+2072:offset+2352] == working_data[offset+2072:offset+2352]:
            print(f"    EDC/ECC: ✅ MATCH")
        else:
            print(f"    EDC/ECC: ❌ DIFFER")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_builder_download.py <builder-bin> <working-bin>")
        print("Example: python compare_builder_download.py ~/Downloads/FINALFANTASY7_D1.bin ~/Downloads/ff7-d1-csr-sd-mov-end.bin")
        sys.exit(1)
    
    compare_bins(sys.argv[1], sys.argv[2])
