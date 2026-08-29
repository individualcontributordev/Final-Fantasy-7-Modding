"""Extracts C struct field layouts from external/ff7-decomp headers.

Ground truth source: `typedef struct { ... } Name;` blocks across the ff7
decompilation (game.h, world.h, battle_private.h, ...). These are matched
against the retail PSX binary, so a field's offset is either:
  - directly documented via a `/* 0xHEX */` leading comment (decomp authors
    already verified this against the disassembly) -> [CONFIRMED],
  - or computed here by summing preceding field sizes when no comment is
    present -> [CONFIRMED] only while every preceding field's size is known
    (primitive, pointer, or a previously-extracted struct with a documented
    `// size:0xHEX` comment); once an unknown-sized field is hit, every
    subsequent computed offset in that struct is [UNCONFIRMED: offset
    depends on a preceding field of unknown size] until the next explicit
    `/* 0xHEX */` comment resets the cursor.

This is the struct-layout counterpart to opcode_struct_layout.py, and pairs
with decomp_symbol_map.py (which gives you the base RAM address of e.g.
`Savemap`) to decode raw memory dumps field-by-field.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DECOMP_ROOT = REPO_ROOT / "external" / "ff7-decomp"

SOURCE_FILES = [
    "include/game.h",
    "src/battle/battle.h",
    "src/battle/battle_private.h",
    "src/world/world.h",
    "src/main/main_private.h",
]

PRIMITIVE_SIZES = {
    "u8": 1, "s8": 1, "char": 1, "unk_data": 1,
    "u16": 2, "s16": 2,
    "u32": 4, "s32": 4, "int": 4, "float": 4,
}

# Small, stable array-length macros used inside these structs (see game.h).
KNOWN_MACROS = {"MAX_PARTY_COUNT": 9, "MAX_INVENTORY_COUNT": 320, "MAX_MATERIA_COUNT": 200}

_STRUCT_RE = re.compile(
    r"typedef\s+struct(?:\s+\w+)?\s*\{(?P<body>.*?)\}\s*(?P<name>\w+)\s*;"
    r"(?:\s*//\s*size\s*:?\s*(?P<size>0x[0-9A-Fa-f]+))?",
    re.DOTALL,
)
_FIELD_RE = re.compile(
    r"^\s*(?:/\*\s*(0x[0-9A-Fa-f]+)\s*\*/\s*)?"
    r"((?:const\s+|volatile\s+|struct\s+)?\w+)\s*(\*?)\s*"
    r"(\w+)((?:\[[\w]*\])*)\s*;"
)


class DecompField:
    __slots__ = ("name", "ctype", "is_ptr", "array", "size", "offset", "confirmed", "comment")

    def __init__(self, name, ctype, is_ptr, array, size, offset, confirmed):
        self.name, self.ctype, self.is_ptr, self.array = name, ctype, is_ptr, array
        self.size, self.offset, self.confirmed = size, offset, confirmed

    def __repr__(self):
        off = f"0x{self.offset:X}" if self.offset is not None else "??"
        sz = f"{self.size}B" if self.size is not None else "?B"
        tag = "CONFIRMED" if self.confirmed else "UNCONFIRMED"
        return f"[{tag}] off={off} size={sz} {self.ctype}{'*' if self.is_ptr else ''} {self.name}{self.array}"


def _array_count(array_str: str) -> int | None:
    if not array_str:
        return 1
    total = 1
    for dim in re.findall(r"\[([\w]*)\]", array_str):
        if dim == "":
            return None  # flexible array member, unknown size
        if dim.isdigit():
            total *= int(dim)
        elif dim in KNOWN_MACROS:
            total *= KNOWN_MACROS[dim]
        else:
            return None
    return total


def _field_size(ctype: str, is_ptr: bool, array_str: str, struct_sizes: dict[str, int]) -> int | None:
    if is_ptr:
        base = 4
    elif ctype in PRIMITIVE_SIZES:
        base = PRIMITIVE_SIZES[ctype]
    elif ctype in struct_sizes:
        base = struct_sizes[ctype]
    else:
        return None
    n = _array_count(array_str)
    return None if n is None else base * n


def _parse_struct_body(body: str, struct_sizes: dict[str, int]) -> list[DecompField]:
    fields: list[DecompField] = []
    cursor = 0  # None once we lose track (unknown-sized field seen)
    for line in body.splitlines():
        m = _FIELD_RE.match(line)
        if not m:
            continue
        off_comment, ctype, star, name, array = m.groups()
        ctype = re.sub(r"^(const|volatile|struct)\s+", "", ctype.strip())
        if ctype in ("typedef", "struct"):
            continue
        size = _field_size(ctype, bool(star), array, struct_sizes)
        if off_comment is not None:
            offset = int(off_comment, 16)
            confirmed = True
            cursor = offset + size if size is not None else None
        else:
            offset = cursor
            confirmed = cursor is not None
            if cursor is not None and size is not None:
                cursor = cursor + size
            else:
                cursor = None
        fields.append(DecompField(name, ctype, bool(star), array or "", size, offset, confirmed))
    return fields


_layout_cache: dict[str, list[DecompField]] | None = None
_size_cache: dict[str, int] | None = None


def load_struct_layouts() -> dict[str, list[DecompField]]:
    global _layout_cache, _size_cache
    if _layout_cache is not None:
        return _layout_cache
    struct_sizes: dict[str, int] = {}
    bodies: dict[str, str] = {}
    for rel in SOURCE_FILES:
        path = DECOMP_ROOT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in _STRUCT_RE.finditer(text):
            name = m.group("name")
            bodies[name] = m.group("body")
            if m.group("size"):
                struct_sizes[name] = int(m.group("size"), 16)
    layouts = {name: _parse_struct_body(body, struct_sizes) for name, body in bodies.items()}
    _layout_cache = layouts
    _size_cache = struct_sizes
    return layouts


def get_struct(name: str) -> list[DecompField] | None:
    return load_struct_layouts().get(name)


def get_struct_size(name: str) -> int | None:
    load_struct_layouts()
    return (_size_cache or {}).get(name)
