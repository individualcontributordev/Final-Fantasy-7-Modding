#!/usr/bin/env python3
"""
Test if the website's EDC/ECC calculation produces the same values as what's
already in the working bin.

This ports the exact JavaScript logic from edc.js to Python.
"""

from pathlib import Path

# EDC/ECC lookup tables (from edc.js lines 25-40)
ecc_f_lut = [0] * 256
ecc_b_lut = [0] * 256
edc_lut = [0] * 256

def init_luts():
    for i in range(256):
        j = (i << 1) ^ (0x11d if (i & 0x80) else 0)
        ecc_f_lut[i] = j & 0xff
        ecc_b_lut[i ^ j] = i
        
        edc = i
        for k in range(8):
            edc = (edc >> 1) ^ (0xd8018001 if (edc & 1) else 0)
        edc_lut[i] = edc & 0xffffffff

init_luts()

def edc_compute_block(src, start, size):
    """Compute EDC for a block (from edc.js lines 42-48)"""
    edc = 0
    for i in range(size):
        edc = (edc_lut[(edc ^ src[start + i]) & 0xff] ^ (edc >> 8)) & 0xffffffff
    return edc

def ecc_compute_block(src_base, major_count, minor_count, major_mult, minor_inc):
    """Compute ECC block (from edc.js lines 50-68)"""
    size = major_count * minor_count
    result = bytearray(major_count * 2)
    
    for major in range(major_count):
        index = ((major >> 1) * major_mult + (major & 1))
        ecc_a = 0
        ecc_b = 0
        
        for minor in range(minor_count):
            temp = src_base[index]
            index += minor_inc
            if index >= size:
                index -= size
            ecc_a ^= temp
            ecc_b ^= temp
            ecc_a = ecc_f_lut[ecc_a]
        
        ecc_a = ecc_b_lut[ecc_f_lut[ecc_a] ^ ecc_b]
        result[major] = ecc_a
        result[major + major_count] = ecc_a ^ ecc_b
    
    return result

def generate_mode2_form1_edc_ecc(sector_data):
    """Generate EDC/ECC for a Mode2 Form1 sector (from edc.js lines 92-116)"""
    sector = bytearray(sector_data)
    
    # Compute EDC (bytes 2072-2075)
    edc = edc_compute_block(sector, 0x10, 0x808)  # subheader + user data
    sector[0x818] = edc & 0xff
    sector[0x819] = (edc >> 8) & 0xff
    sector[0x81a] = (edc >> 16) & 0xff
    sector[0x81b] = (edc >> 24) & 0xff
    
    # Save and zero address bytes for ECC calculation
    a0, a1, a2, a3 = sector[12], sector[13], sector[14], sector[15]
    sector[12] = sector[13] = sector[14] = sector[15] = 0
    
    # Compute ECC P (bytes 2076-2247)
    src = sector[0x0c:]  # from byte 12
    ecc_p = ecc_compute_block(src, 86, 24, 2, 86)
    sector[0x81c:0x81c+172] = ecc_p
    
    # Compute ECC Q (bytes 2248-2351)
    ecc_q = ecc_compute_block(src, 52, 43, 86, 88)
    sector[0x8c8:0x8c8+104] = ecc_q
    
    # Restore address bytes
    sector[12], sector[13], sector[14], sector[15] = a0, a1, a2, a3
    
    return bytes(sector)


# Test on a new sector from working bin
working = Path("~/Downloads/ff7-d1-csr-sd-mov-end.bin").expanduser()
working_data = working.read_bytes()

print("=== Testing EDC/ECC Calculation ===\n")

# Test on LBA 317788 (a new Form1 data sector)
lba = 317788
offset = lba * 2352
sector_original = working_data[offset:offset+2352]

# Regenerate EDC/ECC
sector_regenerated = generate_mode2_form1_edc_ecc(sector_original)

# Compare
if sector_original == sector_regenerated:
    print(f"✅ LBA {lba}: EDC/ECC regeneration produces IDENTICAL result")
else:
    # Find differences
    diffs = [i for i in range(2352) if sector_original[i] != sector_regenerated[i]]
    print(f"❌ LBA {lba}: EDC/ECC regeneration produces DIFFERENT result")
    print(f"   {len(diffs)} bytes differ")
    
    # Show first few differences
    for i in diffs[:10]:
        print(f"   Offset {i}: {sector_original[i]:02x} → {sector_regenerated[i]:02x}")

print()

# Test on a few more
for test_lba in [317789, 317790, 317800, 318000]:
    offset = test_lba * 2352
    if offset + 2352 > len(working_data):
        break
        
    sector_original = working_data[offset:offset+2352]
    sector_regenerated = generate_mode2_form1_edc_ecc(sector_original)
    
    match = sector_original == sector_regenerated
    print(f"{'✅' if match else '❌'} LBA {test_lba}: {'MATCH' if match else 'DIFFER'}")
