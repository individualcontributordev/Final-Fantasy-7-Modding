#!/usr/bin/env python3
"""
Build v0.1.2 single-disc with EDC/ECC repair.

This script:
1. Applies all layers (field + manip-movies + endings)
2. Repairs EDC/ECC for all modified sectors
3. Verifies exact match to working bin
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))

import json
from apply_layer import apply_layer
from edc_ecc import repair_image_edc_ecc


def main():
    print("=== Single-Disc v0.1.2 Build with EDC/ECC Repair ===\n")
    
    # Paths
    repo_root = Path(__file__).parent.parent.parent.parent
    pristine = repo_root / "workspace/pristine/FINALFANTASY7_D1.bin"
    working = Path("/Users/david.morton/Downloads/ff7-d1-csr-sd-mov-end.bin")
    output = repo_root / "workspace/v012-build/v012-with-edc.bin"
    
    # Layer paths
    field_layer = repo_root / "builder/single-disc-on-csr/layers/disc1.layer.json"
    manip_layer = repo_root / "builder/single-disc-csr-manip-movies-v0.1.4/layers/disc1.layer.json"
    ending_layers = [
        repo_root / f"builder/single-disc-endings-v0.1.0-part{i}/layers/disc1.layer.json"
        for i in range(1, 8)
    ]
    
    # Verify all layers exist
    all_layers = [field_layer, manip_layer] + ending_layers
    for layer in all_layers:
        if not layer.exists():
            print(f"❌ Layer not found: {layer}")
            sys.exit(1)
    
    print("Step 1: Load pristine D1")
    if not pristine.exists():
        print(f"❌ Pristine bin not found: {pristine}")
        sys.exit(1)
    
    img = bytearray(pristine.read_bytes())
    print(f"✅ Loaded {len(img):,} bytes\n")
    
    print("Step 2: Apply all layers")
    
    # Apply field layer
    print("  - Field layer...")
    layer = json.loads(field_layer.read_text())
    apply_layer(img, layer)
    print(f"    ✅ {len(layer['records']):,} records")
    
    # Apply manip-movies
    print("  - Manip-movies...")
    layer = json.loads(manip_layer.read_text())
    apply_layer(img, layer)
    print(f"    ✅ {len(layer['records']):,} records")
    
    # Apply endings
    for i, ending_path in enumerate(ending_layers, 1):
        print(f"  - Ending part {i}/7...")
        layer = json.loads(ending_path.read_text())
        apply_layer(img, layer)
        print(f"    ✅ {len(layer['records']):,} records")
    
    print(f"\n✅ All layers applied\n")
    
    print("Step 3: Identify modified sectors from layers")
    # Track which sectors were modified
    pristine_img = bytearray(pristine.read_bytes())
    sector_size = 2352
    total_sectors = len(img) // sector_size

    modified_sectors = set()
    for sector_num in range(total_sectors):
        offset = sector_num * sector_size
        if img[offset:offset+sector_size] != pristine_img[offset:offset+sector_size]:
            modified_sectors.add(sector_num)

    print(f"  {len(modified_sectors):,} sectors modified by layers\n")

    print("Step 4: Repair EDC/ECC for modified sectors only")
    from edc_ecc import repair_sector_edc_ecc

    for i, sector_num in enumerate(sorted(modified_sectors)):
        if i % 1000 == 0:
            print(f"  Progress: {i:,} / {len(modified_sectors):,} sectors...")

        offset = sector_num * sector_size
        sector = img[offset:offset+sector_size]
        repair_sector_edc_ecc(sector)

    print(f"  ✅ EDC/ECC repaired for {len(modified_sectors):,} sectors\n")

    print("Step 5: Save and verify")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(img)
    print(f"✅ Saved to: {output}\n")
    
    # Verify against working bin
    if working.exists():
        print("Step 6: Verify against working bin")
        working_data = working.read_bytes()
        
        print(f"  Working: {len(working_data):,} bytes")
        print(f"  Rebuilt: {len(img):,} bytes")
        
        if len(img) != len(working_data):
            print(f"  ❌ SIZE MISMATCH: {len(img) - len(working_data):,} bytes")
            sys.exit(1)
        
        print("  ✅ Sizes match\n")
        
        # Byte-by-byte comparison
        print("  Byte-by-byte comparison...")
        diffs = sum(1 for i in range(len(img)) if img[i] != working_data[i])
        
        if diffs == 0:
            print("  🎉 PERFECT MATCH! Byte-for-byte identical!")
            print("\n✅✅✅ SUCCESS ✅✅✅")
            print("The rebuilt bin is EXACTLY the same as your working bin.")
        else:
            print(f"  ❌ {diffs:,} bytes differ ({100*diffs/len(img):.4f}%)")
            
            # Analyze remaining differences
            print("\n  Analyzing remaining differences...")
            sector_size = 2352
            diff_sectors = []
            for sector_num in range(len(img) // sector_size):
                offset = sector_num * sector_size
                if img[offset:offset+sector_size] != working_data[offset:offset+sector_size]:
                    diff_sectors.append(sector_num)
            
            print(f"  Different sectors: {len(diff_sectors):,}")
            
            if len(diff_sectors) > 0:
                print(f"\n  First 10 different sectors:")
                for sector_num in diff_sectors[:10]:
                    print(f"    Sector {sector_num:6d} (0x{sector_num:05X})")
            
            sys.exit(1)
    else:
        print("  (Working bin not found for comparison)\n")
    
    print(f"\n✅ Build complete: {output}")
    print("Next: Test in DuckStation")


if __name__ == "__main__":
    main()
