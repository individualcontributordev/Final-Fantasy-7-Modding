"""Extracts C struct field layouts from ergonomy-joe's PC (1998 retail .exe)
FF7 decompilation headers (external/ff7-chocobo, external/ff7-coaster --
`NEWFF7/ff7_structs.h`, identical shared header across both minigame
projects).

Ground truth source: this is a DIFFERENT binary/address-space than
external/ff7-decomp and external/ffvii (PSX). ergonomy_joe decompiled the PC
DirectX build (Windows 9x-era .exe/.dll), not the PSX executable -- so
addresses (elsewhere in these repos, e.g. `C_00404D80.cpp` filenames) are
0x00xxxxxx range, not 0x8000xxxx PSX RAM. This module only extracts struct
*layouts* (field offsets/types), which are binary-format facts independent
of which platform's executable they came from (many, e.g. VECTOR/SVECTOR/
MATRIX, mirror PSX GTE conventions and are near-identical across platforms;
others, e.g. tBlendModeInfo/D3D-suffixed types, are PC-only rendering
internals with no PSX equivalent).

Field offsets here are given directly as `/*HEX*/` comments with NO `0x`
prefix (unlike ff7-decomp's `/* 0xHEX */`) -- e.g. `/*00*/float x;`,
`/*1c*/int f_1c;`. Every matched field's offset is therefore [CONFIRMED]
straight from the source comment; this module does not need to compute
offsets by summing sizes like decomp_struct_layout.py does.

Structs are wrapped in `#if 1 ... #else ... #endif` (the `#else` branch
re-expresses the same fields as anonymous unions for debugging -- same
layout, not new information), so only the `#if 1` branch is parsed to avoid
duplicate/UNCONFIRMED-looking re-declarations of the same field.

Not for: PSX RAM globals/structs (use decomp_symbol_map.py /
decomp_struct_layout.py) or field-script opcodes (use
opcode_struct_layout.py).
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILES = [
    REPO_ROOT / "external" / "ff7-chocobo" / "NEWFF7" / "ff7_structs.h",
    REPO_ROOT / "external" / "ff7-coaster" / "NEWFF7" / "ff7_structs.h",
]

PRIMITIVE_SIZES = {
    "u8": 1, "s8": 1, "char": 1, "unsigned char": 1, "signed char": 1, "BYTE": 1,
    "u16": 2, "s16": 2, "short": 2, "unsigned short": 2, "WORD": 2,
    "u32": 4, "s32": 4, "int": 4, "unsigned int": 4, "long": 4, "unsigned long": 4,
    "float": 4, "DWORD": 4, "UINT": 4,
}

# Matches a `struct NAME { ... };` block, optionally with a `//size 0xHEX`
# or `//size HEX` trailing comment on the opening line.
_STRUCT_RE = re.compile(
    r"^struct\s+(?P<name>\w+)\s*\{(?:\s*//\s*size\s*0?x?(?P<size>[0-9A-Fa-f]+))?"
    r"(?P<body>.*?)^\};",
    re.DOTALL | re.MULTILINE,
)
_FIELD_RE = re.compile(
    r"^\s*/\*([0-9A-Fa-f]+)\*/\s*"
    r"((?:unsigned\s+|signed\s+|const\s+|struct\s+|volatile\s+)*[A-Za-z_]\w*)\s*"
    r"(\**)\s*(\w+)((?:\[[\w]*\])*)\s*;"
)


class PcField:
    __slots__ = ("name", "ctype", "is_ptr", "array", "offset", "size", "confirmed")

    def __init__(self, name, ctype, is_ptr, array, offset, size):
        self.name, self.ctype, self.is_ptr, self.array = name, ctype, is_ptr, array
        self.offset, self.size = offset, size
        self.confirmed = True  # offset always comes straight from a source /*HEX*/ comment

    def __repr__(self):
        sz = f"{self.size}B" if self.size is not None else "?B"
        return (f"[CONFIRMED] off=0x{self.offset:X} size={sz} "
                f"{self.ctype}{'*' if self.is_ptr else ''} {self.name}{self.array}")


def _strip_devel_branch(body: str) -> str:
    """Keeps only the `#if 1` branch, dropping `#else ... #endif` (the
    anonymous-union re-expression of the same fields)."""
    out_lines = []
    skipping = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#else"):
            skipping = True
            continue
        if stripped.startswith("#endif"):
            skipping = False
            continue
        if stripped.startswith("#if"):
            continue
        if not skipping:
            out_lines.append(line)
    return "\n".join(out_lines)


def _parse_struct_body(body: str) -> list[PcField]:
    fields: list[PcField] = []
    for line in _strip_devel_branch(body).splitlines():
        m = _FIELD_RE.match(line)
        if not m:
            continue
        off_hex, ctype, star, name, array = m.groups()
        ctype_clean = re.sub(r"^(unsigned|signed|const|struct|volatile)\s+", "", ctype.strip())
        base = 4 if star else PRIMITIVE_SIZES.get(ctype.strip(), PRIMITIVE_SIZES.get(ctype_clean))
        n = 1
        for dim in re.findall(r"\[([\w]*)\]", array):
            if dim.isdigit():
                n *= int(dim)
            else:
                n = None
                break
        size = None if (base is None or n is None) else base * n
        fields.append(PcField(name, ctype.strip(), bool(star), array or "", int(off_hex, 16), size))
    return fields


_cache: dict[str, list[PcField]] | None = None
_size_cache: dict[str, int] | None = None


def load_struct_layouts() -> dict[str, list[PcField]]:
    global _cache, _size_cache
    if _cache is not None:
        return _cache
    layouts: dict[str, list[PcField]] = {}
    sizes: dict[str, int] = {}
    for path in SOURCE_FILES:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in _STRUCT_RE.finditer(text):
            name = m.group("name")
            if name in layouts:
                continue  # both source files share the same header verbatim
            layouts[name] = _parse_struct_body(m.group("body"))
            if m.group("size"):
                sizes[name] = int(m.group("size"), 16)
    _cache, _size_cache = layouts, sizes
    return layouts


def get_struct(name: str) -> list[PcField] | None:
    return load_struct_layouts().get(name)


def get_struct_size(name: str) -> int | None:
    load_struct_layouts()
    return (_size_cache or {}).get(name)
