#!/usr/bin/env python3
"""CLI for scripts/decomp_symbol_map.py -- look up FF7 decomp global symbols
by name or PSX RAM address.

Verification contract (scripts/README.md): every result line is tagged
[CONFIRMED] (address comes directly from the `D_<hex>` symbol name or an
explicit `// 0xADDR` source comment) or [UNCONFIRMED: <reason>] (named
global with no documented address -- correlate via duckstation_addr_advisor
before trusting).

Examples:
  python3 scripts/decomp_symbol_lookup.py --name Savemap
  python3 scripts/decomp_symbol_lookup.py --addr 0x8009C6E4
  python3 scripts/decomp_symbol_lookup.py --addr 0x8009C700 --nearest
  python3 scripts/decomp_symbol_lookup.py --stats
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from decomp_symbol_map import find_by_address, find_nearest_below, get, load_symbols  # noqa: E402


def _fmt(sym) -> str:
    return repr(sym)


def cmd_name(name: str) -> int:
    sym = get(name)
    if sym is None:
        print(f"[UNCONFIRMED: symbol not found in extracted headers] {name}")
        return 1
    print(_fmt(sym))
    return 0


def cmd_addr(addr: int, nearest: bool) -> int:
    sym = find_by_address(addr)
    if sym is not None:
        print(_fmt(sym))
        return 0
    if not nearest:
        print(f"[UNCONFIRMED: no symbol with exact address 0x{addr:08X}] "
              f"(pass --nearest to find the containing symbol)")
        return 1
    near = find_nearest_below(addr)
    if near is None:
        print(f"[UNCONFIRMED: no confirmed-address symbol at or below 0x{addr:08X}]")
        return 1
    offset = addr - near.address
    print(f"[CONFIRMED] 0x{addr:08X} is +0x{offset:X} into {near.name} "
          f"(base 0x{near.address:08X}, {near.ctype}{near.array}, {near.source_file})")
    if near.comment:
        print(f"    comment: {near.comment}")
    return 0


def cmd_stats() -> int:
    syms = load_symbols()
    confirmed = [s for s in syms.values() if s.confirmed]
    unconfirmed = [s for s in syms.values() if not s.confirmed]
    print(f"[CONFIRMED] {len(confirmed)} symbols with a known RAM address "
          f"(D_<hex> name or documented comment)")
    print(f"[UNCONFIRMED: no documented address] {len(unconfirmed)} named globals "
          f"(g_*, etc.) with no address in this extraction")
    print(f"total extracted: {len(syms)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", help="exact decomp symbol name, e.g. Savemap")
    ap.add_argument("--addr", help="PSX RAM address, e.g. 0x8009C6E4")
    ap.add_argument("--nearest", action="store_true",
                     help="with --addr, fall back to nearest symbol at/below the address")
    ap.add_argument("--stats", action="store_true", help="print extraction coverage stats")
    args = ap.parse_args()

    if args.stats:
        return cmd_stats()
    if args.name:
        return cmd_name(args.name)
    if args.addr:
        try:
            addr = int(args.addr, 16) if args.addr.lower().startswith("0x") else int(args.addr)
        except ValueError:
            print(f"error: bad address {args.addr!r}", file=sys.stderr)
            return 1
        return cmd_addr(addr, args.nearest)

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
