#!/usr/bin/env python3
"""Ship single-disc-on-csr v0.1.36 - LOST2 music + ambient AKAOs

Fix: v0.1.35 enabled MUSIC opcode but hit RET before ambient AKAOs.
Solution: Replace RET at init/0 offset 0x3c with JMPF ->0x63 (ambient AKAOs).

v0.1.35 flow: MUSIC id=1 @0x3a -> RET @0x3c (stops)
v0.1.36 flow: MUSIC id=1 @0x3a -> JMPF @0x3c ->0x63 (reaches ambient AKAOs @0x63-0x10b)
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from psx_mode2_iso import extract_file
from lzs import decompress_all_with_header as decompress, compress_all_with_header as compress

# Read CSR D2 pristine LOST2
d2_bin = (ROOT / "workspace/pristine/FINALFANTASY7_D2.bin").read_bytes()
lost2_enc = extract_file(d2_bin, "FIELD/LOST2.DAT")
lost2_dec = decompress(lost2_enc)

print(f"D2 LOST2 decompressed size: {len(lost2_dec)}")

# Find init/0 script - it's at 0x0434 in CSR D2 pristine
# Verify by checking for MPNAM opcode (0x43)
idx = 0x0434
if idx >= len(lost2_dec) or lost2_dec[idx] != 0x43:
    raise SystemExit(f"Expected MPNAM at {idx:#x}, found {lost2_dec[idx]:#x}")

print(f"Found init/0 at offset {idx:#x}")

# The RET we want to patch is at idx + 0x3c
ret_offset = idx + 0x3c
print(f"RET at offset {ret_offset:#x}: {lost2_dec[ret_offset]:#x}")

if lost2_dec[ret_offset] != 0x00:
    raise SystemExit(f"Expected RET (0x00) at {ret_offset:#x}")

# Patch: replace single-byte RET with 3-byte JMPF ->0x63
# JMPF opcode: 0x10 <i16_le offset>
# Target: idx + 0x63 (ambient AKAOs)
# Offset from RET: 0x63 - 0x3c - 3 = 0x24
jmpf_offset = 0x24

new_dec = bytearray(lost2_dec[:ret_offset])
new_dec.extend([0x10, jmpf_offset, 0x00])  # JMPF +0x24
new_dec.extend(lost2_dec[ret_offset + 1:])  # Rest of file

print(f"Patched RET->{ret_offset:#x} to JMPF +{jmpf_offset:#x}")
print(f"Size change: {len(lost2_dec)} -> {len(new_dec)} ({len(new_dec) - len(lost2_dec):+d})")

# Compress
lost2_new_enc = compress(bytes(new_dec))
print(f"Compressed: {len(lost2_enc)} -> {len(lost2_new_enc)} ({len(lost2_new_enc) - len(lost2_enc):+d})")

# Build layer
layer_path = ROOT / "builder/single-disc-on-csr-v0.1.36-disc1.layer.json"
layer = {
    "version": "ic-layer-v1",
    "records": [
        {
            "path": "FIELD/LOST2.DAT",
            "data": lost2_new_enc.hex(),
        }
    ]
}

layer_path.write_text(json.dumps(layer, indent=2))
print(f"Wrote {layer_path}")

# Update manifest
manifest_path = ROOT / "builder/manifest.json"
manifest = json.loads(manifest_path.read_text())

addon = {
    "id": "single-disc-on-csr-v0.1.36",
    "displayName": "Single-Disc v0.1.36 (test)",
    "version": "0.1.36",
    "layerUrl": "./single-disc-on-csr-v0.1.36-disc1.layer.json",
    "compatibleBases": ["csr-v0.14.1", "highwind-v0.2.0"],
    "discs": [1],
    "badgeText": "v0.1.36",
    "description": "LOST2 forest music + ambient AKAOs",
    "autoIncludeWhen": {"addonSelected": "single-disc-on-csr-v0.1.33"},
    "enabled": True,
    "hidden": True,
}

# Find v0.1.35 and add v0.1.36 after it, disable v0.1.35
for i, a in enumerate(manifest["addons"]):
    if a["id"] == "single-disc-on-csr-v0.1.35":
        a["enabled"] = False
        manifest["addons"].insert(i + 1, addon)
        break
else:
    manifest["addons"].append(addon)

manifest_path.write_text(json.dumps(manifest, indent=2))
print(f"Updated {manifest_path}")
print("✓ v0.1.36 ready: LOST2 MUSIC + ambient AKAOs (JMPF patch)")
