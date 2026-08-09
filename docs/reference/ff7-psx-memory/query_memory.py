#!/usr/bin/env python3
"""Query imported FF7 PSX memory map.

Usage:
  python3 docs/reference/ff7-psx-memory/query_memory.py victory
  python3 docs/reference/ff7-psx-memory/query_memory.py 62D78
  python3 docs/reference/ff7-psx-memory/query_memory.py 80062D78
  python3 docs/reference/ff7-psx-memory/query_memory.py --tag battle-end
  python3 docs/reference/ff7-psx-memory/query_memory.py --near 62D7C --span 0x40
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "psx-address-list.json"


def load() -> list[dict]:
    return json.loads(DATA.read_text(encoding="utf-8"))["entries"]


def parse_addr(s: str) -> int | None:
    s = s.strip().lower().replace("0x", "")
    if not re.fullmatch(r"[0-9a-f]+", s):
        return None
    v = int(s, 16)
    if v >= 0x80000000:
        v &= 0x1FFFFF
    elif v >= 0xA0000000:
        v &= 0x1FFFFF
    return v


def fmt(it: dict) -> str:
    va = it.get("duckstation_va") or "-"
    tags = ",".join(it.get("tags") or [])
    notes = it.get("notes") or ""
    if len(notes) > 160:
        notes = notes[:157] + "..."
    line = (
        f"{it.get('psx_offset') or '?':>8}  {va:>12}  "
        f"{str(it.get('byte_length') or '-'):>4}  {it.get('description')}"
    )
    if tags:
        line += f"  [{tags}]"
    if notes:
        line += f"\n           {notes}"
    return line


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("query", nargs="?", help="text and/or hex address")
    ap.add_argument("--tag", action="append", default=[], help="require tag")
    ap.add_argument("--near", help="hex offset center")
    ap.add_argument("--span", default="0x80", help="span around --near")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args(argv)

    hits = load()
    if args.tag:
        need = set(args.tag)
        hits = [e for e in hits if need.issubset(set(e.get("tags") or []))]

    if args.near:
        c = parse_addr(args.near)
        if c is None:
            print("bad --near", args.near, file=sys.stderr)
            return 2
        span = int(args.span, 0)
        lo, hi = c - span, c + span
        hits = [
            e
            for e in hits
            if e.get("psx_offset_int") is not None and lo <= e["psx_offset_int"] <= hi
        ]

    if args.query:
        q = args.query.strip()
        addr = parse_addr(q)
        pure_addr = addr is not None and re.fullmatch(r"(0x)?[0-9a-fA-F]+", q)
        text_q = q.lower()
        filtered: list[dict] = []
        for e in hits:
            ok = False
            if addr is not None and e.get("psx_offset_int") is not None:
                bl = max(e.get("byte_length") or 1, 1)
                base = e["psx_offset_int"]
                if base == addr or base <= addr < base + bl:
                    ok = True
            blob = (
                f"{e.get('description', '')} {e.get('notes') or ''} "
                f"{' '.join(e.get('tags') or [])}"
            ).lower()
            if not pure_addr and text_q in blob:
                ok = True
            if ok:
                filtered.append(e)
        hits = filtered

    hits = sorted(
        hits, key=lambda e: (e.get("psx_offset_int") is None, e.get("psx_offset_int") or 0)
    )
    if args.json:
        json.dump(hits, sys.stdout, indent=2)
        print()
    else:
        print(f"{len(hits)} hit(s)")
        for e in hits[:200]:
            print(fmt(e))
            print()
        if len(hits) > 200:
            print(f"... {len(hits) - 200} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
