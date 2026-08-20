#!/usr/bin/env python3
"""Build the merged single-disc-on-csr work bin (rebuild-from-scratch pipeline).

Pipeline, on top of CSR D1 as the base:
  1. Apply the 66-slot verdict-table merge for the 9 "rework" fields
     (BLACKBGB, BUGIN1A, COS_BTM, COS_BTM2, DEL1, JUNAIR2, LOST2, NIVGATE,
     RCKTIN2) via merge_rework_fields.py's logic.
  2. Apply the bulk "safe" field merge -- every other CSR field edited on
     only one non-D1 disc (plus RCKTIN7, a safe D2-superset) -- via
     merge_safe_fields.py.
  3. Remove DSKCG ("Ask for disc") ops from BLACKBGB/BLACKBGE/BLACKBG3
     (expect 19 total: 4 + 1 + 14) via remove_dskcg.py's splicer.
  4. Inject SNOVA from pristine D3 onto D1 + remap BATTLE.X hardcoded LBAs
     via inject_snova_d3_to_d1.py.

This produces the merged single-disc-on-csr work .bin -- NOT a final release
layer (still needs diffing into disc1.layer.json via bin_diff_to_layer.py).

Usage (from repo root):
  python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-work.bin
  python3 mods/single-disc/scripts/build_work_bin.py -o OUT.bin --skip-snova
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from disc_sources import load_csr_image, pristine_bin  # noqa: E402
from psx_mode2_iso import extract_file, replace_file_within_sectors  # noqa: E402

from merge_rework_fields import (  # noqa: E402
    SLOT_SPLICE_FIELDS,
    WHOLE_FILE_FIELDS,
    merge_slots,
)
from merge_safe_fields import find_safe_whole_file_merges  # noqa: E402
from remove_dskcg import remove_dskcg_from_field  # noqa: E402

DSKCG_FIELDS = ["BLACKBGB", "BLACKBGE", "BLACKBG3"]
EXPECTED_DSKCG_TOTAL = 19


def apply_rework_merge(img: bytearray, c1: bytes, c2: bytes) -> None:
    print("\nApplying 9-field rework merge (verdict table)...")
    for field, disc in WHOLE_FILE_FIELDS.items():
        src = c1 if disc == 1 else c2
        path = f"FIELD/{field}.DAT"
        data = extract_file(src, path)
        replace_file_within_sectors(img, path, data)
        print(f"  [whole-file] {field}: CSR D{disc} ({len(data)} bytes)")
    for field, slot_discs in SLOT_SPLICE_FIELDS.items():
        merge_slots(img, field, slot_discs, c1, c2)


def apply_safe_field_merge(img: bytearray) -> int:
    print("\nApplying bulk safe-field merge (non-collision D2/D3 edits)...")
    merges = find_safe_whole_file_merges()
    src_imgs = {2: bytes(load_csr_image(2)), 3: bytes(load_csr_image(3))}
    applied = 0
    for field, disc in sorted(merges.items()):
        path = f"FIELD/{field}.DAT"
        data = extract_file(src_imgs[disc], path)
        current = extract_file(img, path)
        if data == current:
            continue
        replace_file_within_sectors(img, path, data)
        applied += 1
    print(f"  Applied {applied}/{len(merges)} safe field merges")
    return applied


def apply_dskcg_removal(img: bytearray) -> int:
    print("\nRemoving DSKCG ('Ask for disc') ops...")
    total = 0
    for field in DSKCG_FIELDS:
        path = f"FIELD/{field}.DAT"
        raw = extract_file(img, path)
        new_raw, removed = remove_dskcg_from_field(raw, field)
        if removed:
            replace_file_within_sectors(img, path, new_raw)
        print(f"  {field}: removed {removed}")
        total += removed
    print(f"  Total DSKCG removed: {total}")
    if total != EXPECTED_DSKCG_TOTAL:
        print(f"  WARNING: expected {EXPECTED_DSKCG_TOTAL} total, got {total}")
    return total


def inject_snova(work_bin: Path) -> None:
    print("\nInjecting SNOVA D3 -> D1...")
    d3 = pristine_bin(3)
    snova_script = Path(__file__).resolve().parent / "inject_snova_d3_to_d1.py"
    subprocess.check_call(
        [sys.executable, str(snova_script), "--d1", str(work_bin), "--d3", str(d3), "--in-place"],
        cwd=str(ROOT),
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--skip-snova", action="store_true", help="skip SNOVA D3->D1 inject step")
    args = ap.parse_args()

    print("Loading CSR D1/D2 reference images...")
    c1 = bytes(load_csr_image(1))
    c2 = bytes(load_csr_image(2))

    img = bytearray(c1)
    print(f"Base: CSR D1 ({len(img):,} bytes)")

    apply_rework_merge(img, c1, c2)
    apply_safe_field_merge(img)
    apply_dskcg_removal(img)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(img)
    print(f"\nWrote {args.output} ({len(img):,} bytes) [pre-SNOVA]")

    if args.skip_snova:
        print("Skipping SNOVA inject (--skip-snova)")
        return 0

    inject_snova(args.output)
    print(f"\nDone. Final work bin: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
