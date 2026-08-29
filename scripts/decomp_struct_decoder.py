#!/usr/bin/env python3
"""Decode a raw memory dump against a ff7-decomp struct layout
(scripts/decomp_struct_layout.py), optionally anchored to a known global's
RAM address (scripts/decomp_symbol_map.py) for absolute-address output.

Verification contract (scripts/README.md):
  - [CONFIRMED] fields: offset is either a decomp-documented `/* 0xHEX */`
    comment, or computed purely from preceding known-size fields.
  - [UNCONFIRMED: offset depends on a preceding field of unknown size]:
    an earlier field in the struct has no resolvable size (custom struct
    type not extracted, flexible array, bitfield, etc.), so this field's
    offset is a guess -- verify against the source header directly.

Examples:
  # Decode a raw dump of the SaveWork struct (e.g. bytes read from
  # DuckStation at 0x8009C6E4, the documented address of `Savemap`).
  python3 scripts/decomp_struct_decoder.py SaveWork <hexbytes> --symbol Savemap

  python3 scripts/decomp_struct_decoder.py --list-structs
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from decomp_struct_layout import get_struct, get_struct_size, load_struct_layouts  # noqa: E402
from decomp_symbol_map import get as get_symbol  # noqa: E402

_INT_TYPES = {"u8": False, "s8": True, "u16": False, "s16": True, "u32": False, "s32": True, "int": True}


def decode(struct_name: str, raw: bytes, base_addr: int | None) -> list[str]:
    fields = get_struct(struct_name)
    out: list[str] = []
    if fields is None:
        out.append(f"[UNCONFIRMED: no typedef struct named {struct_name!r} found in extracted headers]")
        return out

    total = get_struct_size(struct_name)
    if total is not None and len(raw) < total:
        out.append(f"[UNCONFIRMED: input is {len(raw)}B, struct documents size {total}B -- "
                   f"decode may run past provided bytes]")

    for f in fields:
        if f.offset is None or f.size is None:
            out.append(f"[UNCONFIRMED: offset/size unresolved] {struct_name}.{f.name} "
                       f"({f.ctype}{'*' if f.is_ptr else ''}{f.array})")
            continue
        chunk = raw[f.offset:f.offset + f.size]
        addr_prefix = f"0x{base_addr + f.offset:08X} " if base_addr is not None else ""
        tag = "CONFIRMED" if f.confirmed else "UNCONFIRMED: offset depends on a preceding field of unknown size"
        if len(chunk) < f.size:
            out.append(f"[{tag}] {addr_prefix}off=0x{f.offset:X} {struct_name}.{f.name} "
                       f"-- insufficient bytes ({len(chunk)}/{f.size})")
            continue
        if f.is_ptr:
            val_str = chunk.hex()
        elif f.ctype in _INT_TYPES and f.array in ("", "[1]"):
            val = int.from_bytes(chunk, "little", signed=_INT_TYPES[f.ctype])
            val_str = f"0x{val:X} ({val})"
        else:
            val_str = chunk.hex()
        out.append(f"[{tag}] {addr_prefix}off=0x{f.offset:X} size={f.size}B "
                   f"{struct_name}.{f.name} ({f.ctype}{f.array}) = {val_str}")
    return out


def list_structs() -> list[str]:
    layouts = load_struct_layouts()
    out = []
    for name in sorted(layouts):
        size = get_struct_size(name)
        n_confirmed = sum(1 for f in layouts[name] if f.confirmed)
        out.append(f"{name}: {len(layouts[name])} fields, {n_confirmed} confirmed-offset, "
                   f"documented size={'0x%X' % size if size else 'unknown'}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("struct", nargs="?", help="struct name, e.g. SaveWork, FieldEntity")
    ap.add_argument("hex", nargs="?", help="raw bytes as hex")
    ap.add_argument("--symbol", help="anchor decode to a known decomp_symbol_map symbol's RAM address")
    ap.add_argument("--list-structs", action="store_true", help="list all extracted structs and exit")
    args = ap.parse_args()

    if args.list_structs:
        for line in list_structs():
            print(line)
        return 0

    if not args.struct or not args.hex:
        ap.print_help()
        return 1

    try:
        raw = bytes.fromhex(args.hex)
    except ValueError:
        print(f"error: bad hex value: {args.hex!r}", file=sys.stderr)
        return 1

    base_addr = None
    if args.symbol:
        sym = get_symbol(args.symbol)
        if sym is None or sym.address is None:
            print(f"[UNCONFIRMED: symbol {args.symbol!r} not found or has no known address]")
        else:
            base_addr = sym.address

    for line in decode(args.struct, raw, base_addr):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
