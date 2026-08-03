#!/usr/bin/env python3
"""Copy D3 SNOVA/* onto a D1 Mode2 FF7 image by raw-copying the contiguous
SNOVA extent (dir + 17 files = 570 sectors), then remapping directory LBAs
and fixing MSF headers. Preserves EDC/ECC on file sectors (unlike v1
user-data rewrite).

  python3 mods/no-swap/scripts/inject_snova_d3_to_d1.py \
    --d1 workspace/iso-extract/ff7_d1_snova_test.bin \
    --d3 workspace/pristine/FINALFANTASY7_D3.bin \
    --in-place
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
    _list_dir,
    _read_extent,
    _u32_le,
    _user,
    extract_file,
    find_file,
)

# D3 retail layout (verified contiguous)
D3_SNOVA_DIR_LBA = 127100
D3_SNOVA_SECTORS = 570  # dir + files through SNOVA15


def both_u32(v: int) -> bytes:
    return struct.pack("<I", v) + struct.pack(">I", v)


def bcd(x: int) -> int:
    return ((x // 10) << 4) | (x % 10)


def lba_to_msf(lba: int) -> bytes:
    a = lba + 150
    m, s, f = a // 4500, (a % 4500) // 75, a % 75
    return bytes([bcd(m), bcd(s), bcd(f)])


def fix_sector_msf(img: bytearray, lba: int) -> None:
    base = lba * SECTOR
    img[base + 12 : base + 15] = lba_to_msf(lba)


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


def write_user_sector(img: bytearray, lba: int, user: bytes, hdr_from: int) -> None:
    assert len(user) == USER
    base = lba * SECTOR
    src = hdr_from * SECTOR
    img[base : base + 24] = img[src : src + 24]
    img[base + 24 : base + 24 + USER] = user
    img[base + 24 + USER : base + SECTOR] = b"\x00" * (SECTOR - 24 - USER)
    fix_sector_msf(img, lba)


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


def parse_path_L(blob: bytes) -> list:
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


def patch_dir_lbas(user: bytearray, delta: int, new_self: int, new_parent: int) -> None:
    """Add delta to every directory record LBA; set . and .. explicitly."""
    i = 0
    while i < len(user):
        ln = user[i]
        if ln == 0:
            break
        name_len = user[i + 32]
        name = bytes(user[i + 33 : i + 33 + name_len])
        if name_len == 1 and name[0] == 0:
            user[i + 2 : i + 10] = both_u32(new_self)
            user[i + 10 : i + 18] = both_u32(USER)
        elif name_len == 1 and name[0] == 1:
            user[i + 2 : i + 10] = both_u32(new_parent)
        else:
            old = struct.unpack_from("<I", user, i + 2)[0]
            user[i + 2 : i + 10] = both_u32(old + delta)
        i += ln


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
        raise SystemExit("D1 already has SNOVA/ — abort (rebuild from pristine/bak)")
    except FileNotFoundError:
        pass

    pvd3 = _user(d3, 16)
    root3 = pvd3[156:190]
    snova_meta = None
    for name, lb, sz, isdir in _list_dir(d3, _u32_le(root3, 2), _u32_le(root3, 10)):
        if name == "SNOVA" and isdir:
            snova_meta = (lb, sz)
            break
    if not snova_meta or snova_meta[0] != D3_SNOVA_DIR_LBA:
        raise SystemExit("unexpected D3 SNOVA dir LBA %r" % (snova_meta,))

    files = sorted(
        (n, lb, sz)
        for n, lb, sz, isd in _list_dir(d3, snova_meta[0], snova_meta[1])
        if n not in (".", "..") and not isd
    )
    first_file_lba = min(lb for _, lb, _ in files)
    last = max(lb + (sz + USER - 1) // USER for _, lb, sz in files)
    if first_file_lba != D3_SNOVA_DIR_LBA + 1 or last - D3_SNOVA_DIR_LBA != D3_SNOVA_SECTORS:
        raise SystemExit(
            "D3 SNOVA not contiguous as expected: files %s..%s (want dir %s, %s sectors)"
            % (first_file_lba, last, D3_SNOVA_DIR_LBA, D3_SNOVA_SECTORS)
        )
    print("D3 SNOVA raw block LBA %s+%s files=%s" % (D3_SNOVA_DIR_LBA, D3_SNOVA_SECTORS, len(files)))

    old_sec = len(img) // SECTOR
    new_dir = old_sec
    delta = new_dir - D3_SNOVA_DIR_LBA
    new_sec = old_sec + D3_SNOVA_SECTORS
    img.extend(b"\x00" * (D3_SNOVA_SECTORS * SECTOR))
    print("grow sectors %s -> %s (delta LBA %s)" % (old_sec, new_sec, delta))

    # Raw copy full Mode2 sectors from D3 (keeps EDC/ECC + subheaders)
    src = D3_SNOVA_DIR_LBA * SECTOR
    dst = new_dir * SECTOR
    nbytes = D3_SNOVA_SECTORS * SECTOR
    img[dst : dst + nbytes] = d3[src : src + nbytes]

    # Fix MSF on every copied sector for new LBAs
    for s in range(new_dir, new_sec):
        fix_sector_msf(img, s)

    pvd = bytearray(_user(img, 16))
    root = pvd[156:190]
    root_lba = _u32_le(bytes(root), 2)
    root_size = _u32_le(bytes(root), 10)
    if root_size != USER:
        raise SystemExit("unexpected root size %s" % root_size)

    dir_user = bytearray(img[new_dir * SECTOR + 24 : new_dir * SECTOR + 24 + USER])
    patch_dir_lbas(dir_user, delta, new_dir, root_lba)
    img[new_dir * SECTOR + 24 : new_dir * SECTOR + 24 + USER] = dir_user
    # Directory user changed -> EDC stale; zero EDC/ECC tail (DS OK). File sectors untouched.
    img[new_dir * SECTOR + 24 + USER : new_dir * SECTOR + SECTOR] = b"\x00" * (SECTOR - 24 - USER)

    root_blob = bytearray(_read_extent(img, root_lba, root_size))
    rec = dir_rec("SNOVA", new_dir, USER, True)
    i, ins = 0, None
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
    new_e = path_L("SNOVA", new_dir, 1)
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
    print("wrote %s (raw-copy v2)" % out)

    for n, _lb, sz in files:
        got = extract_file(bytes(img), "SNOVA/%s" % n)
        exp = extract_file(d3, "SNOVA/%s" % n)
        if got != exp or len(got) != sz:
            raise SystemExit("verify fail %s" % n)
    f0 = find_file(bytes(img), "SNOVA/SNOVA0.LZS")
    d3f = find_file(d3, "SNOVA/SNOVA0.LZS")
    s1 = bytes(img[f0.lba * SECTOR + 16 : f0.lba * SECTOR + SECTOR])
    s3 = d3[d3f.lba * SECTOR + 16 : d3f.lba * SECTOR + SECTOR]
    print("SNOVA0 sector sub+payload+edc match D3: %s (LBA d1=%s d3=%s)" % (s1 == s3, f0.lba, d3f.lba))
    print("verify: all SNOVA files match D3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
