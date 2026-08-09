#!/usr/bin/env python3
"""Generate battle-related.md from psx-address-list.json."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "docs/reference/ff7-psx-memory/psx-address-list.json"
OUT = REPO / "docs/reference/ff7-psx-memory/battle-related.md"


def main() -> None:
    items = json.loads(DATA.read_text(encoding="utf-8"))["entries"]
    battle = []
    seen: set[str] = set()
    for it in items:
        tags = set(it.get("tags") or [])
        off = it.get("psx_offset_int")
        keep = bool(tags & {"battle", "battle-end", "input", "rng", "audio", "rewards"})
        if off is not None and (0x62000 <= off <= 0x64000 or 0xF8000 <= off <= 0xF9000):
            keep = True
        if keep and it["id"] not in seen:
            seen.add(it["id"])
            battle.append(it)
    battle.sort(key=lambda x: (x.get("psx_offset_int") is None, x.get("psx_offset_int") or 0))

    def cell(s: str) -> str:
        return s.replace("|", "/").replace("\n", " ")

    lines = [
        "# PSX memory — battle-related (excerpt)",
        "",
        "Auto-filtered from psx-address-list.json for battle / battle-end / nearby input / audio / rewards.",
        "Full list: same folder JSON/CSV.",
        "Query: python3 docs/reference/ff7-psx-memory/query_memory.py TEXT_OR_ADDR",
        "",
        "| Offset | DuckStation VA | Len | Description | Notes |",
        "|--------|----------------|-----|-------------|-------|",
    ]
    for it in battle:
        notes = cell(it.get("notes") or "")
        if len(notes) > 120:
            notes = notes[:117] + "..."
        desc = cell(it["description"])
        off = it.get("psx_offset") or ""
        va = it.get("duckstation_va") or ""
        bl = it.get("byte_length") or ""
        lines.append(f"| {off} | {va} | {bl} | {desc} | {notes} |")
    lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(battle)} rows -> {OUT}")


if __name__ == "__main__":
    main()
