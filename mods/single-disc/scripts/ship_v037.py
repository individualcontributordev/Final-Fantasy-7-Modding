#!/usr/bin/env python3
"""
Single-disc v0.1.37 — Fix D1→D2 transition (force break scene)

Problem:
- CSR LOST2 D2 init checks GM=0xa455 before jumping to COS_BTM2 break scene
- Single-disc never sets the transition bit (no disc swap hardware)
- Result: LOST2 RETs without playing break scene or music

Fix:
- Patch LOST2 init script offset 0x44 (IFUW "else" parameter)
- Change from 0x0b (skip MAPJUMP) to 0x00 (execute MAPJUMP always)
- Forces break scene regardless of GM state

Technical Detail:
LOST2 init @ script offset:
  0x3D: IFUW addr=0x0020 == 0xa455, else +0xb
  0x45: MAPJUMP field #526 (0x20e) — COS_BTM2 break scene

Patch byte at global offset 0x0471 (init script base 0x0434 + 0x3D + 7)
from 0x0b → 0x00

Ship: hidden auto addon, enabled when single-disc core is selected
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from psx_mode2_iso import extract_file
from lzs import decompress_all_with_header as decompress, compress_all_with_header as compress

VERSION = "0.1.37"
PACK_ID = f"single-disc-on-csr-v{VERSION}"
LAYER_DIR = ROOT / "builder" / PACK_ID

def create_pack():
    """Create v0.1.37 layer pack with LOST2 patch"""

    # Read CSR D1 LOST2.DAT (already has LOST2 from both discs merged)
    # CSR is built in sibling repo; use cache if available
    csr_bin_path = ROOT.parent / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D1.bin"
    if not csr_bin_path.exists():
        raise SystemExit(
            f"CSR D1 bin not found at {csr_bin_path}\n"
            f"Build it first: cd ../Final-Fantasy-7-CSR && python3 scripts/build_csr_base_layers.py csr --version 0.14.1 --discs 1"
        )

    d1_bin = csr_bin_path.read_bytes()
    lost2_enc = extract_file(d1_bin, "FIELD/LOST2.DAT")
    lost2_dec = bytearray(decompress(lost2_enc))

    print(f"CSR D1 LOST2 decompressed: {len(lost2_dec)} bytes")

    # Init script starts at 0x434 in CSR D1 LOST2
    init_base = 0x434
    if lost2_dec[init_base] != 0x43:  # MPNAM opcode
        raise SystemExit(f"Expected MPNAM at {init_base:#x}, found {lost2_dec[init_base]:#x}")

    # Two IFUW checks that skip music when GM != 0xa455:
    # @0x43C: IFUW addr=0x0020 != 0xa455, else +0x5
    # @0x448: IFUW addr=0x0020 != 0xa455, else +0x3

    # Patch both else offsets to 0x00 so music always plays
    ifuw1_offset = 0x43C
    ifuw2_offset = 0x448
    else1_offset = ifuw1_offset + 7  # 0x443
    else2_offset = ifuw2_offset + 7  # 0x44F

    print(f"\nIFUW #1 at {ifuw1_offset:#x}, else param at {else1_offset:#x}: {lost2_dec[else1_offset]:#x}")
    print(f"IFUW #2 at {ifuw2_offset:#x}, else param at {else2_offset:#x}: {lost2_dec[else2_offset]:#x}")

    # Verify expected values before patching
    if lost2_dec[else1_offset] != 0x05:
        raise SystemExit(f"Expected 0x05 at {else1_offset:#x}, found {lost2_dec[else1_offset]:#x}")
    if lost2_dec[else2_offset] != 0x03:
        raise SystemExit(f"Expected 0x03 at {else2_offset:#x}, found {lost2_dec[else2_offset]:#x}")

    # Patch both
    lost2_dec[else1_offset] = 0x00
    lost2_dec[else2_offset] = 0x00
    print(f"\nPatched both to 0x00")

    # Re-compress
    lost2_patched = compress(bytes(lost2_dec))
    print(f"Compressed patched LOST2: {len(lost2_patched)} bytes")

    # Build layer JSON
    layer = {
        "version": "ic-layer-v1",
        "records": [
            {
                "path": "FIELD/LOST2.DAT",
                "data": lost2_patched.hex()
            }
        ]
    }

    pack = {
        "id": PACK_ID,
        "version": VERSION,
        "name": "(auto) disc-break fix",
        "blurb": "Internal auto: force D1→D2 break scene by patching LOST2 IFUW.",
        "hint": "Always with Single-disc.",
        "format": "ic-layer-v1",
        "compatibleBases": ["csr-v0.14.1"],
        "layout": "global",
        "enabled": True,
        "uiHidden": True,
        "hidden": True,
        "beta": True,
        "status": "beta",
        "autoIncludeWhen": {
            "addonSelected": "single-disc-on-csr-v0.1.33"
        }
    }

    # Write outputs
    LAYER_DIR.mkdir(parents=True, exist_ok=True)
    layers_dir = LAYER_DIR / "layers"
    layers_dir.mkdir(exist_ok=True)

    (layers_dir / "disc1.layer.json").write_text(json.dumps(layer, indent=2))
    (LAYER_DIR / "pack.json").write_text(json.dumps(pack, indent=2))

    print(f"\n✅ Created {PACK_ID}")
    print(f"   Layer: {layers_dir / 'disc1.layer.json'}")
    print(f"   Pack: {LAYER_DIR / 'pack.json'}")

if __name__ == "__main__":
    create_pack()
