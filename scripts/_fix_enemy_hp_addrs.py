#!/usr/bin/env python3
"""Correct enemy current/max HP in the PSX memory DB (actor block, stride 0x68).

Playtest: Enemy 1 Current HP 0x800F85AC works. Enemy 2/3 are +0x68 / +0xD0,
not the spreadsheet rows at F875C/F87C4 (stats-block copies).
"""
from __future__ import annotations

import csv
import json
import runpy
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs/reference/ff7-psx-memory"
JSON_PATH = OUT / "psx-address-list.json"

# Actor battle block: same stride as Player 1/2/3 HP (0x68).
ACTOR_STRIDE = 0x68
E1_CUR = 0xF85AC
E1_MAX = 0xF85B0
# Spreadsheet's second HP family (stats block) — keep but relabel.
STATS_CUR = {1: 0xF86F4, 2: 0xF875C, 3: 0xF87C4, 4: 0xF882C, 5: 0xF8894, 6: 0xF88FC}
STATS_MAX = {1: 0xF86F8, 2: 0xF8760, 3: 0xF87C8, 4: 0xF8830, 5: 0xF8898, 6: 0xF8900}

NOTE_ACTOR = (
    "Live actor HP in battle (confirmed). Slot stride 0x68 from Enemy 1. "
    "Enemy N = F85AC + (N-1)*0x68. Distinct from stats-block HP near F86F4."
)
NOTE_STATS = (
    "Stats-block / secondary HP copy (spreadsheet). Not the live actor HP used "
    "for on-screen enemy health; use F85AC + (N-1)*0x68 instead."
)


def va(off: int) -> str:
    return f"0x{0x80000000 + off:08X}"


def hex_off(off: int) -> str:
    return f"{off:X}"


def make_entry(off: int, desc: str, notes: str, tags: list[str]) -> dict:
    return {
        "id": f"psx_{hex_off(off).lower()}",
        "description": desc,
        "psx_offset": hex_off(off),
        "psx_offset_int": off,
        "duckstation_va": va(off),
        "type": "2 Bytes",
        "byte_length": 2,
        "show_as_hex": False,
        "notes": notes,
        "tags": tags,
        "source_sort": None,
    }


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    entries: list[dict] = data["entries"]
    by_off: dict[int, list[dict]] = {}
    for e in entries:
        oi = e.get("psx_offset_int")
        if oi is not None:
            by_off.setdefault(oi, []).append(e)

    tags = ["battle"]

    # Update / insert actor-block HP for enemies 1-6
    for n in range(1, 7):
        cur_off = E1_CUR + (n - 1) * ACTOR_STRIDE
        max_off = E1_MAX + (n - 1) * ACTOR_STRIDE
        for off, kind in ((cur_off, "Current HP"), (max_off, "Max HP")):
            desc = f"Enemy {n} {kind}"
            note = NOTE_ACTOR
            existing = by_off.get(off, [])
            matched = [e for e in existing if e.get("description") == desc]
            if matched:
                for e in matched:
                    e["notes"] = note
                    e["tags"] = sorted(set((e.get("tags") or []) + tags))
                    e["byte_length"] = 2
                    e["type"] = "2 Bytes"
                    e["duckstation_va"] = va(off)
            else:
                # avoid dup id if something else owns this offset
                ent = make_entry(off, desc, note, tags)
                if off in by_off:
                    # only add if no same description
                    entries.append(ent)
                    by_off.setdefault(off, []).append(ent)
                else:
                    entries.append(ent)
                    by_off[off] = [ent]

    # Relabel stats-block Current/Max HP
    for n, off in STATS_CUR.items():
        for e in by_off.get(off, []):
            if "Current HP" in (e.get("description") or ""):
                e["description"] = f"Enemy {n} Current HP (stats block)"
                e["notes"] = NOTE_STATS
                e["tags"] = sorted(set((e.get("tags") or []) + tags))
    for n, off in STATS_MAX.items():
        for e in by_off.get(off, []):
            if "Max HP" in (e.get("description") or ""):
                e["description"] = f"Enemy {n} Max HP (stats block)"
                e["notes"] = NOTE_STATS
                e["tags"] = sorted(set((e.get("tags") or []) + tags))

    entries.sort(
        key=lambda x: (x.get("psx_offset_int") is None, x.get("psx_offset_int") or 0, x["description"])
    )
    data["entries"] = entries
    data["entry_count"] = len(entries)
    data.setdefault("source", {})["corrections"] = (
        "Enemy actor HP: F85AC + (N-1)*0x68 confirmed playtest 2026-08-09; "
        "spreadsheet F875C/F87C4 family marked stats-block."
    )
    JSON_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    # JSONL + CSV
    with (OUT / "psx-address-list.jsonl").open("w", encoding="utf-8") as f:
        for it in entries:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    with (OUT / "psx-address-list.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            ["psx_offset", "duckstation_va", "byte_length", "type", "description", "tags", "notes"]
        )
        for it in entries:
            va_s = (it.get("duckstation_va") or "").replace("0x", "")
            w.writerow(
                [
                    it.get("psx_offset") or "",
                    va_s,
                    it["byte_length"] if it.get("byte_length") is not None else "",
                    it.get("type") or "",
                    it.get("description") or "",
                    ",".join(it.get("tags") or []),
                    it.get("notes") or "",
                ]
            )
    runpy.run_path(str(REPO / "scripts/_gen_battle_mem_excerpt.py"), run_name="__main__")
    print("fixed enemy HP entries")


if __name__ == "__main__":
    main()
