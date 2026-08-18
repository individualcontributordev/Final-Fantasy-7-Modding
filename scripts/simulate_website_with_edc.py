#!/usr/bin/env python3
"""
Simulate the EXACT website build process including EDC repair.

This applies layers AND regenerates EDC/ECC for changed sectors,
matching the website's builder.js + edc.js behavior.
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from test_edc_calculation import generate_mode2_form1_edc_ecc

def load_layer(path):
    """Load an ic-layer-v1 file"""
    data = Path(path).read_bytes()
    text = data.decode('utf-8')
    return json.loads(text)

def apply_layer(bin_data, layer):
    """Apply a layer to bin data"""
    result = bytearray(bin_data)

    for op in layer['ops']:
        if op['t'] == 'w':
            # Write operation
            offset = op['o']
            data_hex = op['d']
            data_bytes = bytes.fromhex(data_hex)
            result[offset:offset+len(data_bytes)] = data_bytes
        elif op['t'] == 'a':
            # Append operation
            data_hex = op['d']
            data_bytes = bytes.fromhex(data_hex)
            result.extend(data_bytes)

    return bytes(result)

def is_mode2_form1(sector, offset=0):
    """Check if sector is Mode2 Form1 (from edc.js lines 70-86)"""
    # Check sync pattern and mode byte
    if sector[offset] != 0x00 or sector[offset + 11] != 0x00:
        return False
    for i in range(1, 11):
        if sector[offset + i] != 0xff:
            return False
    if sector[offset + 15] != 0x02:  # Mode 2
        return False
    
    # Check submode
    submode = sector[offset + 18]
    if submode & 0x20:  # Form 2
        return False
    if submode & 0x04:  # XA audio
        return False
    if submode & 0x02:  # video / STR
        return False
    if not (submode & 0x08):  # require Data bit
        return False
    
    return True

def sector_changed(source, patched, lba):
    """Check if a sector changed"""
    offset = lba * 2352
    source_sector = source[offset:offset+2352] if offset < len(source) else None
    patched_sector = patched[offset:offset+2352] if offset < len(patched) else None
    
    if source_sector is None or patched_sector is None:
        return True  # New or missing sector
    
    return source_sector != patched_sector

def repair_edc_in_image(source_bytes, patched_bytes):
    """
    Regenerate Mode2 Form1 EDC/ECC for every sector that differs from source.
    (from edc.js lines 148-191)
    """
    if len(patched_bytes) % 2352 != 0:
        raise ValueError(f"Image length {len(patched_bytes)} not multiple of 2352")
    
    source_sectors = len(source_bytes) // 2352
    patched_sectors = len(patched_bytes) // 2352
    
    fixed = 0
    changed = 0
    
    result = bytearray(patched_bytes)
    
    for lba in range(patched_sectors):
        offset = lba * 2352
        is_new = lba >= source_sectors
        
        if not is_new and not sector_changed(source_bytes, patched_bytes, lba):
            continue
        
        changed += 1
        
        # Check if it's Mode2 Form1 that needs repair
        if is_mode2_form1(result, offset):
            sector = result[offset:offset+2352]
            repaired = generate_mode2_form1_edc_ecc(sector)
            result[offset:offset+2352] = repaired
            fixed += 1
    
    print(f"EDC repair: {changed} changed sectors, {fixed} repaired")
    return bytes(result)


# Main simulation
print("=== Simulating Website Build WITH EDC Repair ===\n")

# Use CSR v0.14.1 base as source (matching what website would use)
csr_base_path = Path("workspace/csr-v0.14.1-d1-base.bin")
if not csr_base_path.exists():
    print(f"❌ CSR base not found at {csr_base_path}")
    print("   Using pristine instead...")
    csr_base_path = Path("workspace/pristine/FINALFANTASY7_D1.bin")

source = csr_base_path.read_bytes()
print(f"Source: {csr_base_path.name}")
print(f"        {len(source):,} bytes ({len(source)//2352} sectors)")

# Apply all 10 single-disc parts
modding_repo = Path(__file__).parent.parent
bin_data = source
for i in range(1, 11):
    layer_path = modding_repo / f"builder/ff7-d1-csr-sd-mov-end-part{i:02d}.iclayerv1"
    layer = load_layer(layer_path)
    print(f"Applying part {i:02d} ({len(layer['ops'])} ops)...")
    bin_data = apply_layer(bin_data, layer)

print(f"\nAfter layers: {len(bin_data):,} bytes ({len(bin_data)//2352} sectors)")

# Apply EDC repair (this is what the website does!)
print("\nApplying EDC/ECC repair...")
bin_data = repair_edc_in_image(source, bin_data)

# Save result
output_path = Path("workspace/website-simulated-with-edc.bin")
output_path.write_bytes(bin_data)
print(f"\n✅ Saved to: {output_path}")
print(f"   Size: {len(bin_data):,} bytes")

# Compare to working bin
working_path = Path("~/Downloads/ff7-d1-csr-sd-mov-end.bin").expanduser()
if working_path.exists():
    working = working_path.read_bytes()
    if bin_data == working:
        print("\n✅ PERFECT MATCH with working bin!")
    else:
        print(f"\n❌ DIFFERS from working bin")
        print(f"   Working size: {len(working):,} bytes")
        
        # Find first difference
        for i in range(min(len(bin_data), len(working))):
            if bin_data[i] != working[i]:
                lba = i // 2352
                offset_in_sector = i % 2352
                print(f"   First diff at byte {i:,} (LBA {lba}, offset {offset_in_sector})")
                break
