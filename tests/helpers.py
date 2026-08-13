"""Small helpers for field opcode / movie payload checks."""
from __future__ import annotations

import struct
from pathlib import Path


def same_or_prefix(a: bytes, b: bytes) -> bool:
    return a == b or a.startswith(b) or b.startswith(a)


def field_ops(dat: bytes) -> list[tuple]:
    """Return list of ('P', mid) and ('J', field_id) from a FIELD/*.DAT."""
    from field_dat import load_field_dat, op_size
    from ff7_opcodes import OPCODE_NAMES

    fd = load_field_dat(dat)
    out: list[tuple] = []
    for s in fd.scripts:
        pos = 0
        raw = s.raw
        while pos < len(raw):
            op = raw[pos]
            sz = max(op_size(raw, pos), 1)
            chunk = raw[pos : pos + sz] if pos + sz <= len(raw) else raw[pos:]
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
            if name == "PMVIE" and len(chunk) >= 2:
                out.append(("P", chunk[1]))
            if name.startswith("MAPJUMP") and len(chunk) >= 3:
                out.append(("J", int.from_bytes(chunk[1:3], "little")))
            pos += sz
    return out


def movie_id_rows_for_lba(mid_bin: bytes, lba: int) -> list[tuple[int, int]]:
    rows = []
    for i in range(len(mid_bin) // 20):
        L, size = struct.unpack_from("<2I", mid_bin, i * 20)
        if L == lba:
            rows.append((i, size))
    return rows


def parse_prefer_list(path: Path) -> dict[str, str]:
    """STEM.DAT -> d1|d2|review from csr-field-disc-prefer.txt."""
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.split("#", 1)[0].strip()
        if not s:
            continue
        parts = s.split()
        if len(parts) >= 2 and parts[0].upper().endswith(".DAT"):
            out[parts[0].upper()] = parts[1].lower()
    return out


def extract_addon_apply_rank_fn(builder_js: str):
    """Eval addonApplyRank from builder.js into a Python callable (mirror ranks)."""
    # Mirror the rank contract in Python — keep in sync with builder.js.
    def addon_apply_rank(entry_id: str) -> int:
        eid = str(entry_id or "")
        if "single-disc-csr-manip-movies" in eid:
            return 10
        # Hidden path/break deltas after player-facing single-disc core.
        if (
            "single-disc-on-csr-v0.1.26" in eid
            or "single-disc-on-csr-v0.1.35" in eid
            or "path-engine" in eid
            or "single-disc-on-csr-ref-" in eid
        ):
            return 21
        if eid.startswith("single-disc-on-"):
            return 20
        if "single-disc-endings" in eid:
            return 30
        if "fanfare" in eid or "encounter" in eid:
            return 40
        if eid.startswith("csr-plus-scene-") or eid.startswith("csr-plus-"):
            return 50
        return 45

    # sanity: source still documents the intended order
    assert "single-disc-csr-manip-movies" in builder_js
    assert "startsWith('single-disc-on-')" in builder_js or 'startsWith("single-disc-on-")' in builder_js
    assert "single-disc-on-csr-v0.1.26" in builder_js
    return addon_apply_rank


def is_mode2_form1_py(sector: bytes | bytearray, off: int = 0) -> bool:
    """Python twin of builder/edc.js isMode2Form1 — do not Form1-repair FMV/XA."""
    if sector[off] != 0x00 or sector[off + 11] != 0x00:
        return False
    if any(sector[off + i] != 0xFF for i in range(1, 11)):
        return False
    if sector[off + 15] != 0x02:
        return False
    submode = sector[off + 18]
    if submode & 0x20:  # Form2
        return False
    if submode & 0x04:  # audio
        return False
    if submode & 0x02:  # video
        return False
    if not (submode & 0x08):  # require Data
        return False
    return True
