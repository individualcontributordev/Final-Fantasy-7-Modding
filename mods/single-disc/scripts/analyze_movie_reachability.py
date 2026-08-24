#!/usr/bin/env python3
"""CFG reachability for PMVIE/MOVIE ops in a FIELD/*.DAT script.

Unlike counting PMVIE/MOVIE opcode presence (false positives: CSR often
leaves the bytes in place but jumps clean over them -- see
docs/findings/2026-08-07-csr-d3-ending-movie-jumps.md), this does real
control-flow analysis per script slot:

  - RET / RETTO / GAMEOVER are terminal (no fallthrough).
  - JMPF/JMPFL/JMPB/JMPBL are unconditional -- only the jump edge, NOT the
    fallthrough (bytes physically after them are dead unless something else
    jumps back into them).
  - IFxx family are conditional -- BOTH the fallthrough (condition true) and
    the jump target (else/false) are live edges.

Jump target math reuses remove_dskcg.py's JUMP_INFO table (already verified
against Makou Reactor's Opcode.h jumpShift()/jump()).

Reachability = BFS from the slot's own offset 0 (its entry point). This
naturally marks unreachable any opcode moved below an unconditional
terminal/jump with no incoming edge, or any code CSR jumps clean over.

Usage:
  python3 mods/single-disc/scripts/analyze_movie_reachability.py \\
      --disc csr:2 --field LOSLAKE1
  python3 mods/single-disc/scripts/analyze_movie_reachability.py \\
      --disc csr:3 --field LASTMAP --dump
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field as dc_field
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))

from disc_sources import load_csr_image, load_pristine_image  # noqa: E402
from field_dat import OPCODE_NAMES, load_field_dat, op_size  # noqa: E402
from psx_mode2_iso import extract_file  # noqa: E402

# (jump-field byte offset within opcode raw, field width bytes, shift, is_backward)
# Source of truth: mods/single-disc/scripts/remove_dskcg.py JUMP_INFO,
# verified against Makou Reactor Opcode.h.
JUMP_INFO: dict[str, tuple[int, int, int, bool]] = {
    "JMPF": (1, 1, 1, False),
    "JMPFL": (1, 2, 1, False),
    "JMPB": (1, 1, 0, True),
    "JMPBL": (1, 2, 0, True),
    "IFUB": (5, 1, 5, False),
    "IFUBL": (5, 2, 5, False),
    "IFSW": (7, 1, 7, False),
    "IFSWL": (7, 2, 7, False),
    "IFUW": (7, 1, 7, False),
    "IFUWL": (7, 2, 7, False),
    "IFKEY": (3, 1, 3, False),
    "IFKEYON": (3, 1, 3, False),
    "IFKEYOFF": (3, 1, 3, False),
    "IFPRTYQ": (2, 1, 2, False),
    "IFMEMBQ": (2, 1, 2, False),
}
UNCONDITIONAL_JUMPS = {"JMPF", "JMPFL", "JMPB", "JMPBL"}
CONDITIONAL_JUMPS = set(JUMP_INFO) - UNCONDITIONAL_JUMPS
TERMINALS = {"RET", "RETTO", "GAMEOVER"}
# Calls that transfer control to another entity/slot's script. Params vary by
# opcode; we don't resolve the callee here (cross-slot resolution done by
# caller via CALL_OPS detection + separate slot lookup), but we must NOT
# treat them as terminal (they fall through to the next op after return).
CALL_OPS = {"REQ", "REQSW", "REQEW", "PREQ", "PRQSW", "PRQEW"}


def _read_jump_val(raw: bytes, offset: int, width: int) -> int:
    return raw[offset] if width == 1 else int.from_bytes(raw[offset : offset + width], "little")


@dataclass
class OpRec:
    offset: int
    size: int
    name: str
    raw: bytes


def decode_with_offsets(script_raw: bytes) -> list[OpRec]:
    ops: list[OpRec] = []
    pos = 0
    n = len(script_raw)
    while pos < n:
        op = script_raw[pos]
        sz = max(op_size(script_raw, pos), 1)
        raw = script_raw[pos : pos + sz]
        name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else f"OP{op:02X}"
        ops.append(OpRec(pos, sz, name, raw))
        pos += sz
    return ops


@dataclass
class SlotAnalysis:
    entity: str
    slot: int
    ops: list[OpRec]
    visited: set[int]
    bad_jumps: list[str] = dc_field(default_factory=list)

    def reachable_pmvie(self) -> list[tuple[int, int]]:
        """[(offset, movie_id)] for PMVIE ops with offset in visited."""
        out = []
        for o in self.ops:
            if o.name == "PMVIE" and o.offset in self.visited:
                out.append((o.offset, o.raw[1]))
        return out

    def reachable_movie_count(self) -> int:
        return sum(1 for o in self.ops if o.name == "MOVIE" and o.offset in self.visited)

    def all_pmvie(self) -> list[tuple[int, int, bool]]:
        """[(offset, movie_id, reachable)] for every PMVIE regardless of reachability."""
        return [(o.offset, o.raw[1], o.offset in self.visited) for o in self.ops if o.name == "PMVIE"]


def analyze_slot(entity: str, slot_idx: int, script_raw: bytes) -> SlotAnalysis:
    ops = decode_with_offsets(script_raw)
    by_offset = {o.offset: o for o in ops}
    end = len(script_raw)

    def edges(o: OpRec) -> list[int]:
        fallthrough = o.offset + o.size
        if o.name in TERMINALS:
            return []
        if o.name in UNCONDITIONAL_JUMPS:
            width_info = JUMP_INFO[o.name]
            off, width, shift, is_back = width_info
            val = _read_jump_val(o.raw, off, width)
            target = o.offset - val if is_back else o.offset + val + shift
            return [target]
        if o.name in CONDITIONAL_JUMPS:
            off, width, shift, is_back = JUMP_INFO[o.name]
            val = _read_jump_val(o.raw, off, width)
            target = o.offset - val if is_back else o.offset + val + shift
            outs = [target]
            if fallthrough < end:
                outs.append(fallthrough)
            return outs
        # CALL_OPS and everything else: straight fallthrough.
        if fallthrough < end:
            return [fallthrough]
        return []

    visited: set[int] = set()
    bad_jumps: list[str] = []
    if ops:
        stack = [0]
        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            if cur not in by_offset:
                bad_jumps.append(f"target {cur} not an instruction boundary")
                continue
            visited.add(cur)
            op = by_offset[cur]
            for t in edges(op):
                if t not in visited:
                    stack.append(t)
    return SlotAnalysis(entity, slot_idx, ops, visited, bad_jumps)


def analyze_field_bytes(field_raw: bytes, field_name: str) -> list[SlotAnalysis]:
    fd = load_field_dat(field_raw, field_name)
    return [analyze_slot(s.entity, s.slot, s.raw) for s in fd.scripts]


def load_field(disc_spec: str, field_name: str) -> bytes:
    if disc_spec.startswith("csr:"):
        img = bytes(load_csr_image(int(disc_spec.split(":", 1)[1])))
    elif disc_spec.startswith("pristine:"):
        img = bytes(load_pristine_image(int(disc_spec.split(":", 1)[1])))
    else:
        img = Path(disc_spec).read_bytes()
    return extract_file(img, f"FIELD/{field_name.upper()}.DAT")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disc", required=True, help="csr:1|csr:2|csr:3|pristine:N|path/to.bin")
    ap.add_argument("--field", required=True)
    ap.add_argument("--movie-id", type=int, help="report only this PMVIE id's reachability")
    ap.add_argument("--dump", action="store_true", help="print every slot's reachable/dead ops")
    args = ap.parse_args()

    raw = load_field(args.disc, args.field)
    slots = analyze_field_bytes(raw, args.field)

    any_hit = False
    for s in slots:
        pmvies = s.all_pmvie()
        if not pmvies and not args.dump:
            continue
        if args.movie_id is not None:
            pmvies = [(o, m, r) for o, m, r in pmvies if m == args.movie_id]
            if not pmvies:
                continue
        any_hit = True
        movie_reach = s.reachable_movie_count()
        print(f"{s.entity}/{s.slot}: {len(s.ops)} ops, {len(s.visited)} reachable, "
              f"MOVIE reachable={movie_reach > 0}")
        for o, mid, reach in pmvies:
            print(f"  PMVIE id={mid} (0x{mid:02x}) @{o:#x} reachable={reach}")
        if s.bad_jumps:
            for b in s.bad_jumps:
                print(f"  WARN: {b}")
        if args.dump:
            for op in s.ops:
                mark = "  " if op.offset in s.visited else "XX"
                print(f"  {mark} @{op.offset:#04x} {op.name} {op.raw.hex()}")
    if not any_hit:
        print(f"{args.field}: no matching PMVIE found" + (f" for id={args.movie_id}" if args.movie_id is not None else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
