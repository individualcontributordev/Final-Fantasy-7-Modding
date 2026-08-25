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
# MAPJUMP (0x60) unconditionally transfers control to a DIFFERENT field's
# script entirely (ffrtt: "Change Field" -- field id + xyz + direction).
# Anything physically after it in this slot is dead unless something else
# jumps back in, so it must be terminal (no fallthrough) here -- same as
# RET/RETTO/GAMEOVER. See docs/findings/2026-08-24-csr-movie-reachability-scan.md.
MAPJUMP_TERMINAL = {"MAPJUMP"}


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
    # offset of a reachable MOVIE op -> set of movie ids that can be "live"
    # (last PMVIE seen on some path from slot entry) when that MOVIE actually
    # executes. None means a path reaches MOVIE without this slot ever having
    # set an id itself (inherited from whatever a prior field/slot left in
    # global state). Path-sensitive: PMVIE alone is a no-op byte-store and
    # NEVER crashes; only a reachable MOVIE whose live id resolves out-of-
    # range or to the wrong file can actually crash/misplay. See user
    # correction in docs/findings/2026-08-24-csr-movie-reachability-scan.md.
    movie_ids_at_movie: dict[int, set[int | None]] = dc_field(default_factory=dict)
    # Whether this slot itself is ever executed at all: slots 0/1 (Init/Main)
    # of every entity auto-run; every other slot only runs if something
    # (REQ/REQSW/REQEW/PREQ/PRQSW/PRQEW) actually calls it. A slot's own
    # intra-slot CFG reachability (`visited`) is meaningless if the slot is
    # never invoked in the first place -- see user report: FSHIP_22 mov/31
    # has a live-looking `MOVIE` at offset 0, but nothing ever REQs into
    # entity "mov" at all, so it never runs. Set by compute_slot_liveness()
    # via analyze_field_bytes(); defaults to True so standalone analyze_slot()
    # callers (no field context) keep prior behavior.
    live: bool = True

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

    def reachable_movie_resolutions(self) -> list[tuple[int, int | None]]:
        """[(movie_offset, live_id)] -- one entry per (offset, id) pair, i.e.
        what id is actually live for each reachable MOVIE call along some
        path. This is the thing that can crash (OOB id) or misplay (wrong
        file), NOT bare PMVIE reachability.

        NOT gated on `self.live` -- see compute_slot_liveness()/`live` field
        docstring. Our REQ/PREQ call-graph is known-incomplete (it only
        models statically-resolvable REQ-family calls, not e.g. system/
        walkmesh-driven entry points), so `live=False` is not a mathematical
        proof a slot never runs -- but per project convention, CSR editing
        only ever touches scripts confirmed to execute, so any slot nobody
        REQs (and that isn't an autorun slot) was left byte-for-byte as
        pristine/untouched precisely BECAUSE it doesn't run. Confirmed for
        FSHIP_22/23/25 mov|move/31, BLIN2_I AD/31, and NRTHMK dir/31 (all
        verified orphans/dead code, NRTHMK by direct playtest). Treat
        `live=False` rows as "uncalled slot -- not required on disc", not as
        open questions needing per-row playtest verification; callers should
        still avoid silently dropping rows from raw data (keep them in
        output, just don't count them toward the disc's required-movie set),
        since a genuinely-missed caller edge would otherwise be invisible."""
        out = []
        for off, ids in self.movie_ids_at_movie.items():
            for mid in ids:
                out.append((off, mid))
        return out

    def reachable_mapjump_targets(self) -> list[int]:
        """Field ids from reachable MAPJUMP ops (0x60: op,I_lo,I_hi,X,X,Y,Y,Z,Z,D).

        Deliberately NOT gated on `self.live`: gating MAPJUMP on liveness
        drops the field-reachability graph from 405/787 to 163/787 reachable
        fields (tried and measured). At least one of those lost edges
        (NRTHMK dir/31 -> MD8_1, field id 133) is the ONLY modeled path into
        that target field (no walkmesh gateway covers it either), and
        MD8_1's reachability status if this edge is cut is unverified either
        way -- NRTHMK dir/31 itself was manually confirmed NOT played in
        CSR, but that doesn't establish whether MD8_1 is reached some other
        way we don't model (e.g. from WORLD.BIN) or is genuinely unreachable
        in CSR. Rather than assert either outcome without per-field
        verification, keep the old (pre-liveness) behavior for field-graph
        construction and treat this as an open question, not a settled
        "definitely live" claim."""
        out = []
        for o in self.ops:
            if o.name == "MAPJUMP" and o.offset in self.visited and len(o.raw) >= 3:
                out.append(o.raw[1] | (o.raw[2] << 8))
        return out


def analyze_slot(entity: str, slot_idx: int, script_raw: bytes) -> SlotAnalysis:
    ops = decode_with_offsets(script_raw)
    by_offset = {o.offset: o for o in ops}
    end = len(script_raw)

    def edges(o: OpRec) -> list[int]:
        fallthrough = o.offset + o.size
        if o.name in TERMINALS or o.name in MAPJUMP_TERMINAL:
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

    # Path-sensitive pass: carry "last id set by PMVIE/BGMOVIE on this path"
    # (None if never set within this slot) so we know which id is actually
    # live at each reachable MOVIE call, instead of just "some id-setter and
    # some MOVIE are each independently reachable somewhere in the slot"
    # (which can both over- and under-report: a later PMVIE/BGMOVIE can
    # overwrite an earlier one before MOVIE runs, or MOVIE can be reachable
    # on a branch that never passed through this slot's id-setter at all).
    # BGMOVIE (0x27) is a second, distinct opcode that sets the same "next
    # MOVIE id" state as PMVIE (0xf8) -- confirmed at LAS4_2/LAS4_3 movkun/1
    # (`BGMOVIE 01` immediately followed by `MOVIE`, id=1).
    movie_ids_at_movie: dict[int, set[int | None]] = {}
    if ops:
        seen_states: set[tuple[int, int | None]] = set()
        pstack: list[tuple[int, int | None]] = [(0, None)]
        while pstack:
            off, cur_id = pstack.pop()
            if (off, cur_id) in seen_states:
                continue
            seen_states.add((off, cur_id))
            if off not in by_offset:
                continue
            op = by_offset[off]
            if op.name in ("PMVIE", "BGMOVIE"):
                cur_id = op.raw[1]
            elif op.name == "MOVIE":
                movie_ids_at_movie.setdefault(off, set()).add(cur_id)
            for t in edges(op):
                if (t, cur_id) not in seen_states:
                    pstack.append((t, cur_id))
    return SlotAnalysis(entity, slot_idx, ops, visited, bad_jumps, movie_ids_at_movie)


# Every entity auto-runs its own slot 0 (Init) and slot 1 (Main). Beyond
# that, the ENGINE (not a REQ opcode) directly invokes certain slots based on
# player interaction, keyed off the entity's detected type (Makou Reactor
# GrpScript::detectType: first opcode of slot 0) --
# docs/reference/makou-reactor-script-labels.md:
#   Model entities    (first op PC/CHAR): slot 2 = Talk, slot 3 = Contact.
#   Location entities (first op LINE):    slots 2-7 = walkmesh-line
#     interactions ([OK]/Move/Move/Go/Go1x/Go away).
#   Everything else (Animation/Director/NoType): only 0/1 auto-run; any
#   other slot number is a plain "Script N" that ONLY runs if something
#   REQs/PREQs into it (this is FSHIP_22 mov/31's situation -- no type
#   detected, slot 31 is not 0/1, and nothing REQs entity "mov").
AUTORUN_SLOTS_MODEL = {0, 1, 2, 3}
AUTORUN_SLOTS_LOCATION = {0, 1, 2, 3, 4, 5, 6, 7}
AUTORUN_SLOTS_DEFAULT = {0, 1}


def _entity_autorun_slots(entity: str, analyses_by_key: dict[tuple[str, int], SlotAnalysis]) -> set[int]:
    """Port of Makou Reactor's GrpScript::detectType: scan slot 0 (Init) top
    to bottom for the first opcode matching a known type-defining category
    (not just the very first opcode in the slot)."""
    slot0 = analyses_by_key.get((entity, 0))
    if slot0 is None:
        return AUTORUN_SLOTS_DEFAULT
    char_seen = False
    for o in slot0.ops:
        if o.name == "PC":
            return AUTORUN_SLOTS_MODEL
        if o.name == "CHAR":
            char_seen = True
            continue
        if o.name == "LINE":
            return AUTORUN_SLOTS_LOCATION
        if o.name in ("BGPDH", "BGSCR", "BGON", "BGOFF", "BGROL", "BGROL2", "BGCLR", "MPNAM"):
            return AUTORUN_SLOTS_DEFAULT
    return AUTORUN_SLOTS_MODEL if char_seen else AUTORUN_SLOTS_DEFAULT


# Opcodes whose target entity is resolved statically via a groupID byte that
# indexes this field's entity list directly (verified against Makou
# Reactor's Opcode.cpp _groupScript()/SCRIPT_ID()/PRIORITY() macros: byte
# layout is [opcode, groupID, scriptIDAndPriority], scriptID = byte2 & 0x1F).
GROUP_CALL_OPS = {"REQ", "REQSW", "REQEW"}
# PREQ family targets "whatever entity is character #N in the current
# party" (byte1 = partyID, not a groupID) -- not statically resolvable here.
# Conservatively treat these as capable of invoking ANY entity's matching
# slot number, so we never under-report reachability.
PARTY_CALL_OPS = {"PREQ", "PRQSW", "PRQEW"}


def compute_slot_liveness(fd, analyses: list[SlotAnalysis]) -> dict[tuple[str, int], bool]:
    """Which (entity, slot) pairs are ever actually executed in this field:
    auto-run Init/Main slots, plus anything transitively REQ'd from a live
    slot's reachable code. A slot's own intra-slot CFG reachability is
    meaningless if nothing ever calls the slot at all."""
    by_key = {(a.entity, a.slot): a for a in analyses}
    live: set[tuple[str, int]] = set()
    queue: list[tuple[str, int]] = []
    for ent in fd.entities:
        for slot in _entity_autorun_slots(ent, by_key):
            key = (ent, slot)
            if key in by_key and key not in live:
                live.add(key)
                queue.append(key)

    all_slot_numbers = {a.slot for a in analyses}
    while queue:
        key = queue.pop()
        sa = by_key[key]
        for o in sa.ops:
            if o.offset not in sa.visited:
                continue
            if o.name in GROUP_CALL_OPS and len(o.raw) >= 3:
                group_id = o.raw[1]
                target_slot = o.raw[2] & 0x1F
                if 0 <= group_id < len(fd.entities):
                    tkey = (fd.entities[group_id], target_slot)
                    if tkey in by_key and tkey not in live:
                        live.add(tkey)
                        queue.append(tkey)
            elif o.name in PARTY_CALL_OPS and len(o.raw) >= 3:
                target_slot = o.raw[2] & 0x1F
                if target_slot in all_slot_numbers:
                    for a in analyses:
                        tkey = (a.entity, target_slot)
                        if tkey in by_key and tkey not in live:
                            live.add(tkey)
                            queue.append(tkey)
    return {key: (key in live) for key in by_key}


def analyze_field_bytes(field_raw: bytes, field_name: str) -> list[SlotAnalysis]:
    fd = load_field_dat(field_raw, field_name)
    analyses = [analyze_slot(s.entity, s.slot, s.raw) for s in fd.scripts]
    liveness = compute_slot_liveness(fd, analyses)
    for a in analyses:
        a.live = liveness.get((a.entity, a.slot), False)
    return analyses


# Section 5 (index 4 in FieldDat.sections; ffrtt calls it "Triggers") layout,
# confirmed against ffrtt's FF7/Field/Triggers page:
#   offset 56, 12 entries * 24 bytes = Gateways.
#   Each gateway: [0:6]=exit line v1, [6:6]=exit line v2, [12:6]=dest vertex,
#   [18:2]=destination field id (u16 LE), [20:4]=unknown.
#   Unused gateway slots have field id 0x7FFF (32767) -- must be excluded.
_GATEWAY_TABLE_OFFSET = 56
_GATEWAY_COUNT = 12
_GATEWAY_ENTRY_SIZE = 24
_GATEWAY_UNUSED_FIELD_ID = 0x7FFF


def field_gateway_targets(field_raw: bytes, field_name: str) -> list[int]:
    """Destination field ids from this field's gateway table (section 5).

    Gateways are walkmesh-line triggers -- always live, unlike scripted
    MAPJUMP which can be dead code under a jump-over. We don't attempt to
    determine if a *specific* gateway is reachable within the field (that
    would require walkmesh polygon connectivity analysis); we conservatively
    treat any non-placeholder gateway entry as a potential exit.
    """
    fd = load_field_dat(field_raw, field_name)
    if len(fd.sections) <= 4:
        return []
    inf = fd.sections[4]
    out = []
    for i in range(_GATEWAY_COUNT):
        off = _GATEWAY_TABLE_OFFSET + i * _GATEWAY_ENTRY_SIZE
        if off + _GATEWAY_ENTRY_SIZE > len(inf):
            break
        fid = inf[off + 18] | (inf[off + 19] << 8)
        if fid != _GATEWAY_UNUSED_FIELD_ID:
            out.append(fid)
    return out


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
        live_str = "" if s.live else " SLOT NEVER CALLED (not Init/Main, no REQ targets it)"
        print(f"{s.entity}/{s.slot}: {len(s.ops)} ops, {len(s.visited)} reachable, "
              f"MOVIE reachable={movie_reach > 0}{live_str}")
        for o, mid, reach in pmvies:
            print(f"  PMVIE id={mid} (0x{mid:02x}) @{o:#x} reachable={reach}")
        for off, mid in s.reachable_movie_resolutions():
            id_str = "NONE (inherited from prior field/slot)" if mid is None else f"{mid} (0x{mid:02x})"
            print(f"  MOVIE @{off:#x} live id={id_str}")
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
