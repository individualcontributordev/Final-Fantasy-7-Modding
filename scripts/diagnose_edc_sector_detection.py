#!/usr/bin/env python3
"""
Diagnose which sectors the website's isMode2Form1 function would try to repair.

This helps us understand if the sector detection logic is too aggressive and
might be incorrectly repairing Form2 (FMV/audio) sectors as Form1 (data).
"""

from pathlib import Path

def is_mode2_form1(sector, offset=0):
    """Port of edc.js isMode2Form1 (lines 70-86)"""
    # sync + mode byte 2
    if sector[offset] != 0x00 or sector[offset + 11] != 0x00:
        return False
    for i in range(1, 11):
        if sector[offset + i] != 0xff:
            return False
    if sector[offset + 15] != 0x02:
        return False
    
    # Submode (byte 18)
    submode = sector[offset + 18]
    if submode & 0x20:  # Form 2
        return False
    if submode & 0x04:  # XA audio
        return False
    if submode & 0x02:  # video / STR
        return False
    if not (submode & 0x08):  # require Data bit (ISO file sectors)
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

# Load bins
working_bin = Path("~/Downloads/ff7-d1-csr-sd-mov-end.bin").expanduser()
csr_base = Path("workspace/csr-v0.14.1-d1-base.bin")

if not working_bin.exists():
    print("❌ Working bin not found")
    exit(1)

if not csr_base.exists():
    print("❌ CSR base not found")
    exit(1)

working_data = working_bin.read_bytes()
source_data = csr_base.read_bytes()

print("=== Sectors That Would Be Repaired by Website ===\n")

source_sectors = len(source_data) // 2352
working_sectors = len(working_data) // 2352

would_repair = []

for lba in range(working_sectors):
    is_new = lba >= source_sectors
    
    if not is_new and not sector_changed(source_data, working_data, lba):
        continue
    
    # Sector changed or is new
    offset = lba * 2352
    if is_mode2_form1(working_data, offset):
        would_repair.append(lba)

print(f"Total sectors: {working_sectors:,}")
print(f"Source sectors: {source_sectors:,}")
print(f"New sectors: {working_sectors - source_sectors:,}")
print(f"Sectors that would be repaired: {len(would_repair):,}")
print()

# Sample first 10 and last 10
print("First 10 sectors that would be repaired:")
for lba in would_repair[:10]:
    offset = lba * 2352
    submode = working_data[offset + 18]
    print(f"  LBA {lba}: submode {submode:#04x}")

print()
print("Last 10 sectors that would be repaired:")
for lba in would_repair[-10:]:
    offset = lba * 2352
    submode = working_data[offset + 18]
    print(f"  LBA {lba}: submode {submode:#04x}")

print()

# Check critical transition area
print("Sectors in transition area (LBA 58700-58730):")
transition_repairs = [lba for lba in would_repair if 58700 <= lba <= 58730]
if transition_repairs:
    for lba in transition_repairs:
        offset = lba * 2352
        submode = working_data[offset + 18]
        print(f"  LBA {lba}: submode {submode:#04x} - WOULD REPAIR")
else:
    print("  None (transition sectors unchanged from CSR base)")

print()

# Check disc 2 area
print("Sectors in disc 2 content area (LBA 126991-127020):")
d2_repairs = [lba for lba in would_repair if 126991 <= lba <= 127020]
if d2_repairs:
    for lba in d2_repairs:
        offset = lba * 2352
        submode = working_data[offset + 18]
        print(f"  LBA {lba}: submode {submode:#04x} - WOULD REPAIR")
else:
    print("  None (disc 2 area unchanged from CSR base)")
