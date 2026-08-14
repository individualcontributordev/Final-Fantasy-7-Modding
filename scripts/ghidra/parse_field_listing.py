#!/usr/bin/env python3
"""Parse Ghidra FIELD.BIN listing export to structured JSON.

Reads: workspace/ghidra-exports/FIELD.BIN.listing.txt (gitignored)
Writes: workspace/ghidra-analysis/field-functions.json (committed)

The listing export contains raw decompiled code. This script extracts only:
- Function addresses and names
- Function sizes
- Cross-references (calls, jumps)
- Data references (to RNG table, Danger, etc.)

Output is structured metadata, not game code.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXPORT_PATH = ROOT / "workspace/ghidra-exports/FIELD.BIN.listing.txt"
OUTPUT_PATH = ROOT / "workspace/ghidra-analysis/field-functions.json"


def parse_listing(listing_path: Path) -> dict:
    """Parse Ghidra listing export and extract structured function metadata.
    
    Returns:
        {
          "functions": [
            {
              "address": "0x800AB9C8",
              "name": "increment_step_id",
              "size": 108,
              "calls_to": ["0x800ABXXX", ...],
              "data_refs": ["0x800E0638", ...]
            },
            ...
          ],
          "data_symbols": {
            "0x800E0638": "g_field_rng_table",
            ...
          }
        }
    """
    if not listing_path.exists():
        raise FileNotFoundError(
            f"Listing not found: {listing_path}\n"
            "Run the Ghidra export steps first (see docs/INSTRUCTIONS.md)"
        )
    
    # TODO: Implement actual parsing based on Ghidra listing format
    # This is a placeholder - will be filled once we see the real export format
    
    print(f"Reading: {listing_path}")
    text = listing_path.read_text()
    
    # Placeholder structure
    result = {
        "source": str(listing_path),
        "format": "ghidra-listing",
        "functions": [],
        "data_symbols": {},
        "notes": "Parser stub - update after seeing real listing format"
    }
    
    return result


def main() -> int:
    print(f"FIELD.BIN listing parser")
    print(f"Export: {EXPORT_PATH}")
    print(f"Output: {OUTPUT_PATH}")
    
    if not EXPORT_PATH.exists():
        print(f"\nERROR: Export file not found!")
        print(f"Expected: {EXPORT_PATH}")
        print(f"\nRun the Ghidra export steps first:")
        print(f"  1. Import FIELD.BIN.dec into Ghidra")
        print(f"  2. Analyze with defaults")
        print(f"  3. File → Export Program → [format] → {EXPORT_PATH}")
        print(f"\nSee docs/INSTRUCTIONS.md for detailed steps.")
        return 1
    
    data = parse_listing(EXPORT_PATH)
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2))
    
    print(f"\nWrote: {OUTPUT_PATH}")
    print(f"  Functions: {len(data['functions'])}")
    print(f"  Data symbols: {len(data['data_symbols'])}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
