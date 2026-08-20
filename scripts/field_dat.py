"""PSX FIELD/*.DAT: LZS → sections → scripts / texts (Makou-compatible)."""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

from ff7_opcodes import OPCODE_LENGTH, OPCODE_NAMES
from lzs import decompress_all_with_header

SECTION_NAMES = (
    "scripts",  # 0 scripts+texts+akao
    "walkmesh",
    "background",
    "camera",
    "inf",
    "encounter",
    "model_loader",
)

# SPECIAL subkey param extras (Makou Opcode::fixedSize)
_SPECIAL_PLUS1 = {0xF5, 0xF6, 0xF7, 0xFB, 0xFC}  # ARROW PNAME GMSPD BTLCK MVLCK
_SPECIAL_PLUS2 = {0xF8, 0xFD}  # SMSPD SPCNM


def op_size(data: bytes, pos: int) -> int:
    if pos >= len(data):
        return 1
    op = data[pos]
    if op == 0x28:  # KAWAI
        return max(data[pos + 1], 1) if pos + 1 < len(data) else 1
    if op == 0x0F:  # SPECIAL
        if pos + 1 >= len(data):
            return 2
        sub = data[pos + 1]
        if sub in _SPECIAL_PLUS1:
            return 3
        if sub in _SPECIAL_PLUS2:
            return 4
        return 2
    if op == 0x1C:
        base = OPCODE_LENGTH[op]
        return base + min(data[pos + 1], 128) if pos + 1 < len(data) else base
    if op < len(OPCODE_LENGTH):
        return max(OPCODE_LENGTH[op], 1)
    return 1


def decode_ops(blob: bytes) -> list[tuple[bytes, str]]:
    ops: list[tuple[bytes, str]] = []
    pos = 0
    while pos < len(blob):
        op = blob[pos]
        sz = max(op_size(blob, pos), 1)
        trunc = pos + sz > len(blob)
        raw = blob[pos:] if trunc else blob[pos : pos + sz]
        name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else f"OP{op:02X}"
        if trunc:
            name += "?TRUNC"
        ops.append((raw, name))
        if trunc:
            break
        pos += sz
    return ops


def fmt_op(raw: bytes, name: str) -> str:
    if name.startswith("SPECIAL") and len(raw) > 1:
        return f"{name}.{raw[1]:02X} {raw.hex()}"
    return f"{name} {raw.hex()}"


def decompress_dat(raw: bytes) -> bytes:
    """LZS FIELD DAT, or already-decompressed if header looks like VRAM ptrs."""
    if len(raw) >= 28:
        p0 = struct.unpack_from("<I", raw, 0)[0]
        # decompressed PS header: ptr0 is VRAM-ish (>= 0x80000000-ish or large)
        if p0 > len(raw) and (p0 & 0xFFF00000) != 0:
            return raw
        # compressed: first u32 is compressed payload size
        if 4 < p0 + 4 <= len(raw) + 4 and p0 < len(raw):
            try:
                return decompress_all_with_header(raw)
            except ValueError:
                pass
    return decompress_all_with_header(raw)


def section_offsets(dat: bytes) -> list[int]:
    ptrs = list(struct.unpack_from("<7I", dat, 0))
    vdiff = ptrs[0] - 28
    return [p - vdiff for p in ptrs]


def slice_sections(dat: bytes) -> list[bytes]:
    offs = section_offsets(dat)
    ends = offs[1:] + [len(dat)]
    return [dat[a:b] for a, b in zip(offs, ends)]


@dataclass
class ScriptSlot:
    entity: str
    slot: int
    raw: bytes
    start: int = 0  # byte offset within section1 (scripts section); 0 if unknown

    def ops(self) -> list[str]:
        return [fmt_op(r, n) for r, n in decode_ops(self.raw)]


@dataclass
class FieldDat:
    path: str | None
    raw_size: int
    dec_size: int
    sections: list[bytes]
    entities: list[str]
    scripts: list[ScriptSlot]
    texts_raw: bytes
    text_entries: list[bytes]  # through 0xFF
    text_pad_total: int
    akao: bytes
    author: str
    version: int
    # Layout metadata (byte offsets within sections[0]) needed by field_dat_write.py
    # to splice script slots without reparsing everything from scratch.
    nb: int = 0
    sc: int = 0
    nb_akao: int = 0
    akao_tbl_off: int = 0
    pos_scripts: int = 0
    pos_texts_val: int = 0
    pos_akao_val: int = 0
    pos_after: int = 0

    @property
    def section_sizes(self) -> dict[str, int]:
        return {SECTION_NAMES[i]: len(self.sections[i]) for i in range(7)}


def _parse_section1(sec: bytes) -> tuple[
    int, str, list[str], list[ScriptSlot], bytes, list[bytes], int, bytes, dict
]:
    version = struct.unpack_from("<H", sec, 0)[0]
    nb = sec[2]
    pos_texts = struct.unpack_from("<H", sec, 4)[0]
    nb_akao = struct.unpack_from("<H", sec, 6)[0]
    demo = version == 0x0301
    cur = 8 if demo else 16
    author = sec[cur : cur + 8].split(b"\x00")[0].decode("latin1", "replace")
    cur += 16
    sc = 16 if demo else 32
    pos_scripts = cur + 8 * nb + 4 * nb_akao
    pos_akao = struct.unpack_from("<I", sec, cur + 8 * nb)[0] if nb_akao else len(sec)
    pos_after = min(pos_akao, pos_texts) if pos_texts else pos_akao

    entities: list[str] = []
    slots: list[ScriptSlot] = []
    empty = 0
    for i in range(nb):
        name = sec[cur + 8 * i : cur + 8 * i + 8].split(b"\x00")[0].decode(
            "latin1", "replace"
        )
        entities.append(name)
        if empty > 1:
            empty -= 1
            continue
        positions = list(
            struct.unpack_from(f"<{sc}H", sec, pos_scripts + sc * 2 * i)
        )
        if i == nb - 1:
            positions.append(pos_after)
        else:
            pos = struct.unpack_from("<H", sec, pos_scripts + sc * 2 * (i + 1))[0]
            if pos > positions[sc - 1]:
                positions.append(pos)
            else:
                empty = 1
                while pos <= positions[sc - 1] and i + empty < nb - 1:
                    pos = struct.unpack_from(
                        "<H", sec, pos_scripts + sc * 2 * (i + empty + 1)
                    )[0]
                    empty += 1
                positions.append(pos_after if i + empty == nb else pos)
        for j in range(sc):
            if positions[j + 1] > positions[j]:
                blob = sec[positions[j] : positions[j + 1]]
                slots.append(ScriptSlot(name, j, blob, start=positions[j]))

    texts_blob = (
        sec[pos_texts:pos_akao] if pos_akao >= pos_texts else sec[pos_texts:]
    )
    entries, pad = _parse_texts(texts_blob)
    akao = sec[pos_akao:] if pos_akao < len(sec) else b""
    meta = dict(
        nb=nb,
        sc=sc,
        nb_akao=nb_akao,
        akao_tbl_off=cur + 8 * nb,
        pos_scripts=pos_scripts,
        pos_texts_val=pos_texts,
        pos_akao_val=pos_akao,
        pos_after=pos_after,
    )
    return version, author, entities, slots, texts_blob, entries, pad, akao, meta


def _parse_texts(blob: bytes) -> tuple[list[bytes], int]:
    if len(blob) < 4:
        return [], 0
    pos_beg = struct.unpack_from("<H", blob, 2)[0]
    if pos_beg < 4:
        return [], 0
    count = pos_beg // 2 - 1
    offs = [struct.unpack_from("<H", blob, 2 + i * 2)[0] for i in range(count)]
    entries: list[bytes] = []
    pad = 0
    for i, o in enumerate(offs):
        end = offs[i + 1] if i + 1 < count else len(blob)
        if o >= len(blob):
            entries.append(b"")
            continue
        span = blob[o:end]
        if 0xFF in span:
            cut = span.index(0xFF) + 1
            entries.append(span[:cut])
            pad += len(span) - cut
        else:
            entries.append(span)
    return entries, pad


def load_field_dat(data: bytes, path: str | None = None) -> FieldDat:
    raw_size = len(data)
    dat = decompress_dat(data)
    sections = slice_sections(dat)
    ver, author, ents, slots, texts, entries, pad, akao, meta = _parse_section1(
        sections[0]
    )
    return FieldDat(
        path=path,
        raw_size=raw_size,
        dec_size=len(dat),
        sections=sections,
        entities=ents,
        scripts=slots,
        texts_raw=texts,
        text_entries=entries,
        text_pad_total=pad,
        akao=akao,
        author=author,
        version=ver,
        **meta,
    )


def load_field_dat_path(path: Path) -> FieldDat:
    return load_field_dat(path.read_bytes(), str(path))
