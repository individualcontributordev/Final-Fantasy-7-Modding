#!/usr/bin/env python3
"""Build the merged single-disc-on-csr work bin (rebuild-from-scratch pipeline).

Pipeline, on top of CSR D1 as the base:
  1. Apply the verdict-table merge for the 8 "rework" fields (BLACKBGB,
     BUGIN1A, COS_BTM, COS_BTM2, DEL1, JUNAIR2, NIVGATE, RCKTIN2) via
     merge_rework_fields.py's logic. All 5 whole-file verdicts (BLACKBGB,
     COS_BTM, COS_BTM2, DEL1, JUNAIR2) resolve to CSR D1 -- already the
     base -- so WHOLE_FILE_FIELDS is empty and those are skipped as no-ops.
     Likewise, the 3 slot-spliced fields (BUGIN1A, NIVGATE, RCKTIN2) only
     list slots whose verdict is CSR D2 -- slots verdicted CSR D1 are
     omitted as no-ops.
  2. Apply the bulk "safe" field merge -- every other CSR field edited on
     only one non-D1 disc (plus RCKTIN7, a safe D2-superset; LOST2 also
     lands here now that CSR D1's LOST2 matches pristine) -- via
     merge_safe_fields.py.
  3. Strip DSKCG (ask-for-disc) ops from BLACKBGB via remove_dskcg.py's
     live opcode splicer (parses scripts, removes 0x0E ops, fixes up
     JMPF/JMPFL/JMPB/JMPBL/IFxx jump targets). This is a pure DSKCG
     removal only -- untested against the D1->D2 transition as of this
     pipeline revision; see docs/findings/ for prior hang reports on an
     earlier version of this step and 2026-08-2x findings for the
     current verification status. BLACKBGE/BLACKBG3 are unused maps
     with no MAPJUMP references from any other field (confirmed in
     Makou Reactor) and are left untouched.
  4. (optional, --apply-table-fix) Patch FIELD.BIN's/WORLD.BIN's embedded
     (location,size) lookup table for every field resized by steps 1-3,
     via fix_field_bin_table.py -- intended to let ff7tk (Makou Reactor)
     save the built bin without "Cannot update game binaries"
     (InvalidError). NOTE: this has not reliably fixed the InvalidError
     in all cases, so it is now opt-in rather than a default step,
     pending further testing.
  5. Inject SNOVA from pristine D3 onto D1 + remap BATTLE.X hardcoded LBAs
     via inject_snova_d3_to_d1.py.

This produces the merged single-disc-on-csr work .bin -- NOT a final release
layer (still needs diffing into disc1.layer.json via bin_diff_to_layer.py).

Usage (from repo root):
  python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-work.bin
  python3 mods/single-disc/scripts/build_work_bin.py -o OUT.bin --skip-snova
  python3 mods/single-disc/scripts/build_work_bin.py -o OUT.bin --d2-only-fields
  python3 mods/single-disc/scripts/build_work_bin.py -o OUT.bin --apply-table-fix
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
from remove_dskcg import remove_dskcg_from_field  # noqa: E402

DSKCG_FIELDS = ["BLACKBGB"]


def apply_rework_merge(img: bytearray, c1: bytes, c2: bytes) -> None:
    print("\nApplying 8-field rework merge (verdict table)...")
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


def apply_dskcg_removal(
    img: bytearray, fields: list[str] | None = None, only_indices: set[int] | None = None
) -> int:
    fields = DSKCG_FIELDS if fields is None else fields
    suffix = f" (only occurrence(s) {sorted(only_indices)})" if only_indices is not None else ""
    print(f"\nRemoving DSKCG (ask-for-disc) ops via live splicer for {fields}{suffix}...")
    total = 0
    for field in fields:
        path = f"FIELD/{field}.DAT"
        current = extract_file(img, path)
        new_raw, removed = remove_dskcg_from_field(current, field, only_indices)
        if removed > 0:
            replace_file_within_sectors(img, path, new_raw)
            total += 1
        print(f"  {field}: removed {removed} DSKCG ({len(new_raw)} bytes)")
    print(f"  Total fields modified: {total}")
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
    ap.add_argument("--apply-table-fix", action="store_true",
                     help="patch FIELD.BIN/WORLD.BIN (location,size) tables after merging "
                          "(opt-in: has not reliably fixed Makou Reactor's InvalidError in "
                          "all cases, kept available for testing)")
    ap.add_argument("--skip-dskcg-removal", action="store_true",
                     help="skip stripping DSKCG (ask-for-disc) ops from BLACKBGB "
                          "(isolation test for D1->D2 transition black-screen hang)")
    args = ap.parse_args()

    print("Loading CSR D1/D2 reference images...")
    c1 = bytes(load_csr_image(1))
    c2 = bytes(load_csr_image(2))

    img = bytearray(c1)
    print(f"Base: CSR D1 ({len(img):,} bytes)")

    apply_rework_merge(img, c1, c2)
    apply_safe_field_merge(img, d2_only=args.d2_only_fields)
    if args.skip_dskcg_removal:
        print("\nSkipping DSKCG removal (--skip-dskcg-removal)")
    else:
        # Only remove the single DSKCG on the actual D1->D2 execution path
        # (occurrence index 0 in BLACKBGB's init slot 0), matching the
        # manual Makou Reactor edit confirmed to work. Removing all 4 (the
        # old default) is known to hang/corrupt the field.
        apply_dskcg_removal(img, only_indices={0})

    if args.apply_table_fix:
        print("\nPatching FIELD.BIN/WORLD.BIN embedded (location,size) tables...")
        fixed = fix_field_and_world_bins(img)
        print(f"  Total table entries patched: {fixed}")
    else:
        print("\nSkipping FIELD.BIN/WORLD.BIN table patch (opt-in via --apply-table-fix)")

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
