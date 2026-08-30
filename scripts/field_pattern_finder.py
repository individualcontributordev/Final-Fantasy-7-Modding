#!/usr/bin/env python3
"""Find opcodes/byte patterns in a FIELD/*.DAT with CONFIRMED/UNCONFIRMED tags.

When to use:
  - You need a script-slot offset for a patch and want it derived from the
    real section/opcode parse (field_dat.py) instead of guessed by eye.
  - Confirming whether a raw byte sequence actually lands on an opcode
    boundary before treating it as "the opcode you're looking for".

See scripts/README.md "Verification contract" for what CONFIRMED/UNCONFIRMED
mean here:
  - Opcode-name search walks field_dat.py's decode_ops() per script slot --
    every hit is [CONFIRMED] (ground-truth structural parse).
  - Raw hex search finds byte offsets first, then checks whether each hit
    lands on a decoded-opcode boundary in that slot. Boundary-aligned hits
    are [CONFIRMED]; others are [UNCONFIRMED: not opcode-boundary aligned]
    (could be inside an opcode's operand bytes, coincidental).

Not for: RAM/DuckStation addresses (use duckstation_addr_advisor.py).

Examples:
  python3 scripts/field_pattern_finder.py pristine:1 --field LOST2 --opcode MUSIC
  python3 scripts/field_pattern_finder.py csr:1 --field DEL1 --hex f052
  python3 scripts/field_pattern_finder.py file:/tmp/LOST2.DAT --opcode JMPF
  python3 scripts/field_pattern_finder.py pristine:1 --field LOST2 --opcode MUSIC --decode-fields
  python3 scripts/field_pattern_finder.py csr:1 --field-id 191 --dump-all | grep IFSW

Sides: path | pristine:N | csr:N | file:PATH (same as compare_field_dat.py).
Env: FF7_PRISTINE_DIR, FF7_CSR_ROOT.

--field-id N: resolve a numeric field ID to its map name via the CSR repo's
scripts/field_maplist.py (requires FF7_CSR_ROOT or the default sibling
checkout ~/Final-Fantasy-7-CSR). Alternative to --field NAME.

--dump-all: print every decoded opcode in every script slot (every line is
[CONFIRMED], same structural parse as --opcode/--hex), for grepping instead
of searching one mnemonic/pattern at a time.

--decode-fields (with --opcode only): pipes each hit's raw param bytes
through opcode_struct_decoder.py and prints the named-field breakdown
indented under the hit, so a single command gives you both "where" and
"what's in it" instead of needing two separate tool calls.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from disc_sources import (  # noqa: E402
    field_iso_path,
    load_csr_image,
    load_pristine_image,
)
from field_dat import decode_ops, load_field_dat  # noqa: E402
from opcode_struct_decoder import decode as decode_opcode_fields  # noqa: E402
from psx_mode2_iso import extract_file  # noqa: E402

_img_cache: dict[tuple[str, int], bytes] = {}


def _image(kind: str, disc: int) -> bytes:
    key = (kind, disc)
    if key not in _img_cache:
        loader = load_pristine_image if kind == "pristine" else load_csr_image
        _img_cache[key] = bytes(loader(disc))
    return _img_cache[key]


def resolve_dat_bytes(spec: str, field: str | None) -> tuple[bytes, str]:
    if spec.startswith("file:"):
        path = Path(spec[5:]).expanduser()
        return path.read_bytes(), str(path)
    if ":" in spec and not Path(spec).exists():
        kind, d_s = spec.split(":", 1)
        kind = kind.lower()
        if kind not in ("pristine", "csr"):
            raise ValueError(f"unknown source kind: {kind!r}")
        if not field:
            raise ValueError("--field required with pristine:/csr: sources")
        disc = int(d_s)
        img = _image(kind, disc)
        raw = extract_file(img, field_iso_path(field))
        return raw, f"{spec} {field}"
    path = Path(spec).expanduser()
    return path.read_bytes(), str(path)


def find_opcode(fd, opcode_name: str, decode_fields: bool = False) -> list[str]:
    out: list[str] = []
    for slot in fd.scripts:
        pos = 0
        for raw, name in decode_ops(slot.raw):
            if name == opcode_name or name.startswith(opcode_name + "."):
                abs_off = slot.start + pos
                out.append(
                    f"[CONFIRMED] {slot.entity} slot={slot.slot} "
                    f"script_off=0x{pos:X} section0_off=0x{abs_off:X} "
                    f"bytes={raw.hex()}"
                )
                if decode_fields:
                    # raw includes the opcode id byte at offset 0; the field
                    # decoder expects only the param bytes after it.
                    mnemonic = name.split(".", 1)[0]
                    for field_line in decode_opcode_fields(mnemonic, raw[1:]):
                        out.append(f"    {field_line}")
            pos += len(raw)
    return out


def resolve_field_id(field_id: int) -> str:
    """Look up a numeric field ID's map name via the CSR repo's field_maplist.py."""
    import os

    csr_root = Path(os.environ.get("FF7_CSR_ROOT", "~/Final-Fantasy-7-CSR")).expanduser()
    maplist_path = csr_root / "scripts" / "field_maplist.py"
    if not maplist_path.is_file():
        raise ValueError(
            f"can't resolve --field-id: {maplist_path} not found "
            "(set FF7_CSR_ROOT or use --field NAME instead)"
        )
    sys.path.insert(0, str(maplist_path.parent))
    from field_maplist import MAPLIST  # noqa: E402  (dynamic path insert above)

    if field_id < 0 or field_id >= len(MAPLIST):
        raise ValueError(f"field id {field_id} out of range (0..{len(MAPLIST) - 1})")
    return MAPLIST[field_id]


def dump_all(fd) -> list[str]:
    out: list[str] = []
    for slot in fd.scripts:
        pos = 0
        for raw, name in decode_ops(slot.raw):
            abs_off = slot.start + pos
            out.append(
                f"[CONFIRMED] {slot.entity} slot={slot.slot} "
                f"script_off=0x{pos:X} section0_off=0x{abs_off:X} "
                f"op={name} bytes={raw.hex()}"
            )
            pos += len(raw)
    return out


def find_hex(fd, pattern: bytes) -> list[str]:
    out: list[str] = []
    for slot in fd.scripts:
        blob = slot.raw
        idx = 0
        while True:
            hit = blob.find(pattern, idx)
            if hit == -1:
                break
            idx = hit + 1
            # Check opcode-boundary alignment by re-walking decode_ops.
            aligned = False
            pos = 0
            for raw, _name in decode_ops(blob):
                if pos == hit:
                    aligned = True
                    break
                if pos > hit:
                    break
                pos += len(raw)
            tag = "[CONFIRMED]" if aligned else "[UNCONFIRMED: not opcode-boundary aligned]"
            abs_off = slot.start + hit
            out.append(
                f"{tag} {slot.entity} slot={slot.slot} script_off=0x{hit:X} "
                f"section0_off=0x{abs_off:X} bytes={pattern.hex()}"
            )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="path | pristine:N | csr:N | file:PATH")
    ap.add_argument("--field", help="field map name, required with pristine:/csr:")
    ap.add_argument("--field-id", type=int,
                     help="numeric field ID (alternative to --field, resolved "
                          "via CSR repo's field_maplist.py)")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--opcode", help="opcode mnemonic, e.g. MUSIC, JMPF")
    group.add_argument("--hex", help="raw byte pattern, e.g. f052")
    group.add_argument("--dump-all", action="store_true",
                        help="print every decoded opcode in every script slot")
    ap.add_argument("--decode-fields", action="store_true",
                     help="with --opcode: also print each hit's named-field "
                          "breakdown via opcode_struct_decoder.py")
    args = ap.parse_args()

    if args.decode_fields and not args.opcode:
        print("error: --decode-fields requires --opcode", file=sys.stderr)
        return 1

    field = args.field
    if args.field_id is not None:
        if field:
            print("error: use either --field or --field-id, not both", file=sys.stderr)
            return 1
        try:
            field = resolve_field_id(args.field_id)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1

    try:
        raw, label = resolve_dat_bytes(args.source, field)
        fd = load_field_dat(raw, label)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.dump_all:
        hits = dump_all(fd)
    elif args.opcode:
        hits = find_opcode(fd, args.opcode.upper(), decode_fields=args.decode_fields)
    else:
        try:
            pattern = bytes.fromhex(args.hex)
        except ValueError:
            print(f"error: bad --hex value: {args.hex!r}", file=sys.stderr)
            return 1
        hits = find_hex(fd, pattern)

    print(f"# {label} ({len(fd.scripts)} script slots)")
    if not hits:
        print("no matches")
        return 0
    for h in hits:
        print(h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
