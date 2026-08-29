"""Parses external/makoureactor/src/core/field/Opcode.h struct definitions
into a flattened, byte-accurate field layout per opcode name.

This is structural extraction (same philosophy as field_pattern_finder.py /
duckstation_addr_advisor.py): the C++ structs are makoureactor's actual
on-wire parse of field-script opcode bytes, so a correctly-flattened layout
is [CONFIRMED] ground truth, not a semantic guess.

Ground truth source: external/makoureactor/src/core/field/Opcode.h
  - `STRUCTPACK(struct Opcode<NAME> : public Opcode<PARENT> { fields });`
  - Fields are C++ POD members read in declaration order, byte-packed
    (STRUCTPACK == #pragma pack(1), no padding).
  - Fields whose name starts with `_` (e.g. `_label`, `_badJump`) are
    editor-only bookkeeping set at runtime (see Opcode::setLabel /
    CaseOpcodeSetAttribute in Opcode.cpp) -- NOT present in the serialized
    byte stream. They are excluded from the on-wire layout here.
  - Pointer fields (e.g. `QByteArray *_data`) are variable-length payloads
    handled specially by the parser (e.g. KAWAI raw data); excluded too.

Not for: opcodes with no direct OpcodeKey-name struct match (e.g. the
`!`-suffixed assign variants, `2BYTE`, `CHAR`, `ANIM!1`/`CANM!1` family) --
those share a struct under a different C++ name; callers should treat a
missing lookup as [UNCONFIRMED: no direct struct match for this opcode name].
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OPCODE_H = REPO_ROOT / "external" / "makoureactor" / "src" / "core" / "field" / "Opcode.h"

# C type -> byte size for the fixed-width Qt integer typedefs makoureactor uses.
TYPE_SIZES = {
    "quint8": 1, "qint8": 1,
    "quint16": 2, "qint16": 2,
    "quint32": 4, "qint32": 4,
    "quint64": 8, "qint64": 8,
}

_FIELD_RE = re.compile(
    r"^\s*(quint8|qint8|quint16|qint16|quint32|qint32|quint64|qint64)\s+"
    r"(\w+)(?:\[(\d+)\])?\s*;(?:\s*//\s*(.*))?$"
)


class OpcodeField:
    __slots__ = ("name", "ctype", "size", "comment")

    def __init__(self, name: str, ctype: str, size: int, comment: str):
        self.name = name
        self.ctype = ctype
        self.size = size
        self.comment = comment

    def __repr__(self):
        c = f"  // {self.comment}" if self.comment else ""
        return f"{self.ctype} {self.name} ({self.size}B){c}"


def _parse_raw_structs(text: str) -> dict[str, tuple[str | None, list[OpcodeField]]]:
    """Returns {struct_suffix: (parent_suffix_or_None, own_fields)} for every
    `STRUCTPACK(struct Opcode<X> : public Opcode<Y> { ... });` in Opcode.h.
    Only direct `OpcodeXxx`-named structs are captured (not OpcodeKawaiXxx-
    style siblings, which are parsed separately if needed)."""
    out: dict[str, tuple[str | None, list[OpcodeField]]] = {}
    for m in re.finditer(
        r"struct\s+Opcode(\w+)\s*(?::\s*public\s+Opcode(\w+))?\s*\{([^}]*)\}",
        text,
    ):
        name, parent, body = m.group(1), m.group(2), m.group(3)
        fields: list[OpcodeField] = []
        for line in body.splitlines():
            fm = _FIELD_RE.match(line)
            if not fm:
                continue
            ctype, fname, arr_n, comment = fm.groups()
            base_size = TYPE_SIZES[ctype]
            size = base_size * int(arr_n) if arr_n else base_size
            fields.append(OpcodeField(fname, ctype, size, comment or ""))
        out[name] = (parent, fields)
    return out


def _flatten(name: str, raw: dict[str, tuple[str | None, list[OpcodeField]]]) -> list[OpcodeField]:
    """Walks the inheritance chain root-first, concatenating fields in
    declaration order (matches C++ memory layout for single inheritance with
    no virtuals), and drops runtime-only `_`-prefixed / pointer fields."""
    chain: list[str] = []
    cur: str | None = name
    seen = set()
    while cur is not None and cur in raw and cur not in seen:
        seen.add(cur)
        chain.append(cur)
        cur = raw[cur][0]
    chain.reverse()  # root (Base) first
    fields: list[OpcodeField] = []
    for struct_name in chain:
        for f in raw[struct_name][1]:
            if f.name.startswith("_"):
                continue  # editor-only, not on-wire (see module docstring)
            if f.name == "id":
                continue  # OpcodeBase.id is declared quint16 (OpcodeKey) but
                # actually read/written as a single byte -- see
                # Opcode::Opcode(const char*): `_opcode.id = OpcodeKey(quint8(data[0]))`
                # in Opcode.cpp. The 1-byte id is implicit at offset 0 for
                # every opcode and is handled separately by callers, not as
                # a params-struct field.
            fields.append(f)
    return fields


_layout_cache: dict[str, list[OpcodeField]] | None = None
_raw_cache: dict[str, tuple[str | None, list[OpcodeField]]] | None = None


def load_layouts() -> dict[str, list[OpcodeField]]:
    """Returns {OpcodeKey name (e.g. 'IFUB'): [OpcodeField, ...]} flattened
    on-wire PARAMETER field layouts. The 1-byte opcode id at offset 0
    (present in every opcode, see field_dat.py's decode_ops) is NOT
    included here -- these are the fields starting at offset 1, matching
    OPCODE_LENGTH[name] - 1 total bytes. Raises FileNotFoundError if
    external/makoureactor isn't cloned."""
    global _layout_cache, _raw_cache
    if _layout_cache is not None:
        return _layout_cache
    if not OPCODE_H.is_file():
        raise FileNotFoundError(f"{OPCODE_H} not found -- external/makoureactor not cloned?")
    text = OPCODE_H.read_text(encoding="utf-8", errors="ignore")
    raw = _parse_raw_structs(text)
    _raw_cache = raw
    layouts: dict[str, list[OpcodeField]] = {}
    for name in raw:
        layouts[name] = _flatten(name, raw)
    _layout_cache = layouts
    return layouts


def get_layout(opcode_name: str) -> list[OpcodeField] | None:
    """Returns the flattened field layout for an OPCODE_NAMES entry (e.g.
    'IFUB', 'MUSIC'), or None if there's no direct Opcode<NAME> struct."""
    return load_layouts().get(opcode_name)
