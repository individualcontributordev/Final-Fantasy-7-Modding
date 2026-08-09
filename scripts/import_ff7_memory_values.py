#!/usr/bin/env python3
"""Import community FF7 Memory Values CSV into docs/reference/ff7-psx-memory/."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "reference" / "ff7-psx-memory"
DEFAULT_CSV = Path.home() / "Downloads" / "FF7 Memory Values - PSX Address List.csv"

TAG_RULES = [
    (r"\bbattle\b|enemy slot|formation|atb|limit bar|cued damage|preemptive|game over|victory|run away|fade out exit", "battle"),
    (r"\bfield\b|danger|step id|encounter|paralysis", "field"),
    (r"world map|\bwm:", "world"),
    (r"\brng\b|random", "rng"),
    (r"controller|inputs", "input"),
    (r"materia|weapon|armor|accessory", "equipment"),
    (r"cloud|barret|tifa|aeris|red xiii|yuffie|cait|vincent|cid|party", "party"),
    (r"chocobo", "chocobo"),
    (r"gil|exp\b|\bap\b|reward", "rewards"),
    (r"music|akao|fanfare|sound", "audio"),
    (r"camera", "camera"),
    (r"status|poison|silence|death|berserk", "status"),
    (r"menu|save", "menu"),
    (r"victory|fanfare|celebr|pose|exit battle", "battle-end"),
]


def tags_for(desc: str, notes: str) -> list[str]:
    blob = f"{desc} {notes}".lower()
    out: list[str] = []
    seen: set[str] = set()
    for pat, tag in TAG_RULES:
        if re.search(pat, blob, re.I) and tag not in seen:
            seen.add(tag)
            out.append(tag)
    return out


def parse_len(blen: str, vtype: str) -> int | None:
    blen = (blen or "").strip()
    if blen:
        try:
            return int(float(blen))
        except ValueError:
            pass
    return {"Byte": 1, "2 Bytes": 2, "4 Bytes": 4, "8 Bytes": 8}.get(vtype)


def norm_offset(s: str) -> str | None:
    s = (s or "").strip().upper().replace("0X", "").replace(" ", "")
    if not s:
        return None
    if re.fullmatch(r"[0-9A-F]+", s):
        return s.lstrip("0") or "0"
    return s


def load_items(csv_path: Path) -> list[dict]:
    items: list[dict] = []
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        rdr = csv.reader(f)
        next(rdr, None)
        for r in rdr:
            g = lambda i: r[i].strip() if i < len(r) and r[i] else ""
            desc, notes, vtype = g(1), g(10), g(3)
            off = norm_offset(g(2) or g(9))
            if not desc and not off:
                continue
            psx_int = int(off, 16) if off and re.fullmatch(r"[0-9A-F]+", off) else None
            duck_va = (
                f"0x{0x80000000 + psx_int:08X}"
                if psx_int is not None and psx_int < 0x200000
                else None
            )
            blen = parse_len(g(7) or g(8), vtype)
            eid = f"psx_{off.lower()}" if off and re.fullmatch(r"[0-9A-F]+", off) else None
            if eid is None:
                eid = "psx_row_" + hashlib.sha1(f"{desc}|{off}".encode()).hexdigest()[:10]
            items.append(
                {
                    "id": eid,
                    "description": desc,
                    "psx_offset": off,
                    "psx_offset_int": psx_int,
                    "duckstation_va": duck_va,
                    "type": vtype or None,
                    "byte_length": blen,
                    "show_as_hex": g(5) in ("1", "1.0", "true", "True"),
                    "notes": notes or None,
                    "tags": tags_for(desc, notes),
                    "source_sort": g(0) or None,
                }
            )
    uniq: dict[tuple, dict] = {}
    for it in items:
        k = (it["psx_offset"], it["description"])
        if k not in uniq or len(it.get("notes") or "") > len(uniq[k].get("notes") or ""):
            uniq[k] = it
    return sorted(
        uniq.values(),
        key=lambda x: (x["psx_offset_int"] is None, x["psx_offset_int"] or 0, x["description"]),
    )


def write_outputs(items: list[dict], src: Path) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "source": {
            "title": "FF7 Memory Values — PSX Address List",
            "imported_from": str(src),
            "sheets_used": ["PSX Address List"],
            "sheets_skipped": [
                "PC Addresses",
                "PC Address List",
                "Using CheatEngine with Emulator",
                "SizeRef",
            ],
            "notes": (
                "Offsets are PSX main RAM offsets (no 0x80000000). "
                "duckstation_va = 0x80000000 + offset for typical main RAM. "
                "Community map; not Square-official."
            ),
        },
        "entry_count": len(items),
        "entries": items,
    }
    (OUT / "psx-address-list.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    with (OUT / "psx-address-list.jsonl").open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    with (OUT / "psx-address-list.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            ["psx_offset", "duckstation_va", "byte_length", "type", "description", "tags", "notes"]
        )
        for it in items:
            va = (it["duckstation_va"] or "").replace("0x", "")
            w.writerow(
                [
                    it["psx_offset"] or "",
                    va,
                    it["byte_length"] if it["byte_length"] is not None else "",
                    it["type"] or "",
                    it["description"],
                    ",".join(it["tags"]),
                    it["notes"] or "",
                ]
            )
    print(f"Wrote {len(items)} entries under {OUT}")
    gen = REPO / "scripts" / "_gen_battle_mem_excerpt.py"
    if gen.is_file():
        import runpy

        runpy.run_path(str(gen), run_name="__main__")


def main() -> None:
    src = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else DEFAULT_CSV
    if not src.is_file():
        raise SystemExit(f"CSV not found: {src}")
    write_outputs(load_items(src), src)


if __name__ == "__main__":
    main()
