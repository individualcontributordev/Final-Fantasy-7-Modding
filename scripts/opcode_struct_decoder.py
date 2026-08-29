#!/usr/bin/env python3
"""Decode a field-script opcode's raw param bytes into named fields, using
struct layouts extracted from external/makoureactor/src/core/field/Opcode.h
(see scripts/opcode_struct_layout.py for the extraction + verification
notes on what is/isn't on-wire).

When to use:
  - You have raw opcode bytes (e.g. from field_pattern_finder.py's --hex
    hits) and want them broken into named/typed fields instead of a hex
    blob, to know what to actually change for a patch.

Verification contract (scripts/README.md):
  - Field breakdown is [CONFIRMED] when: (a) a direct Opcode<NAME> struct
    exists in Opcode.h, AND (b) the flattened field sizes sum to exactly
    OPCODE_LENGTH[name] - 1 (the -1 excludes the opcode id byte at offset
    0). If sizes don't sum to that, the struct/length are out of sync with
    this build of makoureactor and the whole decode is
    [UNCONFIRMED: struct/length size mismatch].
  - [UNCONFIRMED: no direct struct match for this opcode name] when the
    opcode has no Opcode<NAME> struct (e.g. '!'-suffixed assign variants,
    2BYTE, CHAR, ANIM!1/CANM!1 family -- see opcode_struct_layout.py).

Not for: opcode-boundary search in a DAT (use field_pattern_finder.py) or
RAM addresses (use duckstation_addr_advisor.py).

Examples:
  python3 scripts/opcode_struct_decoder.py IFUB 011405000a
  python3 scripts/opcode_struct_decoder.py MUSIC --hex 2801
  python3 scripts/opcode_struct_decoder.py --list-mismatches
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ff7_opcodes import OPCODE_LENGTH, OPCODE_NAMES  # noqa: E402
from opcode_struct_layout import get_layout, load_layouts  # noqa: E402


def opcode_length(name: str) -> int | None:
    try:
        return OPCODE_LENGTH[OPCODE_NAMES.index(name)]
    except ValueError:
        return None


def decode(name: str, raw: bytes) -> list[str]:
    """Returns CONFIRMED/UNCONFIRMED-tagged lines describing each field."""
    fields = get_layout(name)
    total_len = opcode_length(name)
    out: list[str] = []

    if fields is None:
        out.append(f"[UNCONFIRMED: no direct struct match for this opcode name] {name}")
        return out

    expected_param_bytes = sum(f.size for f in fields)
    if total_len is not None and expected_param_bytes != total_len - 1:
        out.append(
            f"[UNCONFIRMED: struct/length size mismatch] {name}: "
            f"struct fields sum to {expected_param_bytes}B, "
            f"OPCODE_LENGTH-1 expects {total_len - 1}B"
        )
        return out

    if len(raw) < expected_param_bytes:
        out.append(
            f"[UNCONFIRMED: insufficient bytes] {name} needs {expected_param_bytes}B "
            f"params, got {len(raw)}B"
        )
        return out

    off = 0
    for f in fields:
        chunk = raw[off:off + f.size]
        val = int.from_bytes(chunk, "little", signed=f.ctype.startswith("qint"))
        comment = f" ({f.comment})" if f.comment else ""
        out.append(
            f"[CONFIRMED] {name}.{f.name} off=0x{off:X} size={f.size}B "
            f"type={f.ctype} value=0x{val:X} ({val}){comment}"
        )
        off += f.size

    return out


def list_mismatches() -> list[str]:
    """Cross-checks every OPCODE_NAMES entry with a direct struct match
    against OPCODE_LENGTH, for spotting extraction bugs / makoureactor
    version drift up front."""
    layouts = load_layouts()
    out: list[str] = []
    for name, length in zip(OPCODE_NAMES, OPCODE_LENGTH):
        if name not in layouts:
            continue
        expected = sum(f.size for f in layouts[name])
        if expected != length - 1:
            out.append(
                f"[UNCONFIRMED: struct/length size mismatch] {name}: "
                f"struct={expected}B OPCODE_LENGTH-1={length - 1}B"
            )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("opcode", nargs="?", help="opcode mnemonic, e.g. IFUB, MUSIC")
    ap.add_argument("hex", nargs="?", help="raw param bytes as hex (opcode id byte excluded)")
    ap.add_argument("--list-mismatches", action="store_true",
                     help="cross-check all opcodes' struct sizes vs OPCODE_LENGTH and exit")
    args = ap.parse_args()

    if args.list_mismatches:
        mismatches = list_mismatches()
        if not mismatches:
            print("no mismatches -- all direct-struct opcodes agree with OPCODE_LENGTH")
        for m in mismatches:
            print(m)
        return 0

    if not args.opcode or not args.hex:
        ap.print_help()
        return 1

    try:
        raw = bytes.fromhex(args.hex)
    except ValueError:
        print(f"error: bad hex value: {args.hex!r}", file=sys.stderr)
        return 1

    for line in decode(args.opcode.upper(), raw):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
