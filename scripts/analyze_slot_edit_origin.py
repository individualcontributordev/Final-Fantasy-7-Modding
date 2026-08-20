#!/usr/bin/env python3
"""Per-slot pristine-anchored edit-origin check for the 9 'rework' field
collisions (all except RCKTIN7, which is already known-safe auto-merge).

For every differing slot (per docs/findings/2026-08-19-collision-mergeability.md),
compare each disc's CSR script for that exact slot against that same disc's
PRISTINE script for that slot. This tells us, per slot, whether:

  - only D1 was actually edited by CSR (D2 CSR == D2 pristine there)
  - only D2 was actually edited by CSR (D1 CSR == D1 pristine there)
  - both sides were edited by CSR (independently, at that slot)
  - neither matches pristine cleanly (slot missing on one pristine disc, etc.)

This is the correct way to judge intent -- NOT "which side differs from
pristine in general" but "which side did CSR's own edit actually touch,
for this specific slot".

Usage:
  python3 scripts/analyze_slot_edit_origin.py -o /tmp/slot_origin.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from disc_sources import load_csr_image, load_pristine_image  # noqa: E402
from field_dat import load_field_dat  # noqa: E402
from psx_mode2_iso import extract_file  # noqa: E402

# (field, entity, slot) list pulled from the mergeability doc, excluding RCKTIN7.
SLOTS = [
    ("BLACKBGB", "init", 0),
    ("BUGIN1A", "AD", 4),
    ("BUGIN1A", "AD", 7),
    ("BUGIN1A", "BUGEN", 1),
    ("COS_BTM", "BUGEN", 3),
    ("COS_BTM", "BUGEN", 31),
    ("COS_BTM", "MES", 31),
    ("COS_BTM2", "AD", 0),
    ("COS_BTM2", "BALLET", 1),
    ("COS_BTM2", "BALLET", 6),
    ("COS_BTM2", "BALLET", 7),
    ("COS_BTM2", "BUGEN", 3),
    ("COS_BTM2", "CLOUD", 22),
    ("COS_BTM2", "EARITH", 1),
    ("COS_BTM2", "EARITH", 7),
    ("COS_BTM2", "EARITH", 30),
    ("COS_BTM2", "KETCY", 6),
    ("COS_BTM2", "RED", 1),
    ("COS_BTM2", "TIFA", 1),
    ("COS_BTM2", "TIFA", 8),
    ("COS_BTM2", "YUFI", 8),
    ("DEL1", "border1", 2),
    ("DEL1", "crew2", 3),
    ("DEL1", "earith", 7),
    ("DEL1", "tifa", 7),
    ("DEL1", "yufi", 31),
    ("JUNAIR2", "dir", 0),
    ("LOST2", "Info", 4),
    ("LOST2", "ballet", 3),
    ("LOST2", "ballet", 5),
    ("LOST2", "cefir", 31),
    ("LOST2", "cid", 3),
    ("LOST2", "cid", 5),
    ("LOST2", "cloud", 7),
    ("LOST2", "cloud", 31),
    ("LOST2", "init", 0),
    ("LOST2", "ketcy", 3),
    ("LOST2", "ketcy", 5),
    ("LOST2", "line", 3),
    ("LOST2", "red13", 3),
    ("LOST2", "red13", 5),
    ("LOST2", "tifa", 3),
    ("LOST2", "tifa", 5),
    ("LOST2", "version", 0),
    ("LOST2", "version", 31),
    ("LOST2", "vincent", 3),
    ("LOST2", "vincent", 5),
    ("LOST2", "yufi", 3),
    ("LOST2", "yufi", 5),
    ("NIVGATE", "b_drct", 1),
    ("NIVGATE", "b_drct", 31),
    ("NIVGATE", "cefiros", 3),
    ("NIVGATE", "cefiros", 6),
    ("NIVGATE", "cefiros", 7),
    ("NIVGATE", "cloud", 3),
    ("NIVGATE", "cloud", 11),
    ("NIVGATE", "cloud", 13),
    ("NIVGATE", "cloud", 17),
    ("NIVGATE", "hei1", 3),
    ("NIVGATE", "hei1", 31),
    ("NIVGATE", "hei2", 3),
    ("NIVGATE", "hei2", 31),
    ("NIVGATE", "line_jp", 2),
    ("NIVGATE", "tifa", 1),
    ("NIVGATE", "tifa", 5),
    ("NIVGATE", "tifa", 9),
    ("NIVGATE", "zax", 5),
    ("RCKTIN2", "cid", 1),
    ("RCKTIN2", "leader", 0),
]


def slot_map(dat_bytes: bytes) -> dict[tuple[str, int], bytes]:
    fd = load_field_dat(dat_bytes)
    return {(s.entity, s.slot): s.raw for s in fd.scripts}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    p1 = bytes(load_pristine_image(1))
    p2 = bytes(load_pristine_image(2))
    c1 = bytes(load_csr_image(1))
    c2 = bytes(load_csr_image(2))

    field_cache: dict[str, tuple[dict, dict, dict, dict]] = {}

    def get_field(name: str):
        if name not in field_cache:
            path = f"FIELD/{name}.DAT"
            field_cache[name] = (
                slot_map(extract_file(c1, path)),
                slot_map(extract_file(c2, path)),
                slot_map(extract_file(p1, path)),
                slot_map(extract_file(p2, path)),
            )
        return field_cache[name]

    lines = ["# Per-slot edit-origin (pristine-anchored) for 9 rework fields", ""]
    lines.append("| Field | Slot | D1 edited by CSR? | D2 edited by CSR? | Origin verdict |")
    lines.append("|---|---|---|---|---|")

    rows = []
    for field, entity, slot in SLOTS:
        c1m, c2m, p1m, p2m = get_field(field)
        key = (entity, slot)
        c1s, c2s, p1s, p2s = c1m.get(key), c2m.get(key), p1m.get(key), p2m.get(key)
        d1_edit = (c1s != p1s)
        d2_edit = (c2s != p2s)
        if p1s is None or p2s is None:
            verdict = "no pristine baseline (slot missing pre-CSR)"
        elif d1_edit and not d2_edit:
            verdict = "D1-ONLY edit -> take D1"
        elif d2_edit and not d1_edit:
            verdict = "D2-ONLY edit -> take D2"
        elif d1_edit and d2_edit:
            verdict = "BOTH edited independently -> needs judgement call"
        else:
            verdict = "NEITHER edited vs pristine (unexpected)"
        rows.append((field, entity, slot, d1_edit, d2_edit, verdict))
        lines.append(f"| {field} | {entity}:{slot} | {d1_edit} | {d2_edit} | {verdict} |")

    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    for field, entity, slot, d1e, d2e, verdict in rows:
        print(f"{field} {entity}:{slot}: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
