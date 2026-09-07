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

RETURN = 0x203
# 0x204-0x22F call system function (opcode - 0x204).
CALL_FN_BASE = 0x204
CALL_FN_LAST = 0x22F

# mnemonic + how many following words are inline operands, mirrored from
# ff7-landscaper's opcode table. Only these eleven carry an operand word.
OPCODES: dict[int, tuple[str, int]] = {
    0x000: ("NOP", 0),
    0x015: ("NEG", 0),
    0x017: ("NOT", 0),
    0x018: ("DIST_POINT", 0),
    0x019: ("DIST_MODEL", 0),
    0x01B: ("DIR_POINT", 0),
    0x030: ("MUL", 0),
    0x040: ("ADD", 0),
    0x041: ("SUB", 0),
    0x050: ("SHL", 0),
    0x051: ("SHR", 0),
    0x060: ("LT", 0),
    0x061: ("GT", 0),
    0x062: ("LE", 0),
    0x063: ("GE", 0),
    0x070: ("EQ", 0),
    0x080: ("AND", 0),
    0x0A0: ("OR", 0),
    0x0B0: ("LAND", 0),
    0x0C0: ("LOR", 0),
    0x0E0: ("WRITE", 0),
    0x100: ("RESET", 0),
    0x110: ("PUSH_CONSTANT", 1),
    0x114: ("PUSH_SAVEMAP_BIT", 1),
    0x117: ("PUSH_SPECIAL_BIT", 1),
    0x118: ("PUSH_SAVEMAP_BYTE", 1),
    0x119: ("PUSH_TEMP_BYTE", 1),
    0x11B: ("PUSH_SPECIAL_BYTE", 1),
    0x11C: ("PUSH_SAVEMAP_WORD", 1),
    0x11D: ("PUSH_TEMP_WORD", 1),
    0x11F: ("PUSH_SPECIAL_WORD", 1),
    0x200: ("GOTO", 1),
    0x201: ("GOTO_IF_FALSE", 1),
    0x203: ("RETURN", 0),
    0x300: ("LOAD_MODEL", 0),
    0x302: ("SET_PLAYER", 0),
    0x303: ("SET_SPEED", 0),
    0x304: ("SET_DIR", 0),
    0x305: ("WAIT_FRAMES", 0),
    0x306: ("WAIT", 0),
    0x307: ("SET_CONTROLS", 0),
    0x308: ("SET_MESH_POS", 0),
    0x309: ("SET_LOCAL_POS", 0),
    0x30A: ("SET_VERT_SPEED", 0),
    0x30B: ("SET_Y_OFFSET", 0),
    0x30C: ("ENTER_VEHICLE", 0),
    0x30D: ("STOP", 0),
    0x30E: ("PLAY_ANIM", 0),
    0x310: ("SET_POINT", 0),
    0x311: ("SET_POINT_MESH", 0),
    0x312: ("SET_POINT_LOCAL", 0),
    0x313: ("SET_TERRAIN_COLOR", 0),
    0x314: ("SET_RADIUS", 0),
    0x315: ("SET_SKY_TOP", 0),
    0x316: ("SET_SKY_BOTTOM", 0),
    0x317: ("BATTLE", 0),
    0x318: ("ENTER_FIELD", 0),
    0x319: ("SET_MAP_OPTIONS", 0),
    0x31B: ("NOP", 0),
    0x31C: ("SET_CAM_LOCK", 0),
    0x31D: ("PLAY_SFX", 0),
    0x31F: ("SET_CAM_SPEED", 0),
    0x320: ("RESET_ZOLOM", 0),
    0x321: ("FACE_POINT", 0),
    0x324: ("SET_WINDOW_SIZE", 0),
    0x325: ("SET_MESSAGE", 0),
    0x326: ("SET_PROMPT", 0),
    0x327: ("WAIT_PROMPT", 0),
    0x328: ("SET_MOVE_DIR", 0),
    0x329: ("SET_CAM_TILT", 0),
    0x32A: ("SET_CAM_ZOOM", 0),
    0x32B: ("SET_ENCOUNTERS", 0),
    0x32C: ("SET_WINDOW_STYLE", 0),
    0x32D: ("WAIT_WINDOW", 0),
    0x32E: ("WAIT_DISMISS", 0),
    0x32F: ("SET_PLAYER_DIR", 0),
    0x330: ("SET_ENTITY", 0),
    0x331: ("EXIT_VEHICLE", 0),
    0x332: ("CHOCOBO_RUN", 0),
    0x333: ("FACE_MODEL", 0),
    0x334: ("WAIT_FUNC", 0),
    0x336: ("SET_WALK_SPEED", 0),
    0x339: ("HIDE_MODEL", 0),
    0x33A: ("SET_VERT_SPEED2", 0),
    0x33B: ("FADE_OUT", 0),
    0x33C: ("EXIT_UNDERWATER", 0),
    0x33D: ("SET_FIELD_ENTRY_ID", 0),
    0x33E: ("PLAY_MUSIC", 0),
    0x347: ("MOVE_TO_MODEL", 0),
    0x348: ("FADE_IN", 0),
    0x349: ("SET_PROGRESS", 0),
    0x34A: ("PLAY_LAYER_ANIM", 0),
    0x34B: ("SET_CHOCOBO", 0),
    0x34C: ("SET_SUBMARINE", 0),
    0x34D: ("SHOW_LAYER", 0),
    0x34E: ("HIDE_LAYER", 0),
    0x34F: ("SET_Y_POS", 0),
    0x350: ("SHOW_METEOR", 0),
    0x351: ("SET_MUSIC_VOL", 0),
    0x352: ("SHAKE_CAM", 0),
    0x353: ("ADJUST_POS", 0),
    0x354: ("SET_VEHICLE_USABLE", 0),
    0x355: ("SET_BATTLE_TIMER", 0),
}


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


def disassemble(data: bytes, start: int, limit: int = 4096) -> list[str]:
    """Linear listing from a function entry up to and including its RETURN.

    Worldscript has no function length field, so a runaway listing means the
    entry offset was wrong rather than that the function is huge.
    """
    lines: list[str] = []
    offset = start

    while offset + 2 <= len(data) and len(lines) < limit:
        opcode = read_word(data, offset)
        line_offset = offset
        offset += 2

        if CALL_FN_BASE <= opcode <= CALL_FN_LAST:
            lines.append(f"  0x{line_offset:04X}: CALL_FN_{opcode - CALL_FN_BASE}")
            continue

        entry = OPCODES.get(opcode)
        if entry is None:
            lines.append(f"  0x{line_offset:04X}: ??? 0x{opcode:03X}")
            continue

        mnemonic, operand_words = entry
        operands = []
        for _ in range(operand_words):
            if offset + 2 > len(data):
                break
            operands.append(read_word(data, offset))
            offset += 2

        text = " ".join(f"0x{value:X}" for value in operands)
        lines.append(f"  0x{line_offset:04X}: {mnemonic} {text}".rstrip())

        if opcode == RETURN:
            break

    return lines


def dump(path: Path, model_id: int | None) -> None:
    """Print every function owned by one model (or all functions)."""
    data = path.read_bytes()
    functions = read_functions(data)

    # Aliases share a body; list each entry offset once.
    seen: set[int] = set()
    for fn in functions:
        is_model_fn = fn["type"] == MODEL
        wanted = model_id is None or (is_model_fn and fn["model"] == model_id)
        if not wanted:
            continue

        owner = describe_owner(functions, fn["offset"])
        print(f"{path.name}  {owner}  entry=0x{fn['offset']:04X}")
        if fn["offset"] in seen:
            print("  (alias -- body listed above)")
            continue

        seen.add(fn["offset"])
        for line in disassemble(data, fn["offset"]):
            print(line)
        print()


def poke(
    input_path: Path,
    offset: int,
    new_value: int,
    output_path: Path,
    expect: int,
) -> None:
    """Write one 16-bit word, refusing unless it currently holds ``expect``.

    Speed immediates have ``patch``; this is for the rest of a script, where a
    wrong offset silently corrupts the opcode stream instead of erroring.
    """
    if not 0 <= new_value <= 0xFFFF:
        raise SystemExit("value must fit in 16 bits")

    data = bytearray(input_path.read_bytes())
    if offset + 2 > len(data):
        raise SystemExit(f"offset 0x{offset:X} is outside the file")

    current = read_word(data, offset)
    if current != expect:
        raise SystemExit(
            f"0x{offset:X} holds 0x{current:X}, expected 0x{expect:X} -- "
            "wrong file or wrong offset"
        )

    struct.pack_into("<H", data, offset, new_value)
    output_path.write_bytes(data)
    print(f"wrote {output_path}: 0x{current:X} -> 0x{new_value:X} at 0x{offset:X}")


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

    dump_p = sub.add_parser("dump", help="disassemble a model's worldscript functions")
    dump_p.add_argument("ev", type=Path, help="WM*.EV file")
    dump_p.add_argument(
        "--model",
        type=int,
        default=DIAMOND_WEAPON,
        help=f"model id (default {DIAMOND_WEAPON} = diamond_weapon)",
    )
    dump_p.add_argument(
        "--all",
        action="store_true",
        help="every function in the file, not just one model",
    )

    poke_p = sub.add_parser("poke", help="write one guarded 16-bit word")
    poke_p.add_argument("ev", type=Path, help="source WM*.EV")
    poke_p.add_argument("offset", help="byte offset (hex or decimal)")
    poke_p.add_argument("value", help="new word value (hex or decimal)")
    poke_p.add_argument("out", type=Path, help="output EV")
    poke_p.add_argument(
        "--expect",
        required=True,
        help="word that must currently be there",
    )

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

    if args.cmd == "dump":
        dump(args.ev, None if args.all else args.model)
        return

    if args.cmd == "poke":
        poke(
            args.ev,
            int(args.offset, 0),
            int(args.value, 0),
            args.out,
            int(args.expect, 0),
        )
        return

    patch(args.ev, int(args.offset, 0), args.speed, args.out)


if __name__ == "__main__":
    main()
