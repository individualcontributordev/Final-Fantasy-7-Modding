#!/usr/bin/env python3
"""CLI for scripts/worldmap_opcode_layout.py -- look up / decode world-map
worldscript opcodes (wm0.ev, wm2.ev, wm3.ev), sourced from
external/ff7-landscaper's shipping opcode table.

Verification contract (scripts/README.md): every opcode line is tagged
[CONFIRMED] (comes directly from Landscaper's `Opcodes` table, which its own
decompiler/compiler round-trips against real world-map scripts). Unknown
opcode ids are reported [UNCONFIRMED: not in Landscaper's opcode table].

Examples:
  python3 scripts/worldmap_opcode_lookup.py --id 0x318
  python3 scripts/worldmap_opcode_lookup.py --mnemonic ENTER_FIELD
  python3 scripts/worldmap_opcode_lookup.py --id 0x210   # CALL_FN_12
  python3 scripts/worldmap_opcode_lookup.py --words 0318 0005 0000
  python3 scripts/worldmap_opcode_lookup.py --list
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from worldmap_opcode_layout import find_by_mnemonic, get, load_opcodes  # noqa: E402


def cmd_id(opcode_id: int) -> int:
    op = get(opcode_id)
    if op is None:
        print(f"[UNCONFIRMED: not in Landscaper's opcode table] 0x{opcode_id:03X}")
        return 1
    print(repr(op))
    return 0


def cmd_mnemonic(mnemonic: str) -> int:
    op = find_by_mnemonic(mnemonic.upper())
    if op is None:
        print(f"[UNCONFIRMED: no opcode with mnemonic {mnemonic!r}]")
        return 1
    print(repr(op))
    return 0


def cmd_words(words: list[str]) -> int:
    """Decodes a stream of 16-bit hex words (as they appear on-wire in
    wmX.ev) into instructions, consuming codeParams words per opcode."""
    values = [int(w, 16) for w in words]
    i = 0
    exit_code = 0
    while i < len(values):
        opcode_id = values[i]
        op = get(opcode_id)
        if op is None:
            print(f"[UNCONFIRMED: not in Landscaper's opcode table] 0x{opcode_id:03X} "
                  f"at word offset {i} -- stopping (can't know how many words to skip)")
            exit_code = 1
            break
        n_params = 0 if op.mnemonic.startswith("CALL_FN_") and op.mnemonic != "CALL_FN_" else op.code_params
        params = values[i + 1: i + 1 + n_params]
        params_str = " ".join(f"0x{p:04X}" for p in params)
        print(f"[CONFIRMED] word {i}: {op.mnemonic} ({op.namespace}.{op.name})"
              + (f"  params=[{params_str}]" if params else ""))
        i += 1 + n_params
    return exit_code


def cmd_list() -> int:
    ops = load_opcodes()
    for opcode_id in sorted(ops):
        print(repr(ops[opcode_id]))
    print(f"\n[CONFIRMED] {len(ops)} individually-listed opcodes "
          f"(+ CALL_FN_0..CALL_FN_43 as a contiguous 0x204-0x22F range)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", help="opcode id, e.g. 0x318")
    ap.add_argument("--mnemonic", help="opcode mnemonic, e.g. ENTER_FIELD")
    ap.add_argument("--words", nargs="+", help="hex words to decode as a script, e.g. 0318 0005 0000")
    ap.add_argument("--list", action="store_true", help="list all extracted opcodes")
    args = ap.parse_args()

    if args.list:
        return cmd_list()
    if args.id:
        return cmd_id(int(args.id, 16) if args.id.lower().startswith("0x") else int(args.id, 16))
    if args.mnemonic:
        return cmd_mnemonic(args.mnemonic)
    if args.words:
        return cmd_words(args.words)

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
