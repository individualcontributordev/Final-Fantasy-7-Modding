#!/usr/bin/env python3
"""Rebuild single-disc-on-csr-v0.1.25 delta: keep MOVIE_ID at original LBA.

DuckStation evidence: Logical seek to [80:52:34] failed.
MSF 80:52:34 = LBA 363784 = where v0.1.25 relocated MINT/MOVIE_ID.BIN past the
~80-minute CD range. Engine loads MOVIE_ID early → boot hang / unloadable.

Fix: grow MOVIE_ID in place (1080→1220 still one 2048-byte Form1 sector at
LBA 126959). Path FMV streams may still append near EOF but stay under image
end; prefer placing them and never move system tables to lead-out.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mods/single-disc/scripts"))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from disc_sources import csr_root, pristine_bin  # noqa: E402
from inject_movies_by_disc_id import _patch_dirent_lba_size, _raw_sectors  # noqa: E402
from field_dat import load_field_dat, op_size  # noqa: E402
from ff7_opcodes import OPCODE_NAMES  # noqa: E402
from lzs import compress_all_with_header, decompress_all_with_header  # noqa: E402
from psx_mode2_iso import (  # noqa: E402
    SECTOR,
    USER,
    extract_file,
    find_file,
    replace_file_padded,
    _write_user,
)

PREV = "single-disc-on-csr-v0.1.24"
MOVIES = "single-disc-csr-manip-movies-v0.1.4"
PACK_ID = "single-disc-on-csr-v0.1.25"

D2_PATH_STREAMS = {
    50: "CANONHT1.MOV",
    51: "CANONHT2.MOV",
    52: "CANONH3F.MOV",
    53: "PARASHOT.MOV",
    55: "CANONHT0.MOV",
    59: "CANONH1P.MOV",
}
REMAP = {55: 54, 59: 55, 50: 56, 51: 57, 53: 58, 52: 59}

# Keep appended path streams below ~79:50:00 when possible (LBA ~ 358000)
SAFE_LBA_MAX = 358000


def install_grow_form1(img: bytearray, path: str, data: bytes) -> None:
    meta = find_file(img, path)
    if len(data) <= meta.size:
        replace_file_padded(img, path, data)
        return
    # Same number of Form1 sectors as existing slot? expand in place via dirent size.
    old_nsec = (meta.size + USER - 1) // USER
    new_nsec = (len(data) + USER - 1) // USER
    if new_nsec == old_nsec:
        # Write user payload sector-by-sector; bump ISO size only
        remaining = len(data)
        sector = meta.lba
        offset = 0
        while remaining > 0:
            take = min(USER, remaining)
            chunk = data[offset : offset + take]
            if take < USER:
                user = bytearray(_user_sec(img, sector))
                user[:take] = chunk
                # zero rest of logical file range only up to take? keep pad zero
                user[take:] = b"\x00" * (USER - take)
                _write_user(img, sector, bytes(user))
            else:
                _write_user(img, sector, chunk)
            offset += take
            remaining -= take
            sector += 1
        _patch_dirent_lba_size(img, path, meta.lba, len(data))
        return
    # Truly larger: append Form1 sectors at EOF (avoid for system tables)
    nsec = new_nsec
    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    new_lba = len(img) // SECTOR
    tmpl = bytes(img[meta.lba * SECTOR : (meta.lba + 1) * SECTOR])
    for i in range(nsec):
        sec = bytearray(tmpl)
        off = i * USER
        chunk = data[off : off + USER]
        if len(chunk) < USER:
            chunk = chunk + b"\x00" * (USER - len(chunk))
        sec[24 : 24 + USER] = chunk
        img.extend(sec)
    _patch_dirent_lba_size(img, path, new_lba, len(data))


def _user_sec(img, sector: int) -> bytes:
    return bytes(img[sector * SECTOR + 24 : sector * SECTOR + 24 + USER])


def append_movie(img: bytearray, src_img: bytes, name: str) -> tuple[int, int]:
    meta = find_file(src_img, f"MOVIE/{name}")
    raw = _raw_sectors(src_img, meta.lba, meta.size)
    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    new_lba = len(img) // SECTOR
    img.extend(raw)
    return new_lba, meta.size


def d2_engine_meta(cd2: bytes, eng_id: int):
    mid = extract_file(cd2, "MINT/MOVIE_ID.BIN")
    L, eng, a, b, c = struct.unpack_from("<5I", mid, eng_id * 20)
    name = D2_PATH_STREAMS[eng_id]
    meta = find_file(cd2, f"MOVIE/{name}")
    if meta.lba != L:
        raise SystemExit(f"D2 id {eng_id} {name} LBA mismatch")
    return eng, a, b, c, name


def brute_patch_pmvie(dat: bytes, remap: dict[int, int]) -> tuple[bytes, int]:
    dec = decompress_all_with_header(dat)
    fd = load_field_dat(dat)
    buf = bytearray(dec)
    changed = 0
    search_from = 0
    for s in fd.scripts:
        idx = buf.find(s.raw, search_from)
        if idx < 0:
            idx = buf.find(s.raw)
        if idx < 0:
            continue
        piece = bytearray(s.raw)
        pos = 0
        dirty = False
        while pos < len(piece):
            op = piece[pos]
            sz = max(op_size(piece, pos), 1)
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
            if name == "PMVIE" and len(piece) > pos + 1 and piece[pos + 1] in remap:
                piece[pos + 1] = remap[piece[pos + 1]]
                dirty = True
                changed += 1
            pos += sz
        if dirty:
            buf[idx : idx + len(s.raw)] = piece
        search_from = idx + max(len(s.raw), 1)
    return compress_all_with_header(bytes(buf)), changed


def pmvie_set(dat: bytes) -> set[int]:
    fd = load_field_dat(dat)
    out: set[int] = set()
    for s in fd.scripts:
        pos = 0
        while pos < len(s.raw):
            op = s.raw[pos]
            sz = max(op_size(s.raw, pos), 1)
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
            if name == "PMVIE" and len(s.raw) > pos + 1:
                out.add(s.raw[pos + 1])
            pos += sz
    return out


def lba_to_msf(lba: int) -> str:
    x = lba + 150
    f = x % 75
    x //= 75
    s = x % 60
    m = x // 60
    return f"{m:02d}:{s:02d}:{f:02d}"


def main() -> int:
    csr = csr_root()
    cd1p = Path.home() / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D1.bin"
    cd2p = Path.home() / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D2.bin"
    if not cd1p.is_file():
        cd1p = csr / "cache/csr/FINALFANTASY7_D1.bin"
    if not cd2p.is_file():
        cd2p = csr / "cache/csr/FINALFANTASY7_D2.bin"
    cd1 = cd1p.read_bytes()
    cd2 = cd2p.read_bytes()
    p2 = pristine_bin(2).read_bytes()

    base_path = ROOT / "workspace/iso-extract/_tmp024.bin"
    work_path = ROOT / "workspace/iso-extract/sd_v025b_work.bin"

    # Baseline for DELTA pack = CSR+movies+024
    print("CSR + movies + 024 ...")
    img = bytearray(cd1)
    apply_layer(
        img, json.loads((ROOT / f"builder/{MOVIES}/layers/disc1.layer.json").read_text())
    )
    apply_layer(
        img, json.loads((ROOT / f"builder/{PREV}/layers/disc1.layer.json").read_text())
    )
    base_path.write_bytes(img)
    print("base", len(img), "mod", len(img) % SECTOR)
    mid_meta0 = find_file(img, "MINT/MOVIE_ID.BIN")
    print("MOVIE_ID before", mid_meta0, "msf", lba_to_msf(mid_meta0.lba))

    for stem in ("FSHIP_24", "BLIN66_6"):
        install_grow_form1(img, f"FIELD/{stem}.DAT", extract_file(cd2, f"FIELD/{stem}.DAT"))
        print("CSR_D2", stem)

    # Path streams first (append), then MOVIE_ID in place
    installed: dict[int, tuple[int, int, tuple[int, int, int], str]] = {}
    for src_id, name in D2_PATH_STREAMS.items():
        eng, a, b, c, n = d2_engine_meta(cd2, src_id)
        new_lba, _iso = append_movie(img, p2, name)
        installed[src_id] = (new_lba, eng, (a, b, c), name)
        print(f"stream {name} LBA {new_lba} ({lba_to_msf(new_lba)}) eng={eng}")
        if new_lba > SAFE_LBA_MAX:
            print(f"  WARN past soft 80min-ish LBA {SAFE_LBA_MAX}")

    mid = bytearray(extract_file(bytes(img), "MINT/MOVIE_ID.BIN"))
    if len(mid) < 61 * 20:
        mid.extend(b"\x00" * (61 * 20 - len(mid)))
    for src_id, new_id in REMAP.items():
        lba, eng, (a, b, c), name = installed[src_id]
        struct.pack_into("<IIIII", mid, new_id * 20, lba, eng, a, b, c)
        print(f"MOVIE_ID[{new_id}] <- {name} LBA={lba}")

    assert len(mid) <= USER, "MOVIE_ID must fit one Form1 sector for in-place grow"
    install_grow_form1(img, "MINT/MOVIE_ID.BIN", bytes(mid))
    mid_meta = find_file(img, "MINT/MOVIE_ID.BIN")
    print("MOVIE_ID after", mid_meta, "msf", lba_to_msf(mid_meta.lba))
    if mid_meta.lba != mid_meta0.lba:
        raise SystemExit(
            f"MOVIE_ID LBA moved {mid_meta0.lba} -> {mid_meta.lba} (must stay in place)"
        )
    if mid_meta.lba != 126959 and mid_meta0.lba == 126959:
        raise SystemExit("unexpected MOVIE_ID LBA")

    for stem, need in (("FSHIP_12", 4), ("MD8_5", 1), ("MD8_52", 1)):
        src = extract_file(cd2, f"FIELD/{stem}.DAT")
        new_dat, n = brute_patch_pmvie(src, REMAP)
        print(f"PMVIE {stem}: {n}")
        if n < need:
            raise SystemExit(f"{stem} patches {n}")
        install_grow_form1(img, f"FIELD/{stem}.DAT", new_dat)

    assert 58 in pmvie_set(extract_file(bytes(img), "FIELD/MD8_5.DAT"))
    assert {54, 55, 56, 57} <= pmvie_set(extract_file(bytes(img), "FIELD/FSHIP_12.DAT"))
    L58 = struct.unpack_from("<I", mid, 58 * 20)[0]
    pmeta = find_file(p2, "MOVIE/PARASHOT.MOV")
    if bytes(img[L58 * SECTOR : (L58 + 1) * SECTOR]) != p2[
        pmeta.lba * SECTOR : (pmeta.lba + 1) * SECTOR
    ]:
        raise SystemExit("id58 not PARASHOT")
    for stem in ("FSHIP_24", "BLIN66_6"):
        a = decompress_all_with_header(extract_file(bytes(img), f"FIELD/{stem}.DAT"))
        b = decompress_all_with_header(extract_file(cd2, f"FIELD/{stem}.DAT"))
        if a != b:
            raise SystemExit(f"{stem} != CSR_D2")
    # boot: SCUS still CSR
    if extract_file(bytes(img), "SCUS_941.63") != extract_file(cd1, "SCUS_941.63"):
        raise SystemExit("SCUS changed")
    print("VERIFY OK MOVIE_ID LBA", mid_meta.lba, lba_to_msf(mid_meta.lba))

    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    work_path.write_bytes(img)
    print("wrote", work_path, len(img), "maxLBA", len(img) // SECTOR - 1, lba_to_msf(len(img)//SECTOR-1))

    pack_dir = ROOT / "builder" / PACK_ID
    layer_dir = pack_dir / "layers"
    layer_dir.mkdir(parents=True, exist_ok=True)
    print("diff delta vs 024 baseline ...")
    layer = build_layer(
        base_path,
        work_path,
        layer_id=PACK_ID + "-disc1",
        description=(
            "v0.1.25b: path-engine; MOVIE_ID grown in-place (no EOF relocate); "
            "PARASHOT@58; CSR D2 FSHIP_24+BLIN66_6"
        ),
    )
    out = layer_dir / "disc1.layer.json"
    out.write_text(json.dumps(layer, separators=(",", ":")) + "\n")
    print("layer bytes", out.stat().st_size, "records", len(layer["records"]), layer.get("stats"))
    if out.stat().st_size > 100_000_000:
        raise SystemExit("layer exceeds GitHub 100MB")

    # keep pack.json uiHidden etc
    pack = json.loads((pack_dir / "pack.json").read_text())
    pack["blurb"] = (
        "Internal fix layer auto-applied with Single-disc. "
        "PARASHOT engine ids; FSHIP_24/BLIN66_6 CSR D2; MOVIE_ID stays in-place."
    )
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2) + "\n")
    print("done", PACK_ID)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
