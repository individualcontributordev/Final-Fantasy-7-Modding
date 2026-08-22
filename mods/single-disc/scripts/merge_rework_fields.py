#!/usr/bin/env python3
"""Merge the 9 "rework" fields' CSR D1/D2 slot edits onto a CSR D1 work image,
per verdicts recorded in docs/findings/2026-08-20-slot-edit-origin.md.

6 fields are pure single-disc replacements (every differing slot's verdict
agrees with one whole disc's CSR file for that field):
  BLACKBGB, COS_BTM, COS_BTM2, DEL1, JUNAIR2 -> verdict = CSR D1, which is
           already the work image's base -- WHOLE_FILE_FIELDS omits these
           (no-op copy onto themselves) to avoid redundant writes. BLACKBGB
           is also fully replaced later anyway (DSKCG removal step).
  LOST2 -> take whole CSR D2 file (adds the `version` entity D1 lacks, and
           the missing MAPJUMP field #526 COS_BTM2 break-scene transition)
           -- the only one of the 6 that actually changes bytes on a D1 base.

3 fields have genuinely mixed per-slot verdicts (entity/slot sets are
identical between discs, so a slot-level splice is safe):
  BUGIN1A, NIVGATE, RCKTIN2 -- SLOT_SPLICE_FIELDS below omits any slot whose
  verdict is CSR D1, since the work image's base is already CSR D1 (no-op
  copy onto themselves). Only slots whose verdict is CSR D2 are listed. The
  full per-slot verdict record (including the omitted D1 slots) lives in
  docs/findings/2026-08-20-slot-edit-origin.md.

Usage (from repo root):
  python3 mods/single-disc/scripts/merge_rework_fields.py --bin work.bin --in-place
  python3 mods/single-disc/scripts/merge_rework_fields.py --bin work.bin -o out.bin
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from disc_sources import load_csr_image  # noqa: E402
from field_dat import load_field_dat  # noqa: E402
from field_dat_write import write_field_dat  # noqa: E402
from psx_mode2_iso import extract_file, replace_file_within_sectors  # noqa: E402

# Fields where the verdict table agrees with one whole CSR disc's file, AND
# that disc differs from the work image's CSR-D1 base (i.e. the merge would
# actually change bytes). BLACKBGB/COS_BTM/COS_BTM2/DEL1/JUNAIR2 all verdict
# to CSR D1 -- since the base is already CSR D1, applying them is a no-op
# copy; they're omitted here to avoid redundant work. See module docstring
# and docs/findings/2026-08-20-slot-edit-origin.md for the full 6-field
# audit record.
WHOLE_FILE_FIELDS = {
    "LOST2": 2,
}

# Fields needing true per-slot splicing: (entity, slot) -> disc, taken
# directly from docs/findings/2026-08-20-slot-edit-origin.md. Only CSR D2
# verdicts are listed -- CSR D1 verdicts are omitted since the work image's
# base is already CSR D1 (applying them would be a no-op copy onto
# themselves). See the module docstring and the findings doc for the full
# per-slot record, including the omitted D1 verdicts.
SLOT_SPLICE_FIELDS: dict[str, dict[tuple[str, int], int]] = {
    "BUGIN1A": {
        ("AD", 7): 2,
    },
    "NIVGATE": {
        ("b_drct", 1): 2,
        ("b_drct", 31): 2,
        ("cefiros", 6): 2,
        ("cefiros", 7): 2,
        ("cloud", 11): 2,
        ("cloud", 13): 2,
        ("cloud", 17): 2,
        ("hei1", 31): 2,
        ("hei2", 31): 2,
        ("tifa", 1): 2,
        ("tifa", 5): 2,
        ("tifa", 9): 2,
        ("zax", 5): 2,
    },
    "RCKTIN2": {
        ("leader", 0): 2,
    },
}


def merge_slots(img: bytearray, field: str, slot_discs: dict[tuple[str, int], int],
                 c1: bytes, c2: bytes) -> None:
    path = f"FIELD/{field}.DAT"
    base = extract_file(img, path)
    fd_base = load_field_dat(base)
    base_keys = {(s.entity, s.slot) for s in fd_base.scripts}

    fd1 = load_field_dat(extract_file(c1, path))
    fd2 = load_field_dat(extract_file(c2, path))
    d1_slots = {(s.entity, s.slot): s.raw for s in fd1.scripts}
    d2_slots = {(s.entity, s.slot): s.raw for s in fd2.scripts}

    edits: dict[tuple[str, int], bytes] = {}
    for key, disc in slot_discs.items():
        if key not in base_keys:
            raise KeyError(f"{field}: slot {key} not present in base (CSR D1) file")
        src = d1_slots if disc == 1 else d2_slots
        if key not in src:
            raise KeyError(f"{field}: slot {key} not present in CSR D{disc} file")
        edits[key] = src[key]

    new_raw = write_field_dat(fd_base, edits)
    replace_file_within_sectors(img, path, new_raw)
    print(f"  [slot-splice] {field}: {len(edits)} slots spliced, new size {len(new_raw)} bytes")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bin", type=Path, required=True, help="work image: pristine D1 + CSR D1 layer applied")
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()

    if not args.in_place and not args.output:
        raise SystemExit("pass --in-place or -o/--output")

    print("Loading CSR D1/D2 reference images...")
    c1 = bytes(load_csr_image(1))
    c2 = bytes(load_csr_image(2))

    img = bytearray(args.bin.read_bytes())

    print("\nWhole-file merges:")
    for field, disc in WHOLE_FILE_FIELDS.items():
        src = c1 if disc == 1 else c2
        path = f"FIELD/{field}.DAT"
        data = extract_file(src, path)
        replace_file_within_sectors(img, path, data)
        print(f"  {field}: replaced with CSR D{disc} ({len(data)} bytes)")

    print("\nSlot-splice merges:")
    for field, slot_discs in SLOT_SPLICE_FIELDS.items():
        merge_slots(img, field, slot_discs, c1, c2)

    out = args.bin if args.in_place else args.output
    out.write_bytes(img)
    print(f"\nWrote {out} ({len(img):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
