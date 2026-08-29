#!/usr/bin/env python3
"""Look up a RAM address/function name with CONFIRMED/UNCONFIRMED tags.

When to use:
  - You have a candidate address (from Ghidra auto-analysis or a guess) and
    want to know whether it's actually been emulator-correlated, before
    writing a patch/hook against it.
  - You remember a function's rough name and want its address(es).

See scripts/README.md "Verification contract":
  - [CONFIRMED]: matches a `- [x]` checklist entry in
    docs/05-ghidra-guide.md's "Functions to identify" section -- those were
    walked through DuckStation PC correlation, not just auto-analysis.
  - [UNCONFIRMED: auto-analysis only, no emulator correlation]: only found
    in scripts/ghidra/<binary>-functions.json / *-symbols.json (Ghidra's
    automatic analysis, un-reviewed).
  - [UNCONFIRMED: no checklist doc for this binary]: binaries other than
    FIELD.BIN currently have no docs/05-ghidra-guide.md-style checklist, so
    every hit for them is auto-analysis only.

Not for: field-script opcode offsets (use field_pattern_finder.py).

Examples:
  python3 scripts/duckstation_addr_advisor.py 0x800AB9C8
  python3 scripts/duckstation_addr_advisor.py increment_step_id
  python3 scripts/duckstation_addr_advisor.py FUN_800a16cc --binary field
  python3 scripts/duckstation_addr_advisor.py 0x800a2314 --binary battle
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GHIDRA_DIR = ROOT / "scripts" / "ghidra"

# binary -> (functions.json stem, checklist doc or None)
BINARIES: dict[str, tuple[str, Path | None]] = {
    "field": ("field", ROOT / "docs" / "05-ghidra-guide.md"),
    "battle": ("battle", None),
    "batres": ("batres", None),
    "world": ("world", None),
    "scus": ("scus-941-63", None),
}

_CHECKLIST_RE = re.compile(r"- \[x\] `([^`]+)`.*?@ `(0x[0-9A-Fa-f]+)`")


def load_checklist(doc: Path) -> list[tuple[str, str]]:
    """Return [(name, addr_hex), ...] from a docs/05-ghidra-guide.md-style
    checklist. `name` may itself embed a `FUN_xxxx` alias, e.g.
    'field_main_loop' with body '`FUN_800a16cc` @ `0x800A16CC`' -- both the
    outer label and any inner FUN_ name are returned as separate entries
    pointing at the same address, so lookups by either name succeed."""
    if not doc.is_file():
        return []
    out: list[tuple[str, str]] = []
    for line in doc.read_text(encoding="utf-8").splitlines():
        m = _CHECKLIST_RE.search(line)
        if not m:
            continue
        label, addr = m.group(1), m.group(2).lower()
        out.append((label, addr))
        for fun_m in re.finditer(r"FUN_[0-9a-fA-F]+", line):
            if fun_m.group(0) != label:
                out.append((fun_m.group(0), addr))
    return out


def load_json(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def norm_addr(s: str) -> str:
    return s.lower().replace("0x", "").lstrip("0") or "0"


def query_binary(binary: str, query: str) -> list[str]:
    stem, doc = BINARIES[binary]
    is_addr = bool(re.fullmatch(r"0x[0-9A-Fa-f]+", query))
    q_addr = norm_addr(query) if is_addr else None
    q_name = query if not is_addr else None

    out: list[str] = []

    checklist = load_checklist(doc) if doc else []
    for label, addr in checklist:
        match = (q_addr and norm_addr(addr) == q_addr) or (
            q_name and q_name.lower() in label.lower()
        )
        if match:
            out.append(f"[CONFIRMED] {label} @ {addr} (docs/05-ghidra-guide.md checklist)")

    funcs = load_json(GHIDRA_DIR / f"{stem}-functions.json")
    syms = load_json(GHIDRA_DIR / f"{stem}-symbols.json")
    reason = (
        "auto-analysis only, no emulator correlation"
        if doc
        else "no checklist doc for this binary"
    )
    for f in funcs:
        addr = f.get("address", "")
        name = f.get("name", "")
        match = (q_addr and norm_addr(addr) == q_addr) or (
            q_name and q_name.lower() in name.lower()
        )
        if match:
            out.append(
                f"[UNCONFIRMED: {reason}] {name} @ 0x{addr} "
                f"size={f.get('size')} callers={f.get('callers')} "
                f"({stem}-functions.json)"
            )
    for s in syms:
        addr = s.get("address", "")
        name = s.get("name", "")
        match = (q_addr and norm_addr(addr) == q_addr) or (
            q_name and q_name.lower() in name.lower()
        )
        if match:
            out.append(
                f"[UNCONFIRMED: {reason}] {name} @ 0x{addr} "
                f"type={s.get('type')} ({stem}-symbols.json)"
            )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", help="0xADDRESS or a (partial) function/symbol name")
    ap.add_argument(
        "--binary",
        choices=sorted(BINARIES),
        default="field",
        help="which Ghidra dataset to search (default: field)",
    )
    args = ap.parse_args()

    hits = query_binary(args.binary, args.query)
    if not hits:
        print(f"no matches for {args.query!r} in {args.binary}")
        print("(checked docs/05-ghidra-guide.md checklist + scripts/ghidra/*.json)")
        return 0
    for h in hits:
        print(h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
