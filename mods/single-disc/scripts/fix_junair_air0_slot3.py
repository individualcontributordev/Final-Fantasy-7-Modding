#!/usr/bin/env python3
"""Apply CSR's D2-only JUNAIR (field 384, Junon airfield) script fix as a
precision slot edit instead of swapping the whole FIELD/JUNAIR.DAT file.

Root cause context: merge_safe_fields.py's auto-detector previously took
CSR D2's JUNAIR.DAT wholesale because CSR only edited this field on D2 (D1's
copy matches pristine). But the only actual delta between CSR D1 and CSR D2
JUNAIR.DAT is a single script slot, `air0`/3 -- CSR added an AKAO/PRTYE/
PRTYE/MMBLK/BITON block ahead of the original MAPJUMP/RET tail (see
docs/findings/2026-08-26-junair-single-disc-battle-return-freeze.md).
Swapping the whole file was implicated as a possible culprit in the
battle-return freeze investigation; this script isolates the change to
exactly the bytes CSR actually touched, same technique as
fix_white2_movie_hang.py.

Usage:
  python3 mods/single-disc/scripts/fix_junair_air0_slot3.py \\
    --bin workspace/iso-extract/work.bin --in-place
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from field_dat import load_field_dat  # noqa: E402
from field_dat_write import write_field_dat  # noqa: E402
from psx_mode2_iso import extract_file, replace_file_within_sectors  # noqa: E402

FIELD = "FIELD/JUNAIR.DAT"

ENTITY, SLOT = "air0", 3
# CSR D1 / pristine D1+D2 (air0,3): IFSW.., MAPJUMP, RET
SLOT_ORIGINAL = bytes.fromhex("16200000f803050b60810111f1f6fb41000000")
# CSR D2 (air0,3): IFSW.., AKAO, PRTYE, PRTYE, MMBLK, BITON, MAPJUMP, MAPJUMP, RET
SLOT_PATCHED = bytes.fromhex(
    "16200000f8030531f2000000c1780000000000000000cafefefeca02fefece"
    "028210e206609201b000250001008060810111f1f6fb41000000"
)


def _fix_slot(fd) -> dict:
    slot = next((s for s in fd.scripts if s.entity == ENTITY and s.slot == SLOT), None)
    if slot is None:
        raise SystemExit(f"{FIELD}: no {ENTITY}/{SLOT} script slot found")
    if slot.raw == SLOT_PATCHED:
        print(f"  {ENTITY}/{SLOT} already patched, nothing to do")
        return {}
    if slot.raw != SLOT_ORIGINAL:
        raise SystemExit(
            f"{FIELD} {ENTITY}/{SLOT}: unexpected script bytes {slot.raw.hex()}, "
            f"expected {SLOT_ORIGINAL.hex()}"
        )
    print(f"  {FIELD} {ENTITY}/{SLOT}: applied CSR D2 fix "
          f"({len(SLOT_ORIGINAL)} -> {len(SLOT_PATCHED)} bytes)")
    return {(ENTITY, SLOT): SLOT_PATCHED}


def fix_junair(img: bytearray) -> bool:
    raw = extract_file(bytes(img), FIELD)
    fd = load_field_dat(raw)

    edits = _fix_slot(fd)
    if not edits:
        return False

    new_raw = write_field_dat(fd, edits)
    fd2 = load_field_dat(new_raw)
    for (entity, slot_idx), expected in edits.items():
        new_slot = next(s for s in fd2.scripts if s.entity == entity and s.slot == slot_idx)
        if new_slot.raw != expected:
            raise SystemExit(f"post-write verification failed: {entity}/{slot_idx} not patched as expected")
    replace_file_within_sectors(img, FIELD, new_raw)
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bin", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()
    if not args.in_place and not args.output:
        raise SystemExit("pass --in-place or -o/--output")

    img = bytearray(args.bin.read_bytes())
    print("Applying CSR JUNAIR air0/3 fix (field 384, Junon airfield)...")
    fix_junair(img)

    out = args.bin if args.in_place else args.output
    out.write_bytes(img)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
