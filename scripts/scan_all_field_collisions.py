#!/usr/bin/env python3
"""Fresh, from-scratch scan of every FIELD/*.DAT across CSR D1/D2/D3.

Does not trust mods/single-disc/patches/csr-d2d3-field-merge-on-d1.md or
csr-field-disc-prefer.txt — rebuilds the truth from the actual disc images.

For every field name present on 2+ CSR discs, determines per-disc whether
CSR edited it (vs pristine same disc), and if 2+ discs both have edits,
classifies the CSR-vs-CSR diff (identical / pad-only / scripts / mixed /
sections) using the existing field_compare machinery. Only "scripts"/"mixed"
with edits on more than one disc are true single-disc-merge collisions
needing an op-level merge (game-moment branch preserved from both).

Usage:
  python3 scripts/scan_all_field_collisions.py -o /tmp/collisions.md
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from disc_sources import load_csr_image, load_pristine_image  # noqa: E402
from field_compare import compare_bytes  # noqa: E402
from psx_mode2_iso import SECTOR, USER, USER_OFF, extract_file, find_file  # noqa: E402


def _u32_le(b: bytes, i: int) -> int:
    return b[i] | (b[i + 1] << 8) | (b[i + 2] << 16) | (b[i + 3] << 24)


def _user(img: bytes, lba: int) -> bytes:
    off = lba * SECTOR + USER_OFF
    return bytes(img[off : off + USER])


def list_field_dir(img: bytes) -> dict[str, tuple[int, int]]:
    """Return {NAME (no .DAT): (lba, size)} for every entry under FIELD/."""
    field_dir = find_file  # reuse resolver by locating FIELD as a "file" won't work; walk manually
    pvd = _user(img, 16)
    root = pvd[156:190]
    dir_lba = _u32_le(root, 2)
    dir_size = _u32_le(root, 10)

    def _list_dir(lba: int, size: int):
        remaining = size
        sector = lba
        blob = bytearray()
        while remaining > 0:
            take = min(USER, remaining)
            blob += _user(img, sector)[:take]
            remaining -= take
            sector += 1
        out = []
        i = 0
        while i < len(blob):
            length = blob[i]
            if length == 0:
                nxt = ((i // USER) + 1) * USER
                if nxt <= i:
                    break
                i = nxt
                continue
            if i + length > len(blob):
                break
            rec = blob[i : i + length]
            flags = rec[25]
            name_len = rec[32]
            if name_len == 1 and rec[33] in (0x00, 0x01):
                i += length
                continue
            name = rec[33 : 33 + name_len].split(b";", 1)[0].decode("ascii", "replace").upper()
            lba_e = _u32_le(rec, 2)
            size_e = _u32_le(rec, 10)
            is_dir = bool(flags & 0x02)
            out.append((name, lba_e, size_e, is_dir))
            i += length
        return out

    root_entries = _list_dir(dir_lba, dir_size)
    field_entry = next((e for e in root_entries if e[0] == "FIELD"), None)
    if field_entry is None:
        raise FileNotFoundError("FIELD dir not found")
    _, flba, fsize, _ = field_entry
    entries = _list_dir(flba, fsize)
    out: dict[str, tuple[int, int]] = {}
    for name, lba, size, is_dir in entries:
        if is_dir or not name.endswith(".DAT"):
            continue
        out[name[: -len(".DAT")]] = (lba, size)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    print("Loading pristine + CSR images for D1/D2/D3...")
    pristine = {d: bytes(load_pristine_image(d)) for d in (1, 2, 3)}
    csr = {d: bytes(load_csr_image(d)) for d in (1, 2, 3)}

    print("Listing FIELD/*.DAT per disc...")
    listings = {d: list_field_dir(csr[d]) for d in (1, 2, 3)}
    all_names = sorted(set(listings[1]) | set(listings[2]) | set(listings[3]))
    print(f"Total distinct field names across D1/D2/D3: {len(all_names)}")

    multi_disc: list[str] = [n for n in all_names if sum(n in listings[d] for d in (1, 2, 3)) >= 2]
    print(f"Fields present on 2+ discs: {len(multi_disc)}")

    rows = []
    for name in multi_disc:
        present = [d for d in (1, 2, 3) if name in listings[d]]
        path = f"FIELD/{name}.DAT"
        edited = {}
        data = {}
        for d in present:
            data[d] = extract_file(csr[d], path)
            try:
                pdata = extract_file(pristine[d], path)
                edited[d] = pdata != data[d]
            except FileNotFoundError:
                edited[d] = True  # field doesn't exist on that pristine disc; CSR-only
        edited_discs = [d for d in present if edited[d]]

        if len(edited_discs) <= 1:
            rows.append((name, present, edited_discs, "safe", "single-disc-edit or no edits"))
            continue

        # 2+ discs edited it — compare CSR-vs-CSR pairwise among edited discs
        worst = "identical"
        detail_bits = []
        order = ["identical", "pad-only", "sections", "scripts", "mixed"]
        for i in range(len(edited_discs)):
            for j in range(i + 1, len(edited_discs)):
                da, db = edited_discs[i], edited_discs[j]
                if data[da] == data[db]:
                    cls = "identical"
                else:
                    diff = compare_bytes(data[da], data[db], a_label=f"D{da}", b_label=f"D{db}")
                    cls = diff.classification
                detail_bits.append(f"D{da}v D{db}={cls}")
                if order.index(cls) > order.index(worst):
                    worst = cls
        verdict = "COLLISION" if worst in ("scripts", "mixed") else "safe"
        rows.append((name, present, edited_discs, verdict, "; ".join(detail_bits)))

    collisions = [r for r in rows if r[3] == "COLLISION"]
    safe = [r for r in rows if r[3] == "safe"]

    lines = [
        "# Fresh field-collision scan: CSR D1 vs D2 vs D3 (all fields)",
        "",
        "Generated by `scripts/scan_all_field_collisions.py`. Supersedes/replaces",
        "`mods/single-disc/patches/csr-d2d3-field-merge-on-d1.md` and",
        "`mods/single-disc/patches/csr-field-disc-prefer.txt` (both deleted).",
        "",
        f"- Fields present on 2+ discs: {len(multi_disc)}",
        f"- Real collisions (2+ discs edited, script/mixed diff): {len(collisions)}",
        f"- Safe (0-1 disc edited, or edits identical/pad-only): {len(safe)}",
        "",
        "## Real collisions — need op-level merge",
        "",
        "| Field | Present on | Edited on | Detail |",
        "|-------|-----------|-----------|--------|",
    ]
    for name, present, edited_discs, _, detail in collisions:
        lines.append(
            f"| {name} | D{','.join(str(d) for d in present)} | "
            f"D{','.join(str(d) for d in edited_discs)} | {detail} |"
        )
    lines += ["", "## Safe fields (single-disc edit or no real conflict)", "",
              "| Field | Present on | Edited on |", "|-------|-----------|-----------|"]
    for name, present, edited_discs, _, _ in safe:
        lines.append(
            f"| {name} | D{','.join(str(d) for d in present)} | "
            f"D{','.join(str(d) for d in edited_discs) if edited_discs else '(none)'} |"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {args.output}")
    print(f"COLLISIONS: {len(collisions)}")
    for name, *_ in collisions:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
