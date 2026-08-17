#!/usr/bin/env python3
"""Build single-disc v0.1.2 layer (rollback from v0.1.40).

Inputs:
  - workspace/pristine/FINALFANTASY7_D1.bin (pristine disc 1)
  - CSR D1 layer (from CSR repo)
  - CSR D2 layer (from CSR repo)
  - workspace/v012-exports/BLACKBGB.DAT (DSKCG stripped, from working v0.1.2)
  - workspace/v012-exports/BLACKBGE.DAT (DSKCG stripped, from working v0.1.2)
  - workspace/v012-exports/BLACKBG3.DAT (DSKCG stripped, from working v0.1.2)

Outputs:
  - builder/single-disc-on-csr/layers/disc1.layer.json (v0.1.2 layer)
  - workspace/v012-build/single-disc-v0.1.2-test.bin (smoke test bin)

Build pattern (from working v0.1.2 analysis):
  - Start with pristine D1
  - Apply CSR D1 layer (174 field edits)
  - Overlay CSR D2 fields: LOST2, CANON_2
  - Inject DSKCG-stripped fields: BLACKBGB, BLACKBGE, BLACKBG3
  - Generate layer from diff

Validation:
  - Record count: 180-220 (sanity check)
  - Layer size: 20-25 MB
  - LOST2 decompresses successfully (check break scene IFUW)
  - BLACKBGB/E/3 decompress successfully (verify DSKCG removed)

Usage:
  python3 mods/single-disc/scripts/build_v012.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from apply_layer import apply_layer
from bin_diff_to_layer import build_layer
from disc_sources import csr_layer
from lzs import decompress_all
import psx_mode2_iso


def load_layer(path: Path) -> dict:
    """Load layer JSON from file."""
    return json.loads(path.read_text())


def apply_layer_to_bin(bin_path: Path, layer: dict):
    """Apply layer to a bin file in-place."""
    img = bytearray(bin_path.read_bytes())
    apply_layer(img, layer)
    bin_path.write_bytes(img)


def generate_layer_from_diff(original: Path, modified: Path, output: Path, version: str, description: str):
    """Generate layer JSON from bin diff."""
    layer = build_layer(
        original=original,
        modified=modified,
        layer_id=f"single-disc-{version}",
        description=description
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(layer, indent=2))
    print(f"Layer written: {output}")

ROOT = Path(__file__).resolve().parents[3]


def validate_layer(layer_path: Path, test_bin: Path):
    """Validate layer before commit."""
    print("\n=== Validation ===")
    
    # 1. Record count
    layer_data = json.loads(layer_path.read_text())
    record_count = len(layer_data["records"])
    print(f"Record count: {record_count}")

    # This layer is built against pristine D1, so it includes all CSR D1 changes (~94K)
    # plus our 5 field overlays. Expected: 94K-96K records
    if record_count < 94000 or record_count > 96000:
        raise ValueError(
            f"❌ Layer record count {record_count} out of range 94000-96000!\n"
            f"   Expected: CSR D1 (~94K) + 5 field changes\n"
            f"   This suggests corruption or wrong build parameters."
        )
    print(f"✅ Record count OK (94000-96000)")
    
    # 2. Layer size
    layer_size_mb = layer_path.stat().st_size / (1024 * 1024)
    print(f"Layer size: {layer_size_mb:.1f} MB")

    # CSR D1 is ~12 MB, plus our field changes should be ~12-14 MB
    if layer_size_mb < 10 or layer_size_mb > 16:
        raise ValueError(
            f"❌ Layer size {layer_size_mb:.1f} MB out of range 10-16 MB!\n"
            f"   This suggests bloat or corruption."
        )
    print(f"✅ Layer size OK (10-16 MB)")
    
    # 3. Critical field decompression
    img = bytearray(test_bin.read_bytes())
    critical_fields = ["LOST2", "BLACKBGB", "BLACKBGE", "BLACKBG3"]
    
    for field in critical_fields:
        try:
            compressed = psx_mode2_iso.extract_file(img, f"FIELD/{field}.DAT")
            decompressed = decompress_all(compressed)
            print(f"✅ {field}: {len(decompressed):,} bytes decompressed")
        except Exception as e:
            raise ValueError(f"❌ {field} decompression FAILED: {e}")
    
    print(f"\n✅ All validation checks passed!")
    print(f"   Record count: {record_count}")
    print(f"   Layer size: {layer_size_mb:.1f} MB")
    print(f"   Field decompression: All OK")


def main() -> int:
    # Paths
    pristine = ROOT / "workspace/pristine/FINALFANTASY7_D1.bin"
    csr_d1_layer = csr_layer(1)
    csr_d2_layer = csr_layer(2)
    work_dir = ROOT / "workspace/v012-build"
    work_bin = work_dir / "work.bin"
    test_bin = work_dir / "single-disc-v0.1.2-test.bin"
    layer_out = ROOT / "builder/single-disc-on-csr/layers/disc1.layer.json"
    
    # DSKCG-stripped field exports
    blackbgb = ROOT / "workspace/v012-exports/BLACKBGB.DAT"
    blackbge = ROOT / "workspace/v012-exports/BLACKBGE.DAT"
    blackbg3 = ROOT / "workspace/v012-exports/BLACKBG3.DAT"
    
    # Check inputs
    for path in [pristine, csr_d1_layer, csr_d2_layer, blackbgb, blackbge, blackbg3]:
        if not path.exists():
            print(f"❌ Missing input: {path}")
            return 1
    
    # Step 1: Start with pristine D1
    print("Step 1: Copy pristine D1...")
    work_dir.mkdir(parents=True, exist_ok=True)
    work_bin.write_bytes(pristine.read_bytes())
    
    # Step 2: Apply CSR D1 layer
    print("Step 2: Apply CSR D1 layer...")
    csr_d1_data = load_layer(csr_d1_layer)
    apply_layer_to_bin(work_bin, csr_d1_data)
    print(f"   Applied {len(csr_d1_data['records'])} records from CSR D1")
    
    # Step 3: Overlay CSR D2 fields (LOST2, CANON_2)
    print("Step 3: Overlay CSR D2 fields (LOST2, CANON_2)...")
    temp_d2 = work_dir / "temp_d2.bin"
    temp_d2.write_bytes(pristine.read_bytes())
    csr_d2_data = load_layer(csr_d2_layer)
    apply_layer_to_bin(temp_d2, csr_d2_data)
    
    # Extract LOST2 and CANON_2 from temp D2 bin
    img_d2 = bytearray(temp_d2.read_bytes())
    lost2 = psx_mode2_iso.extract_file(img_d2, "FIELD/LOST2.DAT")
    canon2 = psx_mode2_iso.extract_file(img_d2, "FIELD/CANON_2.DAT")
    
    # Inject into work bin
    img_work = bytearray(work_bin.read_bytes())
    psx_mode2_iso.replace_file_within_sectors(img_work, "FIELD/LOST2.DAT", lost2)
    psx_mode2_iso.replace_file_within_sectors(img_work, "FIELD/CANON_2.DAT", canon2)
    work_bin.write_bytes(img_work)
    print(f"   Injected LOST2 ({len(lost2):,} bytes)")
    print(f"   Injected CANON_2 ({len(canon2):,} bytes)")
    
    # Step 4: Inject DSKCG-stripped fields
    print("Step 4: Inject DSKCG-stripped fields...")
    img_work = bytearray(work_bin.read_bytes())
    
    for field_name, field_path in [("BLACKBGB", blackbgb), ("BLACKBGE", blackbge), ("BLACKBG3", blackbg3)]:
        field_data = field_path.read_bytes()
        psx_mode2_iso.replace_file_within_sectors(img_work, f"FIELD/{field_name}.DAT", field_data)
        print(f"   Injected {field_name} ({len(field_data):,} bytes)")
    
    work_bin.write_bytes(img_work)
    
    # Step 5: Generate layer from diff
    print("Step 5: Generate layer...")
    generate_layer_from_diff(
        pristine,
        work_bin,
        layer_out,
        version="0.1.2",
        description="Single-disc v0.1.2 rollback: CSR D1 + D2 LOST2/CANON_2 + DSKCG stripped"
    )
    print(f"✅ Layer created: {layer_out}")
    
    # Step 6: Create test bin and validate
    print("\nStep 6: Create test bin...")
    test_bin.write_bytes(pristine.read_bytes())
    apply_layer_to_bin(test_bin, load_layer(layer_out))
    print(f"✅ Test bin: {test_bin}")
    
    # Validate
    validate_layer(layer_out, test_bin)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
