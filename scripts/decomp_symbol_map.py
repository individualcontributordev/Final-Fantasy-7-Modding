"""Extracts global-symbol -> RAM-address ground truth from external/ff7-decomp
and external/ffvii headers/sources.

Ground truth sources:
  - external/ff7-decomp: a decompilation of the retail PSX FF7 binary
    (gameplay code, e.g. `0x8009xxxx` savemap/battle/field state).
  - external/ffvii (github.com/Drahsid/ffvii): an independent, much earlier
    -stage decompilation of the PSX boot executable (`0x8001xxxx`-
    `0x8004xxxx` boot/kernel-adjacent code) -- disjoint address range from
    ff7-decomp, so both are merged into one lookup table without collisions.
    As of this extraction it's ~28 functions with real C bodies out of
    ~700+ declared (`func_<hex>`); the rest are `INCLUDE_ASM` stubs (address
    known, body not yet decompiled) -- tracked via `Symbol.decompiled`.

Global symbols the decompilers couldn't name are auto-labelled
`D_<8-hex-digit-address>` (data) or `func_<8-hex-digit-address>` (functions,
ffvii only) by their toolchain -- the hex digits ARE the confirmed PSX RAM
address the symbol lives at (e.g. `D_8009C6E4` -> 0x8009C6E4). Named symbols
(`g_Foo`, `SavedScriptIds`, ...) have no address encoded in the name; their
address is only known if a `// 0xADDRESS` trailing comment documents it
(e.g. the `Savemap` global). This mirrors the opcode_struct_layout.py
philosophy: structural extraction of an already-authoritative source, not a
semantic guess.

Use this to answer "what's at PSX address X" / "what decomp symbol should I
name this DuckStation watch on" ground-truth questions -- pair with
duckstation_addr_advisor.py rather than guessing from RAG/docs.

Not for: field-script opcode bytes (use opcode_struct_layout.py) or DAT/LGP
file offsets (use field_pattern_finder.py).
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DECOMP_ROOT = REPO_ROOT / "external" / "ff7-decomp"
FFVII_ROOT = REPO_ROOT / "external" / "ffvii"

# Headers/sources with the highest density of `extern` global declarations.
# (Not exhaustive of every .c/.h in the tree -- these are the ones carrying
# global RAM state, as opposed to function-local or purely-static decls.)
SOURCE_FILES = [
    "include/game.h",
    "src/battle/battle.h",
    "src/battle/battle_private.h",
    "src/world/world.h",
    "src/main/main_private.h",
    "src/menu/savemenu.h",
]

# ffvii (boot decompilation) declares every global/function up front in these
# two headers, regardless of whether the body has been decompiled yet.
FFVII_SOURCE_FILES = [
    "include/data_symbols.h",
    "include/function_symbols.h",
]

_ADDR_RE = re.compile(r"^(?:D_|func_)([0-9A-Fa-f]{8})$")
_EXTERN_RE = re.compile(
    r"extern\s+((?:const\s+|volatile\s+|struct\s+)?[A-Za-z_]\w*\s*\*?)\s+"
    r"(\w+)((?:\[[^\];]*\])*)\s*\([^;]*\)\s*;|"
    r"extern\s+((?:const\s+|volatile\s+|struct\s+)?[A-Za-z_]\w*\s*\*?)\s+"
    r"(\w+)((?:\[[^\];]*\])*)\s*;(?:\s*//\s*(.*))?"
)
_ADDR_COMMENT_RE = re.compile(r"0x[0-9A-Fa-f]{6,8}")
# A real (non-stub) definition: `<ret> func_XXXXXXXX(...) {` (INCLUDE_ASM
# stubs never have a `{` on the declaring line/macro).
_FFVII_FUNC_DEF_RE = re.compile(r"^[\w\s\*]+\b(func_[0-9A-Fa-f]{8})\s*\([^;{]*\)\s*\{", re.MULTILINE)


class Symbol:
    __slots__ = ("name", "ctype", "array", "comment", "address", "confirmed", "source_file", "decompiled")

    def __init__(self, name, ctype, array, comment, address, confirmed, source_file, decompiled=None):
        self.name = name
        self.ctype = ctype
        self.array = array
        self.comment = comment
        self.address = address
        self.confirmed = confirmed
        self.source_file = source_file
        self.decompiled = decompiled  # True/False for ffvii funcs, None = n/a (data or ff7-decomp)

    def __repr__(self):
        addr = f"0x{self.address:08X}" if self.address is not None else "??"
        tag = "CONFIRMED" if self.confirmed else "UNCONFIRMED"
        c = f"  // {self.comment}" if self.comment else ""
        d = ""
        if self.decompiled is True:
            d = "  [decompiled body]"
        elif self.decompiled is False:
            d = "  [INCLUDE_ASM stub, not yet decompiled]"
        return f"[{tag}] {addr} {self.ctype} {self.name}{self.array}{c}{d} ({self.source_file})"


def _resolve_address(name: str, comment: str) -> tuple[int | None, bool]:
    m = _ADDR_RE.match(name)
    if m:
        return int(m.group(1), 16), True
    # Named globals sometimes carry the address in a trailing comment
    # (e.g. `extern SaveWork Savemap; // 0x8009C6E4`).
    if comment:
        cm = _ADDR_COMMENT_RE.search(comment)
        if cm:
            return int(cm.group(0), 16), True
    return None, False


def _parse_file(path: Path, decomp_root: Path) -> list[Symbol]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    rel = str(path.relative_to(decomp_root))
    out = []
    for m in _EXTERN_RE.finditer(text):
        fn_ctype, fn_name, fn_array, ctype, name, array, comment = m.groups()
        if fn_name is not None:
            ctype, name, array, comment = fn_ctype, fn_name, fn_array, None
        comment = (comment or "").strip()
        address, confirmed = _resolve_address(name, comment)
        out.append(Symbol(name, ctype.strip(), array or "", comment, address, confirmed, rel))
    return out


def _ffvii_decompiled_names() -> set[str]:
    names: set[str] = set()
    src_dir = FFVII_ROOT / "src"
    if not src_dir.is_dir():
        return names
    for c_file in src_dir.rglob("*.c"):
        text = c_file.read_text(encoding="utf-8", errors="ignore")
        names.update(_FFVII_FUNC_DEF_RE.findall(text))
    return names


_cache: dict[str, Symbol] | None = None


def load_symbols() -> dict[str, Symbol]:
    """Returns {symbol_name: Symbol}, deduped (last declaration wins if a
    symbol is re-declared across headers -- rare but matches C semantics).
    Merges external/ff7-decomp (gameplay) and external/ffvii (boot) symbol
    tables; their address ranges don't overlap."""
    global _cache
    if _cache is not None:
        return _cache
    out: dict[str, Symbol] = {}
    for rel in SOURCE_FILES:
        path = DECOMP_ROOT / rel
        if not path.is_file():
            continue
        for sym in _parse_file(path, DECOMP_ROOT):
            out[sym.name] = sym

    decompiled_names = _ffvii_decompiled_names()
    for rel in FFVII_SOURCE_FILES:
        path = FFVII_ROOT / rel
        if not path.is_file():
            continue
        for sym in _parse_file(path, FFVII_ROOT):
            if sym.name.startswith("func_"):
                sym.decompiled = sym.name in decompiled_names
            out[sym.name] = sym
    _cache = out
    return out


def find_by_address(address: int) -> Symbol | None:
    """Exact-address lookup across all extracted symbols with a confirmed
    address."""
    for sym in load_symbols().values():
        if sym.address == address:
            return sym
    return None


def find_nearest_below(address: int) -> Symbol | None:
    """Returns the confirmed-address symbol with the highest address <=
    the given address -- useful for figuring out which global a raw
    DuckStation watch address falls inside (array/struct member offset)."""
    best = None
    for sym in load_symbols().values():
        if sym.address is not None and sym.address <= address:
            if best is None or sym.address > best.address:
                best = sym
    return best


def get(name: str) -> Symbol | None:
    return load_symbols().get(name)
