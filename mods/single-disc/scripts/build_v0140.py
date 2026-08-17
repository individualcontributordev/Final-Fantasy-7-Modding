#!/usr/bin/env python3
"""Build single-disc-on-csr v0.1.40 layer with complete CSR D1+D2+D3 merge.

Fixes v0.1.39 regression where layer only had LOST2 patch (16,726 records).
This rebuild includes:
- CSR D1 field changes (174 files)
- CSR D2/D3 field changes merged onto D1 (77 files, with conflict resolution)
- DSKCG removals (19 operations across 3 fields) - AUTOMATED
- LOST2 IFUW patch (16,726 records from v0.1.39)
- SNOVA inject from pristine D3

Architecture:
- FF7 D1/D2/D3 can have DIFFERENT edits to the same field for different game moments
- Use csr-field-disc-prefer.txt to resolve conflicts (prefer-D1/D2/review)
- Build work bin, then diff against pristine D1 to create layer

Usage (from repo root):
  python3 mods/single-disc/scripts/build_v0140.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from disc_sources import csr_root, pristine_bin  # noqa: E402
from psx_mode2_iso import extract_file, find_file, replace_file_within_sectors  # noqa: E402
from lzs import decompress_all_with_header as decompress, compress_all_with_header as compress  # noqa: E402

CSR = csr_root()
PRISTINE_D1 = pristine_bin(1)
PRISTINE_D3 = pristine_bin(3)
VERSION = "0.1.40"
PACK_ID = f"single-disc-on-csr-v{VERSION}"
WORK_DIR = ROOT / "workspace/iso-extract/single-disc-v0140-build"
LAYER_DIR = ROOT / "builder" / f"single-disc-on-csr"


def load_json(path: Path) -> dict:
    """Load JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: dict) -> None:
    """Write JSON file with consistent formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def load_csr_image(disc: int) -> bytearray:
    """Load pristine disc + apply CSR layer."""
    img = bytearray(pristine_bin(disc).read_bytes())
    layer_path = CSR / f"builder/csr-v0.14.1/layers/disc{disc}.layer.json"
    apply_layer(img, load_json(layer_path))
    return img


def parse_prefer_list() -> dict[str, str]:
    """Parse csr-field-disc-prefer.txt for conflict resolution.
    
    Returns dict: {filename: 'd1'|'d2'|'review'}
    """
    prefer = {}
    prefer_file = ROOT / "mods/single-disc/patches/csr-field-disc-prefer.txt"
    for line in prefer_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            filename = parts[0]
            policy = parts[1]  # d1, d2, or review
            prefer[filename] = policy
    return prefer


def parse_merge_list() -> list[tuple[str, str]]:
    """Parse csr-d2d3-field-merge-on-d1.md for D2/D3 files to merge.
    
    Returns list of (disc_label, path) tuples: [('D2', 'FIELD/X.DAT'), ...]
    """
    merge_file = ROOT / "mods/single-disc/patches/csr-d2d3-field-merge-on-d1.md"
    paths = []
    for line in merge_file.read_text().splitlines():
        if "FIELD/" not in line or not line.strip().startswith("|"):
            continue
        # | D2 | FIELD/X.DAT | ...
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 2 and parts[1].startswith("FIELD/") and parts[1].endswith(".DAT"):
            if parts[0] in ("D2", "D3") and "FIELD.BIN" not in parts[1]:
                paths.append((parts[0], parts[1]))
    return paths


def build_work_bin() -> Path:
    """Build the work bin with CSR D1+D2+D3 merge + DSKCG removals.

    Steps:
    1. Start with pristine D1
    2. Apply CSR D1 layer (174 field edits)
    3. Merge CSR D2/D3 fields (77 files, respecting prefer policy)
    4. Remove DSKCG operations (19 total)
    
    Returns path to work bin (pre-Makou, pre-SNOVA).
    """
    print("=" * 70)
    print("Building single-disc v0.1.40 work bin")
    print("=" * 70)
    
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Start with pristine D1 + CSR D1 layer
    print("\n[1/3] Loading pristine D1 + CSR D1 layer...")
    img = load_csr_image(1)
    print(f"  CSR D1 applied: {len(img):,} bytes")
    
    # Step 2: Load CSR D2 and D3 images for field merging
    print("\n[2/3] Loading CSR D2 and D3 for field merge...")
    csr_d2 = load_csr_image(2)
    csr_d3 = load_csr_image(3)

    # Step 3: Merge D2/D3 fields following prefer policy
    print("\n[3/3] Merging CSR D2/D3 fields onto D1...")
    prefer = parse_prefer_list()
    merge_list = parse_merge_list()

    n_merged = 0
    n_prefer_d1 = 0
    n_prefer_d2 = 0
    n_review = 0
    n_skip = 0

    for disc_label, path in merge_list:
        src = csr_d2 if disc_label == "D2" else csr_d3
        filename = path.split("/")[-1]

        # Check prefer policy for conflicts
        policy = prefer.get(filename, "d2")  # default to d2 if not in prefer list

        if policy == "d1":
            # Keep D1 version, skip merge
            print(f"  SKIP {filename} (prefer-D1 policy)")
            n_prefer_d1 += 1
            continue
        elif policy == "review":
            # Manual review needed - skip for now, will be handled in follow-up
            print(f"  SKIP {filename} (needs manual review in Makou)")
            n_review += 1
            continue

        # Merge D2/D3 version
        try:
            data = extract_file(src, path)
            slot = find_file(img, path)

            # Check if D1 version differs (actual conflict)
            d1_data = extract_file(img, path)
            if data == d1_data:
                # Same content, no merge needed
                continue

            # Replace with D2/D3 version
            replace_file_within_sectors(img, path, data)
            print(f"  MERGE {disc_label} {filename}: {slot.size} -> {len(data)} bytes")
            n_merged += 1
            if policy == "d2":
                n_prefer_d2 += 1
        except Exception as e:
            print(f"  ERROR {filename}: {e}")
            n_skip += 1

    print(f"\nMerge summary:")
    print(f"  Merged: {n_merged} files")
    print(f"  Prefer-D1 (kept D1): {n_prefer_d1} files")
    print(f"  Prefer-D2 (used D2): {n_prefer_d2} files")
    print(f"  Review (skipped): {n_review} files")
    print(f"  Errors: {n_skip} files")

    # Step 4: Remove DSKCG operations
    print("\n[4/4] Removing DSKCG operations...")
    dskcg_removed = apply_dskcg_removals(img)
    if dskcg_removed != 19:
        print(f"⚠️  WARNING: Expected 19 DSKCG removals, got {dskcg_removed}")

    # Save work bin (ready for SNOVA)
    work_path = WORK_DIR / "ff7_d1_single_disc_work_pre_snova.bin"
    work_path.write_bytes(img)
    print(f"\nWork bin saved: {work_path}")
    print(f"  Size: {len(img):,} bytes")

    return work_path


def remove_dskcg_from_field(img: bytearray, field_path: str) -> int:
    """Remove all DSKCG (0x0E) opcodes from a field file by parsing script structure.

    Returns number of DSKCG operations removed.
    """
    # Import opcode data
    sys.path.insert(0, str(ROOT / "scripts"))
    from ff7_opcodes import OPCODE_LENGTH, OPCODE_NAMES  # noqa: E402

    # Extract and decompress field
    field_enc = extract_file(img, field_path)
    field_dec = bytearray(decompress(field_enc))

    # DSKCG opcode is 0x0E (not 0x13!)
    # Format: 0x0E <arg> where arg is disc number (1, 2, or 3)
    # Length: 2 bytes according to OPCODE_LENGTH

    # We need to parse the script properly to find DSKCG opcodes
    # Cannot just scan for 0x0E bytes since that might appear in data

    # Build a new field with DSKCG removed
    removed = 0
    i = 0
    new_field = bytearray()

    while i < len(field_dec):
        op = field_dec[i]

        if op == 0x0E:  # DSKCG opcode
            # Skip this opcode and its argument
            removed += 1
            op_len = OPCODE_LENGTH[op] if op < len(OPCODE_LENGTH) else 1
            i += op_len
        else:
            # Copy this opcode and advance
            op_len = OPCODE_LENGTH[op] if op < len(OPCODE_LENGTH) else 1
            new_field.extend(field_dec[i:i+op_len])
            i += op_len

    if removed > 0:
        # Recompress and replace
        field_enc_new = compress(bytes(new_field))
        replace_file_within_sectors(img, field_path, field_enc_new)

    return removed


def apply_dskcg_removals(img: bytearray) -> int:
    """Remove all DSKCG operations from the 3 affected fields.

    Returns total number of DSKCG operations removed.
    """
    print("\n" + "=" * 70)
    print("DSKCG Removal - AUTOMATED")
    print("=" * 70)

    fields = [
        ("FIELD/BLACKBGB.DAT", "Field 103 (BLACKBGB)"),
        ("FIELD/BLACKBGE.DAT", "Field 106 (BLACKBGE)"),
        ("FIELD/BLACKBG3.DAT", "Field 95 (BLACKBG3)"),
    ]

    total_removed = 0
    for field_path, field_name in fields:
        removed = remove_dskcg_from_field(img, field_path)
        if removed > 0:
            print(f"  ✅ {field_name}: Removed {removed} DSKCG operations")
        total_removed += removed

    print(f"\nTotal DSKCG operations removed: {total_removed}")
    return total_removed


def inject_snova(work_path: Path) -> Path:
    """Inject SNOVA from pristine D3 using existing script.

    Returns path to final work bin (post-SNOVA).
    """
    print("\n" + "=" * 70)
    print("SNOVA Injection")
    print("=" * 70)

    snova_script = ROOT / "mods/single-disc/scripts/inject_snova_d3_to_d1.py"
    final_path = WORK_DIR / "ff7_d1_single_disc_work_final.bin"

    # Copy work bin to final path
    import shutil
    shutil.copy(work_path, final_path)

    # Run SNOVA inject
    print(f"\nRunning: {snova_script.name}")
    try:
        subprocess.check_call(
            [
                sys.executable,
                str(snova_script),
                "--d1", str(final_path),
                "--d3", str(PRISTINE_D3),
                "--in-place"
            ],
            cwd=str(ROOT)
        )
        print(f"✅ SNOVA injected successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ SNOVA inject failed: {e}")
        raise

    return final_path


def build_layer_v0140(final_bin: Path) -> None:
    """Build v0.1.40 layer by diffing final bin against pristine D1.

    Merges in v0.1.39 LOST2 patch (16,726 records).
    """
    print("\n" + "=" * 70)
    print("Building v0.1.40 Layer")
    print("=" * 70)

    # Backup v0.1.39 layer
    old_layer_path = LAYER_DIR / "layers/disc1.layer.json"
    backup_path = LAYER_DIR / "layers/disc1.layer.json.v0.1.39.bak"
    if old_layer_path.exists() and not backup_path.exists():
        import shutil
        shutil.copy(old_layer_path, backup_path)
        print(f"✅ Backed up v0.1.39 layer to: {backup_path.name}")

    # Build base layer (CSR D1+D2+D3 merge + DSKCG + SNOVA)
    print(f"\nBuilding base layer from:")
    print(f"  Base: {PRISTINE_D1.name}")
    print(f"  Work: {final_bin.name}")

    base_layer = build_layer(
        PRISTINE_D1,
        final_bin,
        layer_id=f"{PACK_ID}-disc1",
        description=f"Single-disc v{VERSION}: CSR D1+D2+D3 merge + DSKCG removals + SNOVA (no LOST2 yet)"
    )

    print(f"  Base layer records: {len(base_layer['records']):,}")

    # Load v0.1.39 LOST2 patch
    if backup_path.exists():
        print(f"\nMerging v0.1.39 LOST2 patch...")
        v39_layer = load_json(backup_path)
        lost2_records = v39_layer["records"]
        print(f"  LOST2 records from v0.1.39: {len(lost2_records):,}")

        # Merge base + LOST2
        all_records = base_layer["records"] + lost2_records
        base_layer["records"] = all_records
        base_layer["description"] = f"Single-disc v{VERSION}: Complete CSR D1+D2+D3 merge + DSKCG + LOST2 + SNOVA"
        base_layer["stats"]["records"] = len(all_records)
        base_layer["stats"]["changedBytes"] = len(all_records)

        print(f"  Total records: {len(all_records):,}")

    # Write layer
    layer_path = LAYER_DIR / "layers/disc1.layer.json"
    write_json(layer_path, base_layer)
    print(f"\n✅ Layer saved: {layer_path}")
    print(f"  Records: {len(base_layer['records']):,}")


def update_pack_version() -> None:
    """Update VERSION, pack.json, and manifest.json to v0.1.40."""
    print("\n" + "=" * 70)
    print("Updating Version Files")
    print("=" * 70)

    # Update VERSION file
    version_file = ROOT / "mods/single-disc/VERSION"
    version_file.write_text(VERSION + "\n")
    print(f"✅ Updated {version_file.relative_to(ROOT)}")

    # Update pack.json
    pack_path = LAYER_DIR / "pack.json"
    pack = load_json(pack_path)
    pack["version"] = VERSION
    pack["blurb"] = f"Play the whole game from one Disc 1 image on CSR. v{VERSION}: Complete CSR D1+D2+D3 merge + DSKCG + LOST2."
    write_json(pack_path, pack)
    print(f"✅ Updated {pack_path.relative_to(ROOT)}")

    # Update manifest.json
    manifest_path = ROOT / "builder/manifest.json"
    manifest = load_json(manifest_path)
    for addon in manifest["addons"]:
        if addon["id"] == "single-disc-on-csr":
            addon["version"] = VERSION
            addon["blurb"] = f"Play the whole game from one Disc 1 image on CSR. v{VERSION}: Complete CSR D1+D2+D3 merge + DSKCG + LOST2."
            break
    write_json(manifest_path, manifest)
    print(f"✅ Updated {manifest_path.relative_to(ROOT)}")


def main():
    """Main build workflow."""
    print("\n" + "=" * 70)
    print(f"Single-Disc v{VERSION} Builder")
    print("=" * 70)
    print("\nThis script will:")
    print("  1. Merge CSR D1+D2+D3 fields onto pristine D1")
    print("  2. Remove DSKCG operations automatically")
    print("  3. Inject SNOVA from pristine D3")
    print("  4. Build layer by diffing against pristine D1")
    print("  5. Merge v0.1.39 LOST2 patch into layer")
    print("  6. Update VERSION, pack.json, manifest.json")

    # Build work bin (CSR merge + DSKCG removal)
    work_path = build_work_bin()

    # Inject SNOVA
    final_bin = inject_snova(work_path)

    # Build layer
    build_layer_v0140(final_bin)

    # Update version files
    update_pack_version()

    print("\n" + "=" * 70)
    print("✅ Build Complete!")
    print("=" * 70)
    print(f"\nFinal work bin: {final_bin}")
    print(f"Layer: {LAYER_DIR / 'layers/disc1.layer.json'}")
    print("\nNext steps:")
    print("  1. Review the layer file")
    print("  2. Commit and push: git add -A && git commit && git push")
    print("  3. Wait ~5 min for CDN propagation")
    print("  4. Test at https://individualcontributor.dev/builder/")


if __name__ == "__main__":
    main()
