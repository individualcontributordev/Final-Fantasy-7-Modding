"""Build single-disc v0.1.36: BLACKBGB music before MAPJUMP #634.

Root cause (from 2026-08-13-v035-music-fail-save-ok.md):
- BLACKBGB disc-2 arms run MAPJUMP #634, then MUSIC id=3
- MUSIC after MAPJUMP never executes (player already on #634)
- Fix: move MUSIC before MAPJUMP in both disc-2 branches

Strategy:
1. Extract BLACKBGB from CSR D1
2. Decode init/0 script to find MAPJUMP #634 opcodes
3. Insert MUSIC opcode before each MAPJUMP #634
4. Recompress and create layer
"""
import sys
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from psx_mode2_iso import find_file, _read_extent
from field_dat import decompress_dat, slice_sections, decode_ops, OPCODE_NAMES, op_size
from lzs import compress_all, compress_all_with_header

# Load CSR D1 BLACKBGB
csr_d1 = (ROOT / "workspace/iso-extract/csr_d1_only.bin").read_bytes()
meta = find_file(csr_d1, "FIELD/BLACKBGB.DAT")
raw = _read_extent(csr_d1, meta.lba, meta.size)
dec = decompress_dat(raw)
secs = slice_sections(dec)

# Parse section 1 (scripts)
sec1 = secs[0]
version = struct.unpack_from("<H", sec1, 0)[0]
nb = sec1[2]
pos_texts = struct.unpack_from("<H", sec1, 4)[0]

# Entity table starts at offset 16 for retail
# Each entity: 8 bytes name, then 32 script u16 offsets
cur = 16
entities = []
for i in range(nb):
    name = sec1[cur:cur+8].split(b"\x00")[0].decode("latin1", "replace")
    entities.append(name)
    cur += 8 + 64  # name + 32 u16 script offsets

# Find init/0 script (first entity, first script slot)
# Script offset table is at entity_base + 8
script_table_off = 16 + 8  # After version/counts header, after first entity name
init0_off = struct.unpack_from("<H", sec1, script_table_off)[0]

# Decode init/0 to find MAPJUMP #634
init0_data = sec1[init0_off:pos_texts]
ops = decode_ops(init0_data)

print("BLACKBGB init/0 script analysis:")
print(f"  Total opcodes: {len(ops)}")
print()

# Find all MAPJUMP #634 locations
mapjump_634_positions = []
pos = 0
for raw_op, name in ops:
    if name == "MAPJUMP" and len(raw_op) >= 3:
        map_id = raw_op[1] | (raw_op[2] << 8)
        if map_id == 634:
            print(f"  Found MAPJUMP #634 at offset 0x{pos:04x}")
            mapjump_634_positions.append(pos)
    pos += len(raw_op)

if not mapjump_634_positions:
    print("ERROR: No MAPJUMP #634 found in BLACKBGB init/0")
    sys.exit(1)

print(f"\n  Will insert MUSIC id=1 before {len(mapjump_634_positions)} MAPJUMP #634 opcode(s)")
print()

# Build patched script by inserting MUSIC id=1 (0x19 0x01) before each MAPJUMP #634
music_op = bytes([0x19, 0x01])  # MUSIC track=1
patched_init0 = bytearray()
pos = 0

for raw_op, name in ops:
    # If this is MAPJUMP #634, insert MUSIC first
    if name == "MAPJUMP" and len(raw_op) >= 3:
        map_id = raw_op[1] | (raw_op[2] << 8)
        if map_id == 634:
            patched_init0.extend(music_op)
            print(f"  Inserted MUSIC at offset 0x{len(patched_init0)-2:04x}")
    
    # Then add the original opcode
    patched_init0.extend(raw_op)
    pos += len(raw_op)

print(f"\n  Original init/0 size: {len(init0_data)} bytes")
print(f"  Patched init/0 size: {len(patched_init0)} bytes")
print(f"  Growth: +{len(patched_init0) - len(init0_data)} bytes")

# Rebuild section 1 with patched script
# Keep everything before init/0, insert patched script, keep everything after
new_sec1 = bytearray(sec1[:init0_off])
new_sec1.extend(patched_init0)
new_sec1.extend(sec1[pos_texts:])

print(f"\n  Original section 1 size: {len(sec1)} bytes")
print(f"  Patched section 1 size: {len(new_sec1)} bytes")

# Rebuild full DAT with updated section offsets
# Sections: scripts, walkmesh, background, camera, inf, encounter, model_loader
new_secs = [bytes(new_sec1)] + secs[1:]
vbase = 0x80000000 + 28  # PSX VRAM base for offsets
offs = []
cur_pos = 28
for s in new_secs:
    offs.append(vbase + cur_pos)
    cur_pos += len(s)

header = struct.pack("<7I", *offs)
new_dec = header + b"".join(new_secs)

print(f"\n  Original decompressed DAT: {len(dec)} bytes")
print(f"  Patched decompressed DAT: {len(new_dec)} bytes")

# Compress
new_comp = compress_all_with_header(new_dec)
print(f"  Patched compressed: {len(new_comp)} bytes (original: {len(raw)} bytes)")

# Save layer
OUT = ROOT / "mods/single-disc/layers/single-disc-on-csr-v0.1.36-disc1.layer.json"
layer = {
    "id": "single-disc-on-csr-v0.1.36",
    "version": "0.1.36",
    "name": "Single-disc on CSR",
    "description": "v0.1.36: BLACKBGB forest music before MAPJUMP #634",
    "records": [
        {
            "path": "FIELD/BLACKBGB.DAT",
            "mode": "replace_within_sectors",
            "data_base64": __import__("base64").b64encode(new_comp).decode()
        }
    ]
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(layer, indent=2))
print(f"\nWrote {OUT}")
print("\nNext: update manifest, test on CSR D1")
