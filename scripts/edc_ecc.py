"""
PSX Mode 2 Form 1 EDC/ECC calculation and repair.

Based on the CD-ROM Yellow Book standard for Mode 2 Form 1 sectors.
Each sector is 2352 bytes:
- 12 bytes sync
- 4 bytes header (MSF address + mode)
- 8 bytes subheader
- 2048 bytes user data
- 4 bytes EDC (Error Detection Code)
- 276 bytes ECC (Error Correction Code - P and Q parity)

References:
- https://problemkaputt.de/psxspx-cdrom-sector-encoding.htm
- https://github.com/ralfguth/langrisser3-english/blob/main/tools/iso_tools.py
"""

# Pre-computed EDC CRC table (polynomial 0xD8018001)
_EDC_TABLE = None

def _init_edc_table():
    """Initialize EDC CRC lookup table."""
    global _EDC_TABLE
    if _EDC_TABLE is not None:
        return

    _EDC_TABLE = []
    for i in range(256):
        edc = i
        for _ in range(8):
            edc = (edc >> 1) ^ (0xD8018001 if (edc & 1) else 0)
        _EDC_TABLE.append(edc)


def compute_edc(data: bytes) -> int:
    """
    Compute EDC (CRC-32) for Mode 2 Form 1 sector data.

    Args:
        data: Data to compute EDC for (header + subheader + user data)

    Returns:
        32-bit EDC value
    """
    _init_edc_table()

    edc = 0
    for byte_val in data:
        edc = (edc >> 8) ^ _EDC_TABLE[(edc ^ byte_val) & 0xFF]
    return edc


def compute_ecc(sector: bytearray):
    """
    Compute and write ECC (P and Q parity) for Mode 2 Form 1 sector.

    Simplified implementation based on proven algorithms.
    Modifies sector in-place, writing 276 bytes of ECC starting at offset 2076.

    Args:
        sector: 2352-byte Mode 2 Form 1 sector (will be modified)
    """
    # Clear ECC area first
    sector[2076:2352] = b'\x00' * 276

    # P parity: 86 vectors of 24 bytes each (172 bytes total)
    p_data = bytes(sector[12:2076])
    p_result = bytearray(172)

    for i in range(86):
        a0, a1 = 0, 0
        for j in range(24):
            idx = i + j * 86
            if idx < len(p_data):
                val = p_data[idx]
            else:
                val = 0
            a0 ^= val
            a1 ^= val
            a0 = ((a0 << 1) ^ (0x11D if a0 & 0x80 else 0)) & 0xFF

        p_result[2 * i] = a0 ^ a1
        p_result[2 * i + 1] = a0

    sector[2076:2248] = p_result

    # Q parity: 52 vectors of 43 bytes each (104 bytes total)
    q_data = bytes(sector[12:2248])
    q_result = bytearray(104)

    for i in range(52):
        a0, a1 = 0, 0
        for j in range(43):
            idx = (i + j * 52) % (43 * 52)
            if idx < len(q_data):
                val = q_data[idx]
            else:
                val = 0
            a0 ^= val
            a1 ^= val
            a0 = ((a0 << 1) ^ (0x11D if a0 & 0x80 else 0)) & 0xFF

        q_result[2 * i] = a0 ^ a1
        q_result[2 * i + 1] = a0

    sector[2248:2352] = q_result


def repair_sector_edc_ecc(sector: bytearray):
    """
    Recalculate and fix EDC/ECC for a Mode 2 Form 1 sector.
    
    Modifies sector in-place.
    
    Args:
        sector: 2352-byte Mode 2 Form 1 sector (will be modified)
    """
    # Check if it's Mode 2 Form 1 (subheader byte 2 should have bit 5 clear)
    if len(sector) != 2352:
        return
    
    # Mode 2 Form 1 check: subheader[2] & 0x20 == 0
    if sector[16 + 2] & 0x20:
        return  # Mode 2 Form 2, no EDC/ECC
    
    # Compute EDC for bytes 16-2075 (header + subheader + data)
    edc_data = sector[16:2076]
    edc = compute_edc(edc_data)
    
    # Write EDC (little-endian)
    sector[2072:2076] = edc.to_bytes(4, 'little')
    
    # Compute and write ECC
    compute_ecc(sector)


def repair_image_edc_ecc(img: bytearray):
    """
    Repair EDC/ECC for all Mode 2 Form 1 sectors in a disc image.
    
    Modifies image in-place.
    
    Args:
        img: PSX disc image (will be modified)
    """
    sector_size = 2352
    total_sectors = len(img) // sector_size
    
    for sector_num in range(total_sectors):
        offset = sector_num * sector_size
        sector = img[offset:offset + sector_size]
        repair_sector_edc_ecc(sector)
