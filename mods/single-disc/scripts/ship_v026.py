#!/usr/bin/env python3
"""single-disc-on-csr-v0.1.26 path-engine delta (under ~80min CD, MOVIE_ID in place).

v0.1.25 failed DuckStation: MOVIE_ID relocated to EOF (80:52:34), then even
in-place rebuild still appended path streams past 80:00 and sticky id@0.1.25
cache served the broken layer.

v0.1.26:
  - New pack id/version (cache bust)
  - MOVIE_ID grows in place at LBA 126959 only
  - Reuse OPENINGE (PARASHOT) + CAR_1209 (CANONHT2) LBAs already on 0.1.24
  - Append only CANONHT0/1/H3F/H1P; keep image end before 80:00:00
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
from psx_mode2_iso import SECTOR, USER, extract_file, find_file, replace_file_padded, _write_user  # noqa: E402

CORE = "single-disc-on-csr-v0.1.24"
MOVIES = "single-disc-csr-manip-movies-v0.1.4"
PACK_ID = "single-disc-on-csr-v0.1.26"
HARD_LBA_MAX = 80 * 60 * 75 - 150  # 80:00:00


def lba_to_msf(lba: int) -> str:
    x = lba + 150
    f = x % 75
    x //= 75
    s = x % 60
    m = x // 60
    return f"{m:02d}:{s:02d}:{f:02d}"


def _user_sec(img, sector: int) -> bytes:
    return bytes(img[sector * SECTOR + 24 : sector * SECTOR + 24 + USER])


def install_grow_form1(img: bytearray, path: str, data: bytes) -> None:
    meta = find_file(img, path)
    if len(data) <= meta.size:
        replace_file_padded(img, path, data)
        return
    old_nsec = (meta.size + USER - 1) // USER
    new_nsec = (len(data) + USER - 1) // USER
    if new_nsec == old_nsec:
        remaining = len(data)
        sector = meta.lba
        offset = 0
        while remaining > 0:
            take = min(USER, remaining)
            chunk = data[offset : offset + take]
            if take < USER:
                user = bytearray(_user_sec(img, sector))
                user[:take] = chunk
                user[take:] = b"\x00" * (USER - take)
                _write_user(img, sector, bytes(user))
            else:
                _write_user(img, sector, chunk)
            offset += take
            remaining -= take
            sector += 1
        _patch_dirent_lba_size(img, path, meta.lba, len(data))
        return
    raise SystemExit(
        f"{path}: needs {new_nsec} sectors (had {old_nsec}); refusing EOF relocate for system files"
    )


def append_movie(img: bytearray, src_img: bytes, name: str) -> tuple[int, int]:
    meta = find_file(src_img, f"MOVIE/{name}")
    raw = _raw_sectors(src_img, meta.lba, meta.size)
    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    new_lba = len(img) // SECTOR
    end_lba = new_lba + (len(raw) // SECTOR) - 1
    if end_lba >= HARD_LBA_MAX:
        raise SystemExit(
            f"{name} would end at LBA {end_lba} ({lba_to_msf(end_lba)}) past 80:00:00"
        )
    img.extend(raw)
    return new_lba, meta.size


def d2_row(cd2: bytes, eng_id: int):
    mid = extract_file(cd2, "MINT/MOVIE_ID.BIN")
    return struct.unpack_from("<5I", mid, eng_id * 20)


def brute_patch_pmvie(dat: bytes, remap: dict[int, int]) -> tuple[bytes, int]:
    fd = load_field_dat(dat)
    buf = bytearray(decompress_all_with_header(dat))
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

    base_path = ROOT / "workspace/iso-extract/_tmp024_for_v026.bin"
    work_path = ROOT / "workspace/iso-extract/sd_v026_work.bin"

    print("CSR + movies + 024 ...")
    img = bytearray(cd1)
    apply_layer(img, json.loads((ROOT / f"builder/{MOVIES}/layers/disc1.layer.json").read_text()))
    apply_layer(img, json.loads((ROOT / f"builder/{CORE}/layers/disc1.layer.json").read_text()))
    base_path.write_bytes(img)
    print("base end", len(img) // SECTOR - 1, lba_to_msf(len(img) // SECTOR - 1))

    mid0 = find_file(img, "MINT/MOVIE_ID.BIN")
    print("MOVIE_ID", mid0, lba_to_msf(mid0.lba))

    for stem in ("FSHIP_24", "BLIN66_6"):
        install_grow_form1(img, f"FIELD/{stem}.DAT", extract_file(cd2, f"FIELD/{stem}.DAT"))
        print("CSR_D2", stem)

    # Engine slots 54-59 (avoid clobbering D1 early-game 0..53)
    # D2 src id -> new D1 eng id
    REMAP = {55: 54, 59: 55, 50: 56, 51: 57, 53: 58, 52: 59}

    # Reuse streams already correct on 0.1.24 image
    openinge = find_file(img, "MOVIE/OPENINGE.MOV")  # PARASHOT payload
    car = find_file(img, "MOVIE/CAR_1209.STR")  # CANONHT2 payload
    p_para = extract_file(p2, "MOVIE/PARASHOT.MOV")
    p_ht2 = extract_file(p2, "MOVIE/CANONHT2.MOV")
    g_open = extract_file(bytes(img), "MOVIE/OPENINGE.MOV")
    g_car = extract_file(bytes(img), "MOVIE/CAR_1209.STR")
    if not (g_open == p_para or g_open.startswith(p_para)):
        raise SystemExit("OPENINGE is not PARASHOT on 024 baseline")
    if not (g_car == p_ht2 or g_car.startswith(p_ht2)):
        raise SystemExit("CAR_1209 is not CANONHT2 on 024 baseline")

    # D2 engine aux for each src id
    def eng_meta(src_id: int, lba: int, name: str):
        _L, eng, a, b, c = d2_row(cd2, src_id)
        return lba, eng, a, b, c, name

    installed = {
        53: eng_meta(53, openinge.lba, "PARASHOT@OPENINGE"),
        51: eng_meta(51, car.lba, "CANONHT2@CAR_1209"),
    }
    # Append remaining streams only
    for src_id, name in (
        (50, "CANONHT1.MOV"),
        (52, "CANONH3F.MOV"),
        (55, "CANONHT0.MOV"),
        (59, "CANONH1P.MOV"),
    ):
        new_lba, _ = append_movie(img, p2, name)
        installed[src_id] = eng_meta(src_id, new_lba, name)
        print(f"append {name} LBA {new_lba} ({lba_to_msf(new_lba)})")

    print("reuse PARASHOT LBA", openinge.lba, lba_to_msf(openinge.lba))
    print("reuse CANONHT2 LBA", car.lba, lba_to_msf(car.lba))
    print("image end", len(img) // SECTOR - 1, lba_to_msf(len(img) // SECTOR - 1))
    if len(img) // SECTOR - 1 >= HARD_LBA_MAX:
        raise SystemExit("image past 80:00:00")

    mid = bytearray(extract_file(bytes(img), "MINT/MOVIE_ID.BIN"))
    if len(mid) < 61 * 20:
        mid.extend(b"\x00" * (61 * 20 - len(mid)))
    if len(mid) > USER:
        raise SystemExit("MOVIE_ID larger than one sector")
    for src_id, new_id in REMAP.items():
        lba, eng, a, b, c, name = installed[src_id]
        struct.pack_into("<IIIII", mid, new_id * 20, lba, eng, a, b, c)
        print(f"MOVIE_ID[{new_id}] <- D2#{src_id} {name} LBA={lba} eng={eng}")

    install_grow_form1(img, "MINT/MOVIE_ID.BIN", bytes(mid))
    mid1 = find_file(img, "MINT/MOVIE_ID.BIN")
    if mid1.lba != mid0.lba:
        raise SystemExit(f"MOVIE_ID moved {mid0.lba}->{mid1.lba}")
    print("MOVIE_ID stays", mid1.lba, lba_to_msf(mid1.lba), "size", mid1.size)

    for stem, need in (("FSHIP_12", 4), ("MD8_5", 1), ("MD8_52", 1)):
        new_dat, n = brute_patch_pmvie(extract_file(cd2, f"FIELD/{stem}.DAT"), REMAP)
        print(f"PMVIE {stem} {n}")
        if n < need:
            raise SystemExit(stem)
        install_grow_form1(img, f"FIELD/{stem}.DAT", new_dat)

    assert 58 in pmvie_set(extract_file(bytes(img), "FIELD/MD8_5.DAT"))
    assert {54, 55, 56, 57} <= pmvie_set(extract_file(bytes(img), "FIELD/FSHIP_12.DAT"))
    L58 = struct.unpack_from("<I", mid, 58 * 20)[0]
    if L58 != openinge.lba:
        raise SystemExit("eng58 must be OPENINGE/PARASHOT LBA")
    for stem in ("FSHIP_24", "BLIN66_6"):
        if decompress_all_with_header(extract_file(bytes(img), f"FIELD/{stem}.DAT")) != decompress_all_with_header(
            extract_file(cd2, f"FIELD/{stem}.DAT")
        ):
            raise SystemExit(stem)
    if extract_file(bytes(img), "SCUS_941.63") != extract_file(cd1, "SCUS_941.63"):
        raise SystemExit("SCUS")
    print("VERIFY OK")

    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    work_path.write_bytes(img)
    print("wrote", work_path, len(img), lba_to_msf(len(img) // SECTOR - 1))

    pack_dir = ROOT / "builder" / PACK_ID
    layer_dir = pack_dir / "layers"
    layer_dir.mkdir(parents=True, exist_ok=True)
    layer = build_layer(
        base_path,
        work_path,
        layer_id=PACK_ID + "-disc1",
        description=(
            "v0.1.26 path-engine under 80min: MOVIE_ID in-place; "
            "reuse PARASHOT/CANONHT2 LBAs; append HT0/HT1/H3F/H1P only"
        ),
    )
    outp = layer_dir / "disc1.layer.json"
    outp.write_text(json.dumps(layer, separators=(",", ":")) + "\n")
    print("layer", outp.stat().st_size, layer.get("stats"))
    if outp.stat().st_size > 100_000_000:
        raise SystemExit("layer >100MB")

    pack = {
        "id": PACK_ID,
        "version": "0.1.26",
        "name": "Single-disc path-engine (internal)",
        "blurb": "Internal. Auto with Single-disc. Engine movie ids + fields 71/255. Under 80min.",
        "hint": "Always included with Single-disc; not selectable.",
        "format": "ic-layer-v1",
        "compatibleBases": ["csr-v0.14.1"],
        "layout": "global",
        "discs": {"1": "./layers/disc1.layer.json"},
        "enabled": True,
        "uiHidden": True,
        "hidden": True,
        "beta": True,
        "status": "beta",
        "autoIncludeWhen": {"addonSelected": CORE},
    }
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2) + "\n")

    man_path = ROOT / "builder/manifest.json"
    man = json.loads(man_path.read_text())
    entry = {
        "id": PACK_ID,
        "name": pack["name"],
        "kind": "mod",
        "version": "0.1.26",
        "blurb": pack["blurb"],
        "hint": pack["hint"],
        "format": "ic-layer-v1",
        "compatibleBases": ["csr-v0.14.1"],
        "layout": "global",
        "discs": {"1": "./" + PACK_ID + "/layers/disc1.layer.json"},
        "enabled": True,
        "uiHidden": True,
        "hidden": True,
        "beta": True,
        "status": "beta",
        "autoIncludeWhen": {"addonSelected": CORE},
    }
    # disable 025 auto, face 024 as 0.1.26
    out = []
    found = False
    for a in man["addons"]:
        aid = a.get("id", "")
        if aid == CORE:
            a = dict(a)
            a["enabled"] = True
            a["name"] = "Single-disc"
            a["version"] = "0.1.26"
            a["blurb"] = (
                "Play the whole game from one Disc 1 image on CSR. "
                "v0.1.26: path-engine boot fix (under 80min CD) + PARASHOT/MD8."
            )
            a.pop("uiHidden", None)
            a.pop("hidden", None)
            out.append(a)
        elif aid == "single-disc-on-csr-v0.1.25":
            a = dict(a)
            a["enabled"] = False
            a["uiHidden"] = True
            a["hidden"] = True
            a["autoIncludeWhen"] = {}
            out.append(a)
        elif aid == PACK_ID:
            out.append(entry)
            found = True
        elif aid.startswith("single-disc-on-csr-v0.1.") and aid not in (CORE, PACK_ID, "single-disc-on-csr-v0.1.25"):
            a = dict(a)
            a["enabled"] = False
            out.append(a)
        else:
            # retarget autos that pointed at 025
            aw = a.get("autoIncludeWhen") or {}
            if aw.get("addonSelected") == "single-disc-on-csr-v0.1.25":
                a = dict(a)
                aw = dict(aw)
                aw["addonSelected"] = CORE
                a["autoIncludeWhen"] = aw
            out.append(a)
    if not found:
        out.append(entry)
    man["addons"] = out
    man_path.write_text(json.dumps(man, indent=2) + "\n")
    print("manifest ok", PACK_ID)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
