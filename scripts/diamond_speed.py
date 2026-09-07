#!/usr/bin/env python3
"""Find and change Diamond Weapon's world-map movement speed.

WORLD.BIN.dec is the engine overlay. Diamond Weapon's march is a worldscript
immediate in WORLD/WM{0-3}.EV: PUSH_CONSTANT <speed> then SET_SPEED (0x303)
or SET_WALK_SPEED (0x336). Model id 10 is diamond_weapon.

Scan every EV, then patch the reported offset into a same-size copy for ISO
inject. A save state taken after spawn keeps the old RAM speed.
"""
from __future__ import annotations

import argparse
import struct
import sys
from bisect import bisect_right
from pathlib import Path

# Worldscript opcodes are 16-bit little-endian words. Immediate values sit
# in the word after PUSH_CONSTANT, not inside the opcode itself.
PUSH_CONSTANT = 0x110
SET_SPEED = 0x303  # Entity.set_movespeed — ignores walkmesh
SET_WALK_SPEED = 0x336  # Entity.set_walk_speed — follows walkmesh
SPEED_OPCODES = {SET_SPEED: "SET_SPEED", SET_WALK_SPEED: "SET_WALK_SPEED"}

# landscaper modelsMapping: 10 = diamond_weapon
DIAMOND_WEAPON = 10

# Call table is 256 x 4-byte entries (header + script offset). Bytecode
# starts at 0x400; script offsets in the table are in 16-bit words from there.
TABLE_START = 0x000
TABLE_END = 0x400
CODE_BASE = 0x400

SYSTEM = 0
MODEL = 1
MESH = 2


def read_word(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def read_functions(data: bytes) -> list[dict]:
    """Parse the EV call table into owners we can attribute bytecode to.

    Header bits: type in the top 2, model id in bits 8–13 for model functions,
    function id in the low 8. The first table slot is a dummy (zeros).
    """
    functions = []
    for table_offset in range(TABLE_START + 4, TABLE_END, 4):
        header, script_offset = struct.unpack_from("<HH", data, table_offset)
        if header == 0xFFFF:
            continue
        functions.append(
            {
                "type": header >> 14,
                "id": header & 0xFF,
                "model": (header >> 8) & 0x3F,
                "offset": CODE_BASE + script_offset * 2,
            }
        )
    return functions


def describe_owner(functions: list[dict], instruction_offset: int) -> str:
    """Map a bytecode address to the last function whose body starts at or before it.

    Aliases share an offset, so several names can print for one site.
    """
    starts = sorted({fn["offset"] for fn in functions})
    index = bisect_right(starts, instruction_offset) - 1
    if index < 0:
        return "unknown"

    function_start = starts[index]
    descriptions = []
    for owner in functions:
        if owner["offset"] != function_start:
            continue
        if owner["type"] == MODEL:
            name = (
                "diamond_weapon"
                if owner["model"] == DIAMOND_WEAPON
                else f"model_{owner['model']}"
            )
            descriptions.append(f"{name}:function_{owner['id']}")
        elif owner["type"] == SYSTEM:
            descriptions.append(f"system:function_{owner['id']}")
        else:
            descriptions.append(f"mesh:function_{owner['id']}")
    return ", ".join(descriptions) or "unknown"


def scan(path: Path) -> int:
    data = path.read_bytes()
    if len(data) < CODE_BASE + 6:
        print(f"{path}: too small to be an EV file", file=sys.stderr)
        return 0

    functions = read_functions(data)
    found = 0

    # Step by 2: opcodes are aligned words. A hit is PUSH_CONSTANT, a 16-bit
    # immediate, then a speed opcode — the compile form of Entity.set_*speed(N).
    for push_offset in range(CODE_BASE, len(data) - 5, 2):
        if read_word(data, push_offset) != PUSH_CONSTANT:
            continue
        speed = read_word(data, push_offset + 2)
        opcode = read_word(data, push_offset + 4)
        name = SPEED_OPCODES.get(opcode)
        if name is None:
            continue

        owner = describe_owner(functions, push_offset)
        immediate_offset = push_offset + 2
        diamond = "  <-- diamond_weapon" if "diamond_weapon" in owner else ""
        print(
            f"{path.name}  offset=0x{immediate_offset:X}  "
            f"speed={speed}  opcode={name}  owner={owner}{diamond}"
        )
        found += 1

    if not found:
        print(f"{path}: no constant movement-speed instructions")
    return found


def patch(input_path: Path, offset: int, new_speed: int, output_path: Path) -> None:
    if not 0 <= new_speed <= 255:
        raise SystemExit("speed must be 0–255")

    data = bytearray(input_path.read_bytes())
    if offset < 2 or offset + 2 > len(data):
        raise SystemExit(f"offset 0x{offset:X} is outside the file")

    # Guard against poking an unrelated word: the site must still be
    # PUSH_CONSTANT <this word> SET_SPEED/SET_WALK_SPEED.
    previous_opcode = read_word(data, offset - 2)
    next_opcode = read_word(data, offset + 2)
    if previous_opcode != PUSH_CONSTANT:
        raise SystemExit(f"0x{offset:X} is not a PUSH_CONSTANT value")
    if next_opcode not in SPEED_OPCODES:
        raise SystemExit(f"0x{offset:X} is not followed by a speed opcode")

    old_speed = read_word(data, offset)
    struct.pack_into("<H", data, offset, new_speed)
    output_path.write_bytes(data)
    print(f"wrote {output_path}: speed {old_speed} -> {new_speed} at 0x{offset:X}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan or poke Diamond Weapon worldscript movement speed in WM*.EV"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    scan_p = sub.add_parser("scan", help="list PUSH_CONSTANT speed sites")
    scan_p.add_argument("ev", type=Path, nargs="+", help="WM*.EV files")

    patch_p = sub.add_parser("patch", help="write a same-size EV with a new speed")
    patch_p.add_argument("ev", type=Path, help="source WM*.EV")
    patch_p.add_argument("offset", help="immediate offset from scan (hex or decimal)")
    patch_p.add_argument("speed", type=int, help="new speed 0–255")
    patch_p.add_argument("out", type=Path, help="output EV (do not overwrite the source)")

    args = parser.parse_args()
    if args.cmd == "scan":
        total = sum(scan(path) for path in args.ev)
        if total == 0:
            sys.exit(1)
        return

    patch(args.ev, int(args.offset, 0), args.speed, args.out)


if __name__ == "__main__":
    main()
