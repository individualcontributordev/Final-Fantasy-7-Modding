#!/usr/bin/env python3
"""Extract files from FF7 PSX disc images (.bin files).

Usage:
    python scripts/extract_from_iso.py <disc.bin> <path/in/iso> <output-file>

Examples:
    # Extract FIELD.BIN from disc 1
    python scripts/extract_from_iso.py \
        workspace/pristine/FINALFANTASY7_D1.bin \
        FIELD/FIELD.BIN \
        workspace/iso-extract/FIELD.BIN

    # Extract BATTLE.BIN
    python scripts/extract_from_iso.py \
        workspace/pristine/FINALFANTASY7_D1.bin \
        BATTLE/BATTLE.BIN \
        workspace/iso-extract/BATTLE.BIN
"""

import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from psx_mode2_iso import extract_file


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        print("\nError: Wrong number of arguments")
        print(f"Got {len(sys.argv) - 1} arguments, expected 3")
        sys.exit(1)

    iso_path = Path(sys.argv[1])
    file_path = sys.argv[2]
    output_path = Path(sys.argv[3])

    # Validate inputs
    if not iso_path.exists():
        print(f"❌ ISO file not found: {iso_path}")
        print("\nAvailable disc images in workspace/pristine/:")
        pristine = Path("workspace/pristine")
        if pristine.exists():
            for f in pristine.glob("*.bin"):
                print(f"  - {f}")
        sys.exit(1)

    # Read disc image
    print(f"Reading disc image: {iso_path}")
    print(f"  Size: {iso_path.stat().st_size:,} bytes")
    
    img = iso_path.read_bytes()
    
    # Extract file
    print(f"\nExtracting: {file_path}")
    try:
        data = extract_file(img, file_path)
    except FileNotFoundError as e:
        print(f"❌ File not found in ISO: {e}")
        print("\nTip: Use uppercase paths like 'FIELD/FIELD.BIN'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        sys.exit(1)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    
    print(f"✅ Extracted {len(data):,} bytes")
    print(f"✅ Saved to: {output_path}")


if __name__ == "__main__":
    main()
