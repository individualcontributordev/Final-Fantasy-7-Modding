"""Extracts world-map (`wm0.ev`/`wm2.ev`/`wm3.ev`) worldscript opcode ground
truth from external/ff7-landscaper's TypeScript worldscript engine.

Ground truth source: external/ff7-landscaper/src/ff7/worldscript/opcodes.ts --
a hand-curated, already-shipping opcode table (`Opcodes: Record<number,
OpcodeDefinition>`) used by Landscaper's real decompiler/compiler for FF7's
world-map bytecode. This is a different VM from field-script opcodes
(makoureactor/opcode_struct_layout.py): world-map bytecode is stack-based,
16-bit-word-granular (opcode id and every code-param are 2 bytes, confirmed
via evfile.ts's `decodeOpcodes`/`totalSize += def.codeParams * 2`), not the
byte-oriented, fixed-struct field-script format.

On-wire shape per instruction: `<opcode_id:u16le> <codeParams * u16le>`.
`stackParams` are NOT on-wire bytes -- they're values popped from the VM's
runtime evaluation stack, so they carry no byte-layout info here (unlike
field opcodes' inline bank/value bytes). Only `codeParams` (count) affects
how many words to consume after the opcode id.

Special case (confirmed in evfile.ts): opcode ids 0x204-0x22F are not
individually listed in the table -- they're a contiguous `CALL_FN_<n>` range
(`n = opcode_id - 0x204`), decoded arithmetically rather than by table
lookup.

Use this to identify/label raw world-map script words -- pair with
opcode_struct_layout.py (field scripts) rather than confusing the two VMs.

Not for: field-script opcode bytes (use opcode_struct_layout.py) or PSX RAM
globals (use decomp_symbol_map.py).
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OPCODES_TS = REPO_ROOT / "external" / "ff7-landscaper" / "src" / "ff7" / "worldscript" / "opcodes.ts"

CALL_FN_LOW = 0x204
CALL_FN_HIGH = 0x22F

_BLOCK_START_RE = re.compile(r"^\s*(0x[0-9A-Fa-f]+):\s*\{", re.MULTILINE)
_FIELD_RE = {
    "name": re.compile(r'name:\s*"([^"]*)"'),
    "mnemonic": re.compile(r"mnemonic:\s*Mnemonic\.(\w+)"),
    "namespace": re.compile(r"namespace:\s*Namespace\.(\w+)"),
    "stackParams": re.compile(r"stackParams:\s*(\d+)"),
    "codeParams": re.compile(r"codeParams:\s*(\d+)"),
    "description": re.compile(r'description:\s*"([^"]*)"'),
    "pushesResult": re.compile(r"pushesResult:\s*(true|false)"),
}


class WorldmapOpcode:
    __slots__ = ("opcode_id", "name", "mnemonic", "namespace", "stack_params",
                 "code_params", "description", "pushes_result", "confirmed")

    def __init__(self, opcode_id, name, mnemonic, namespace, stack_params,
                 code_params, description, pushes_result):
        self.opcode_id = opcode_id
        self.name = name
        self.mnemonic = mnemonic
        self.namespace = namespace
        self.stack_params = stack_params
        self.code_params = code_params
        self.description = description
        self.pushes_result = pushes_result
        self.confirmed = True  # directly sourced from Landscaper's shipping opcode table

    @property
    def wire_size_words(self) -> int:
        """1 (opcode id) + codeParams words. CALL_FN_ ids are always size 1
        (the function number is baked into the opcode id itself)."""
        if self.mnemonic == "CALL_FN_":
            return 1
        return 1 + self.code_params

    def __repr__(self):
        tag = "CONFIRMED"
        return (f"[{tag}] 0x{self.opcode_id:03X} {self.mnemonic} ({self.namespace}.{self.name})"
                f" stackParams={self.stack_params} codeParams={self.code_params}"
                f" wireWords={self.wire_size_words} -- {self.description}")


def _find_matching_brace(text: str, open_idx: int) -> int:
    depth = 0
    i = open_idx
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("unbalanced braces")


def _extract(text: str) -> dict[int, WorldmapOpcode]:
    out: dict[int, WorldmapOpcode] = {}
    for m in _BLOCK_START_RE.finditer(text):
        opcode_id = int(m.group(1), 16)
        brace_open = text.index("{", m.end() - 1)
        brace_close = _find_matching_brace(text, brace_open)
        block = text[brace_open:brace_close]

        def field(key, default=None, cast=str):
            fm = _FIELD_RE[key].search(block)
            if not fm:
                return default
            return cast(fm.group(1))

        out[opcode_id] = WorldmapOpcode(
            opcode_id=opcode_id,
            name=field("name", ""),
            mnemonic=field("mnemonic", ""),
            namespace=field("namespace", ""),
            stack_params=field("stackParams", 0, int),
            code_params=field("codeParams", 0, int),
            description=field("description", ""),
            pushes_result=field("pushesResult", "false") == "true",
        )
    return out


_cache: dict[int, WorldmapOpcode] | None = None


def load_opcodes() -> dict[int, WorldmapOpcode]:
    global _cache
    if _cache is not None:
        return _cache
    if not OPCODES_TS.is_file():
        _cache = {}
        return _cache
    text = OPCODES_TS.read_text(encoding="utf-8", errors="ignore")
    _cache = _extract(text)
    return _cache


def get(opcode_id: int) -> WorldmapOpcode | None:
    """Looks up an opcode by its 2-byte on-wire id, handling the
    CALL_FN_0..CALL_FN_43 (0x204-0x22F) contiguous range specially since
    those aren't individually listed in the source table."""
    if CALL_FN_LOW <= opcode_id <= CALL_FN_HIGH:
        base = load_opcodes().get(CALL_FN_LOW)
        if base is None:
            return None
        fn_number = opcode_id - CALL_FN_LOW
        return WorldmapOpcode(
            opcode_id=opcode_id, name=f"call_function_{fn_number}",
            mnemonic=f"CALL_FN_{fn_number}", namespace=base.namespace,
            stack_params=base.stack_params, code_params=0,
            description=f"{base.description} (function #{fn_number})",
            pushes_result=base.pushes_result,
        )
    return load_opcodes().get(opcode_id)


def find_by_mnemonic(mnemonic: str) -> WorldmapOpcode | None:
    for op in load_opcodes().values():
        if op.mnemonic == mnemonic:
            return op
    return None
