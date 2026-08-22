#!/usr/bin/env python3
"""Build the merged single-disc-on-csr work bin (rebuild-from-scratch pipeline).

Pipeline, on top of CSR D1 as the base:
  1. Apply the 66-slot verdict-table merge for the 9 "rework" fields
     (BLACKBGB, BUGIN1A, COS_BTM, COS_BTM2, DEL1, JUNAIR2, LOST2, NIVGATE,
     RCKTIN2) via merge_rework_fields.py's logic.
  2. Apply the bulk "safe" field merge -- every other CSR field edited on
     only one non-D1 disc (plus RCKTIN7, a safe D2-superset) -- via
     merge_safe_fields.py.
  3. Replace BLACKBGB/BLACKBGE/BLACKBG3 with the pre-exported,
     DSKCG-stripped fields from workspace/v012-exports/ (proven working
     in v0.1.2). The live remove_dskcg.py splicer produces a field that
     diverges from the proven file by ~12k bytes after decompression
     (see docs/findings/) and causes a black-screen hang at the D1->D2
     transition, so it is no longer used for these three fields.
  4. Patch FIELD.BIN's/WORLD.BIN's embedded (location,size) lookup table
     for every field resized by steps 1-3, via fix_field_bin_table.py --
     without this, ff7tk (Makou Reactor) fails ANY save of the built bin
     with "Cannot update game binaries" (InvalidError), because its
     unconditional reorganizeModifiedFilesAfter() searches FIELD.BIN for
     each field's current directory-record size and finds the stale one.
  5. Inject SNOVA from pristine D3 onto D1 + remap BATTLE.X hardcoded LBAs
     via inject_snova_d3_to_d1.py.

This produces the merged single-disc-on-csr work .bin -- NOT a final release
layer (still needs diffing into disc1.layer.json via bin_diff_to_layer.py).

Usage (from repo root):
  python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-work.bin
  python3 mods/single-disc/scripts/build_work_bin.py -o OUT.bin --skip-snova
  python3 mods/single-disc/scripts/build_work_bin.py -o OUT.bin --d2-only-fields
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
from fix_field_bin_table import fix_field_and_world_bins  # noqa: E402

DSKCG_FIELDS = ["BLACKBGB", "BLACKBGE", "BLACKBG3"]
V012_EXPORTS_DIR = ROOT / "workspace" / "v012-exports"


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


def apply_safe_field_merge(img: bytearray, d2_only: bool = False) -> int:
    label = "D2-only" if d2_only else "D2/D3"
    print(f"\nApplying bulk safe-field merge (non-collision {label} edits)...")
    merges = find_safe_whole_file_merges()
    if d2_only:
        merges = {f: d for f, d in merges.items() if d == 2}
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


def apply_dskcg_removal(img: bytearray, fields: list[str] | None = None) -> int:
    fields = DSKCG_FIELDS if fields is None else fields
    print(f"\nInjecting pre-exported DSKCG-stripped fields (proven v0.1.2) for {fields}...")
    total = 0
    for field in fields:
        path = f"FIELD/{field}.DAT"
        export_path = V012_EXPORTS_DIR / f"{field}.DAT"
        new_raw = export_path.read_bytes()
        current = extract_file(img, path)
        if new_raw != current:
            replace_file_within_sectors(img, path, new_raw)
            total += 1
        print(f"  {field}: injected from {export_path.relative_to(ROOT)} ({len(new_raw)} bytes)")
    print(f"  Total fields replaced: {total}")
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
    ap.add_argument("--d2-only-fields", action="store_true",
                     help="safe-field merge: only apply CSR D2 fields, skip D3 fields entirely "
                          "(isolation test for D1->D2 transition regression)")
    ap.add_argument("--blackbgb-only-dskcg", action="store_true",
                     help="only strip DSKCG from BLACKBGB (skip BLACKBGE/BLACKBG3) -- "
                          "further isolation of the D1->D2 break-scene regression")
    args = ap.parse_args()

    print("Loading CSR D1/D2 reference images...")
    c1 = bytes(load_csr_image(1))
    c2 = bytes(load_csr_image(2))

    img = bytearray(c1)
    print(f"Base: CSR D1 ({len(img):,} bytes)")

    apply_rework_merge(img, c1, c2)
    apply_safe_field_merge(img, d2_only=args.d2_only_fields)
    dskcg_fields = ["BLACKBGB"] if args.blackbgb_only_dskcg else None
    apply_dskcg_removal(img, fields=dskcg_fields)

    print("\nPatching FIELD.BIN/WORLD.BIN embedded (location,size) tables...")
    fixed = fix_field_and_world_bins(img)
    print(f"  Total table entries patched: {fixed}")

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
