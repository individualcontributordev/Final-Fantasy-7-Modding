#!/usr/bin/env python3
"""Bulk-merge the "safe" (non-collision) FIELD/*.DAT CSR edits onto a CSR D1
work image.

Scope: every field present on 2+ discs where CSR only really edited it
(vs pristine) on exactly one disc, or where edits on 2+ discs are
identical/pad-only/sections-only (no genuine script rework) -- i.e.
everything scripts/scan_all_field_collisions.py classifies as "safe".
This is the complement of the 8 real collisions handled by
merge_rework_fields.py -- RCKTIN7 is also folded in here since it's a
safe D2-superset, not a genuine rework (see
docs/findings/2026-08-19-collision-mergeability.md). LOST2 also lands
here now: CSR v0.14.2 reverted D1's LOST2 to pristine and removed the
stray `version` entity, so it's a clean D2-only edit picked up
automatically by find_safe_whole_file_merges() below.

For each safe field:
  - If untouched by CSR on any disc, or already CSR D1 (the work-image
    base), nothing to do.
  - If CSR only edited it on D2 or D3, replace the D1 slot's FIELD/<X>.DAT
    with that disc's CSR file wholesale (whole-file swap, same as
    merge_rework_fields.py's WHOLE_FILE_FIELDS path). replace_file_within_
    sectors() will raise if the swap doesn't fit the D1 directory's sector
    allocation -- these are surfaced, not silently skipped.

Usage (from repo root):
  python3 mods/single-disc/scripts/merge_safe_fields.py --bin work.bin --in-place
  python3 mods/single-disc/scripts/merge_safe_fields.py --bin work.bin -o out.bin
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from disc_sources import load_csr_image, load_pristine_image  # noqa: E402
from psx_mode2_iso import extract_file, replace_file_within_sectors  # noqa: E402
from scan_all_field_collisions import list_field_dir  # noqa: E402

# RCKTIN7 is flagged as a "collision" by the naive D1-vs-D2 scripts check,
# but per docs/findings/2026-08-19-collision-mergeability.md every differing
# slot is a pure b-superset (CSR D2 is CSR D1 + insertions only) -- safe to
# take D2 wholesale, same as the true single-disc-edit fields below.
EXTRA_SAFE_WHOLE_FILE: dict[str, int] = {"RCKTIN7": 2}

# Fields fully owned by the 8-field rework merge -- must not be touched here.
REWORK_FIELDS = {
    "BLACKBGB", "BUGIN1A", "COS_BTM", "COS_BTM2", "DEL1",
    "JUNAIR2", "NIVGATE", "RCKTIN2",
}


def find_safe_whole_file_merges() -> dict[str, int]:
    """Return {field: disc} for every field CSR only really edited on one
    non-D1 disc (D2 or D3), excluding the genuine-rework fields."""
    pristine = {d: bytes(load_pristine_image(d)) for d in (1, 2, 3)}
    csr = {d: bytes(load_csr_image(d)) for d in (1, 2, 3)}
    listings = {d: list_field_dir(csr[d]) for d in (1, 2, 3)}
    all_names = sorted(set(listings[1]) | set(listings[2]) | set(listings[3]))

    out: dict[str, int] = dict(EXTRA_SAFE_WHOLE_FILE)
    for name in all_names:
        if name in REWORK_FIELDS or name in out:
            continue
        present = [d for d in (1, 2, 3) if name in listings[d]]
        if len(present) < 2:
            continue
        path = f"FIELD/{name}.DAT"
        edited = {}
        for d in present:
            data = extract_file(csr[d], path)
            try:
                pdata = extract_file(pristine[d], path)
                edited[d] = pdata != data
            except FileNotFoundError:
                edited[d] = True
        edited_discs = [d for d in present if edited[d]]
        if len(edited_discs) == 1 and edited_discs[0] != 1:
            out[name] = edited_discs[0]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bin", type=Path, required=True, help="work image: CSR D1 base + rework merge already applied")
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()

    if not args.in_place and not args.output:
        raise SystemExit("pass --in-place or -o/--output")

    print("Scanning CSR D1/D2/D3 for safe single-disc-edited fields...")
    merges = find_safe_whole_file_merges()
    print(f"Found {len(merges)} safe whole-file merges to apply.")

    print("Loading CSR D2/D3 reference images...")
    src_imgs = {2: bytes(load_csr_image(2)), 3: bytes(load_csr_image(3))}

    img = bytearray(args.bin.read_bytes())

    applied = 0
    for field, disc in sorted(merges.items()):
        path = f"FIELD/{field}.DAT"
        data = extract_file(src_imgs[disc], path)
        current = extract_file(img, path)
        if data == current:
            continue
        replace_file_within_sectors(img, path, data)
        print(f"  {field}: replaced with CSR D{disc} ({len(data)} bytes)")
        applied += 1

    out = args.bin if args.in_place else args.output
    out.write_bytes(img)
    print(f"\nApplied {applied}/{len(merges)} merges (rest already matched D1 base).")
    print(f"Wrote {out} ({len(img):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
