#!/usr/bin/env python3
"""Copy pristine D3 SNOVA/* onto a D1 Mode2 FF7 image (grow ISO, add dir).

Makou cannot add folders. CDmage works manually; this automates for DuckStation.

  python3 mods/no-swap/scripts/inject_snova_d3_to_d1.py \
    --d1 workspace/iso-extract/ff7_d1_noswap_work.bin \
    --d3 workspace/pristine/FINALFANTASY7_D3.bin \
    --in-place

EDC/ECC on new sectors is zeroed — fine for DuckStation; repair before burn.
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from psx_mode2_iso import (  # noqa: E402
    SECTOR,
    USER,
    _read_extent,
    _u32_le,
    _user,
    extract_file,
    find_file,
)

SNOVA_NAMES = [
    "LASBOSS3.BIN", "SNOVA0.LZS", "SNOVA1.LZS", "SNOVA10.LZS", "SNOVA11.LZS",
    "SNOVA12.LZS", "SNOVA13.LZS", "SNOVA14.LZS", "SNOVA15.LZS", "SNOVA2.LZS",
    "SNOVA3.LZS", "SNOVA4.LZS", "SNOVA5.LZS", "SNOVA6.LZS", "SNOVA7.LZS",
    "SNOVA8.LZS", "SNOVA9.LZS",
]


def both_u32(v: int) -> bytes:
    return struct.pack("<I", v) + struct.pack(">I", v)


def dir_rec(name: str, lba: int, size: int, is_dir: bool) -> bytes:
    if name == ".":
        nm = bytes([0])
    elif name == "..":
        nm = bytes([1])
    else:
        nm = name.encode("ascii")
    nlen = len(nm)
    length = 33 + nlen + (nlen % 2)
    rec = bytearray(length)
    rec[0] = length
    rec[2:10] = both_u32(lba)
    rec[10:18] = both_u32(size)
    rec[25] = 0x02 if is_dir else 0x00
    rec[28:32] = struct.pack("<H", 1) + struct.pack(">H", 1)
    rec[32] = nlen
    rec[33 : 33 + nlen] = nm
    return bytes(rec)


def write_user_sector(img: bytearray, lba: int, user: bytes, hdr_from: int = 24) -> None:
    assert len(user) == USER
    base = lba * SECTOR
    src = hdr_from * SECTOR
    img[base : base + 24] = img[src : src + 24]
    img[base + 24 : base + 24 + USER] = user
    img[base + 24 + USER : base + SECTOR] = b"\x00" * (SECTOR - 24 - USER)


def write_file(img: bytearray, lba: int, data: bytes) -> int:
    rem, off, sec = len(data), 0, lba
    while rem > 0:
        take = min(USER, rem)
        user = bytearray(USER)
        user[:take] = data[off : off + take]
        write_user_sector(img, sec, bytes(user))
        off += take
        rem -= take
        sec += 1
    return sec - lba


def path_L(name: str, lba: int, parent: int) -> bytes:
    if name == "\x00":
        nm = bytes([0])
    elif name == "\x01":
        nm = bytes([1])
    else:
        nm = name.encode("ascii")
    di = len(nm)
    rec = bytes([di, 0]) + struct.pack("<I", lba) + struct.pack("<H", parent) + nm
    return rec + (b"\x00" if di % 2 else b"")


def path_M(name: str, lba: int, parent: int) -> bytes:
    if name == "\x00":
        nm = bytes([0])
    elif name == "\x01":
        nm = bytes([1])
    else:
        nm = name.encode("ascii")
    di = len(nm)
    rec = bytes([di, 0]) + struct.pack(">I", lba) + struct.pack(">H", parent) + nm
    return rec + (b"\x00" if di % 2 else b"")


def parse_path_L(blob: bytes) -> list[bytes]:
    out, i = [], 0
    while i < len(blob):
        di = blob[i]
        if di == 0:
            break
        n = 8 + di + (di % 2)
        out.append(blob[i : i + n])
        i += n
    return out


def ent_name_L(e: bytes) -> str:
    di = e[0]
    raw = e[8 : 8 + di]
    if di == 1 and raw[0] in (0, 1):
        return "\x00" if raw[0] == 0 else "\x01"
    return raw.decode("ascii")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--d1", type=Path, required=True)
    ap.add_argument("--d3", type=Path, required=True)
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("-o", type=Path)
    args = ap.parse_args()

    img = bytearray(args.d1.read_bytes())
    d3 = args.d3.read_bytes()
    try:
        find_file(img, "SNOVA/SNOVA0.LZS")
        raise SystemExit("D1 already has SNOVA/ — abort")
    except FileNotFoundError:
        pass

    payloads = [(n, extract_file(d3, f"SNOVA/{n}")) for n in SNOVA_NAMES]
    print(f"SNOVA files={len(payloads)} bytes={sum(len(d) for _, d in payloads)}")

    old_sec = len(img) // SECTOR
    pvd = bytearray(_user(img, 16))
    root = pvd[156:156 + 34]
    root_lba = _u32_le(bytes(root), 2)
    root_size = _u32_le(bytes(root), 10)
    if root_size != USER:
        raise SystemExit(f"unexpected root size {root_size}")

    snova_dir_lba = old_sec
    cursor = snova_dir_lba + 1
    meta: list[tuple[str, int, int]] = []
    for name, data in payloads:
        nsec = (len(data) + USER - 1) // USER
        meta.append((name, cursor, len(data)))
        cursor += nsec
    new_sec = cursor
    img.extend(b"\x00" * ((new_sec - old_sec) * SECTOR))
    print(f"grow sectors {old_sec} -> {new_sec} (+{new_sec - old_sec})")

    for name, data in payloads:
        lb = next(x[1] for x in meta if x[0] == name)
        write_file(img, lb, data)
        print(f"  {name} @ LBA {lb}")

    dir_body = b"".join(
        [dir_rec(".", snova_dir_lba, USER, True), dir_rec("..", root_lba, USER, True)]
        + [dir_rec(n, lb, sz, False) for n, lb, sz in meta]
    )
    if len(dir_body) > USER:
        raise SystemExit("SNOVA dir > 2048")
    write_user_sector(
        img, snova_dir_lba, dir_body + b"\x00" * (USER - len(dir_body)), hdr_from=root_lba
    )

    root_blob = bytearray(_read_extent(img, root_lba, root_size))
    rec = dir_rec("SNOVA", snova_dir_lba, USER, True)
    i = 0
    ins = None
    while i < len(root_blob):
        ln = root_blob[i]
        if ln == 0:
            ins = i
            break
        i += ln
    if ins is None or ins + len(rec) > len(root_blob):
        raise SystemExit("no root dir padding for SNOVA record")
    root_blob[ins : ins + len(rec)] = rec
    write_user_sector(img, root_lba, bytes(root_blob), hdr_from=root_lba)

    pt_size = _u32_le(bytes(pvd), 132)
    pt_l = _u32_le(bytes(pvd), 140)
    pt_l2 = _u32_le(bytes(pvd), 144)
    pt_m = struct.unpack(">I", bytes(pvd[148:152]))[0]
    ents = parse_path_L(_read_extent(img, pt_l, pt_size))
    new_e = path_L("SNOVA", snova_dir_lba, 1)
    idx = len(ents)
    for j, e in enumerate(ents):
        nm = ent_name_L(e)
        if nm in ("\x00", "\x01"):
            continue
        parent = struct.unpack_from("<H", e, 6)[0]
        if parent == 1 and nm > "SNOVA":
            idx = j
            break
    ents = ents[:idx] + [new_e] + ents[idx:]
    pt_new = b"".join(ents)
    if len(pt_new) > USER:
        raise SystemExit("L path table > 2048")
    pt_pad = pt_new + b"\x00" * (USER - len(pt_new))
    for lba in {pt_l, pt_l2}:
        if lba:
            write_user_sector(img, lba, pt_pad, hdr_from=pt_l)

    ments = []
    for e in ents:
        nm = ent_name_L(e)
        lba = struct.unpack_from("<I", e, 2)[0]
        parent = struct.unpack_from("<H", e, 6)[0]
        ments.append(path_M(nm, lba, parent))
    mt = b"".join(ments)
    if len(mt) > USER:
        raise SystemExit("M path table > 2048")
    if pt_m:
        write_user_sector(img, pt_m, mt + b"\x00" * (USER - len(mt)), hdr_from=pt_l)

    pvd[132:140] = both_u32(len(pt_new))
    pvd[80:88] = both_u32(new_sec)
    write_user_sector(img, 16, bytes(pvd), hdr_from=16)

    out = args.d1 if args.in_place or not args.o else args.o
    if not args.in_place and not args.o:
        raise SystemExit("pass --in-place or -o OUT.bin")
    out.write_bytes(img)
    print(f"wrote {out}")

    for n, data in payloads:
        got = extract_file(bytes(img), f"SNOVA/{n}")
        if got != data:
            raise SystemExit(f"verify fail {n}")
    print("verify: all SNOVA files match D3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
