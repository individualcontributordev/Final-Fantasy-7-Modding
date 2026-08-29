#!/usr/bin/env python3
"""Decode a raw memory dump against a PC (1998 retail .exe) FF7 struct
layout extracted from ergonomy-joe's ff7-chocobo/ff7-coaster decompilations
(scripts/pc_struct_layout.py).

Verification contract (scripts/README.md): every field's offset is
[CONFIRMED] -- ergonomy_joe's headers give explicit `/*HEX*/` offset
comments for every field, unlike ff7-decomp where offsets are sometimes
computed. There is no PC RAM symbol map yet (unlike decomp_symbol_map.py for
PSX), so decodes here are relative-offset only -- pass a base address
yourself with --base if you have one from a live PC-version debugger.

This is PC-binary struct ground truth, NOT the PSX structs from
decomp_struct_layout.py -- don't mix the two; field offsets/sizes can differ
between platforms even for a same-named concept.

Examples:
  python3 scripts/pc_struct_decoder.py VECTOR 0100000002000000030000000000000
  python3 scripts/pc_struct_decoder.py --list-structs
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pc_struct_layout import get_struct, get_struct_size, load_struct_layouts  # noqa: E402

_INT_TYPES = {
    "u8": False, "s8": True, "unsigned char": False, "signed char": True, "BYTE": False,
    "u16": False, "s16": True, "short": True, "unsigned short": False, "WORD": False,
    "u32": False, "s32": True, "int": True, "unsigned int": False, "long": True,
    "unsigned long": False, "DWORD": False, "UINT": False,
}


def decode(struct_name: str, raw: bytes, base_addr: int | None) -> list[str]:
    fields = get_struct(struct_name)
    out: list[str] = []
    if fields is None:
        out.append(f"[UNCONFIRMED: no struct named {struct_name!r} found in extracted PC headers]")
        return out

    total = get_struct_size(struct_name)
    if total is not None and len(raw) < total:
        out.append(f"[UNCONFIRMED: input is {len(raw)}B, struct documents size {total}B -- "
                   f"decode may run past provided bytes]")

    for f in fields:
        if f.size is None:
            out.append(f"[UNCONFIRMED: field size unresolved (custom/array type not in PRIMITIVE_SIZES)] "
                       f"off=0x{f.offset:X} {struct_name}.{f.name} ({f.ctype}{'*' if f.is_ptr else ''}{f.array})")
            continue
        chunk = raw[f.offset:f.offset + f.size]
        addr_prefix = f"0x{base_addr + f.offset:08X} " if base_addr is not None else ""
        if len(chunk) < f.size:
            out.append(f"[CONFIRMED] {addr_prefix}off=0x{f.offset:X} {struct_name}.{f.name} "
                       f"-- insufficient bytes ({len(chunk)}/{f.size})")
            continue
        if f.is_ptr:
            val_str = chunk.hex()
        elif f.ctype in _INT_TYPES and f.array in ("", "[1]"):
            val = int.from_bytes(chunk, "little", signed=_INT_TYPES[f.ctype])
            val_str = f"0x{val:X} ({val})"
        else:
            val_str = chunk.hex()
        out.append(f"[CONFIRMED] {addr_prefix}off=0x{f.offset:X} size={f.size}B "
                   f"{struct_name}.{f.name} ({f.ctype}{f.array}) = {val_str}")
    return out


def list_structs() -> list[str]:
    layouts = load_struct_layouts()
    out = []
    for name in sorted(layouts):
        size = get_struct_size(name)
        out.append(f"{name}: {len(layouts[name])} fields, "
                   f"documented size={'0x%X' % size if size else 'unknown'}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("struct", nargs="?", help="struct name, e.g. VECTOR, MATRIX, tBlendModeInfo")
    ap.add_argument("hex", nargs="?", help="raw bytes as hex")
    ap.add_argument("--base", help="base address (hex) to prefix decoded field offsets with")
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

    base_addr = int(args.base, 16) if args.base else None
    for line in decode(args.struct, raw, base_addr):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
