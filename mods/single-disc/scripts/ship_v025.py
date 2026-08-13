#!/usr/bin/env python3
"""single-disc-on-csr-v0.1.25 — cumulative pack vs CSR+movies.

Fixes on top of v0.1.24 content:
  - Grow MOVIE_ID to 61 rows; D2 path streams at engine ids 54-59
  - Remap FSHIP_12/MD8_5/MD8_52 PMVIE to those ids (53->58 PARASHOT)
  - CSR D2 FIELD for FSHIP_24 (#71) and BLIN66_6 (#255)
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
from psx_mode2_iso import SECTOR, USER, extract_file, find_file, replace_file_padded  # noqa: E402

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
# D2 eng id -> new D1 eng id (keep 0..53 early-game)
REMAP = {55: 54, 59: 55, 50: 56, 51: 57, 53: 58, 52: 59}


def install_grow_form1(img: bytearray, path: str, data: bytes) -> None:
    meta = find_file(img, path)
    if len(data) <= meta.size:
        replace_file_padded(img, path, data)
        return
    nsec = (len(data) + USER - 1) // USER
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


def append_movie(img: bytearray, src_img: bytes, name: str) -> tuple[int, int]:
    meta = find_file(src_img, f"MOVIE/{name}")
    raw = _raw_sectors(src_img, meta.lba, meta.size)
    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    new_lba = len(img) // SECTOR
    img.extend(raw)
    return new_lba, meta.size


def d2_engine_meta(cd2: bytes, eng_id: int) -> tuple[int, int, int, int, int, str]:
    mid = extract_file(cd2, "MINT/MOVIE_ID.BIN")
    L, eng, a, b, c = struct.unpack_from("<5I", mid, eng_id * 20)
    name = D2_PATH_STREAMS[eng_id]
    meta = find_file(cd2, f"MOVIE/{name}")
    if meta.lba != L:
        raise SystemExit(f"D2 id {eng_id} {name} LBA mismatch {L} vs {meta.lba}")
    return L, eng, a, b, c, name


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

    # Layer baseline = CSR + movies only (same as v0.1.24) so pack is standalone
    movies_layer = ROOT / f"builder/{MOVIES}/layers/disc1.layer.json"
    prev_layer = ROOT / f"builder/{PREV}/layers/disc1.layer.json"
    base_path = ROOT / "workspace/iso-extract/_csr_plus_movies_baseline_sd025.bin"
    work_path = ROOT / "workspace/iso-extract/sd_v025_work.bin"

    print("CSR + movies baseline ...")
    base = bytearray(cd1)
    apply_layer(base, json.loads(movies_layer.read_text()))
    base_path.write_bytes(base)
    print("baseline", len(base), "mod", len(base) % SECTOR)

    print("Apply SD 0.1.24 cumulative content ...")
    img = bytearray(base)
    apply_layer(img, json.loads(prev_layer.read_text()))
    print("after 024", len(img), "mod", len(img) % SECTOR)

    # CSR D2 field trims #71 / #255
    for stem in ("FSHIP_24", "BLIN66_6"):
        data = extract_file(cd2, f"FIELD/{stem}.DAT")
        install_grow_form1(img, f"FIELD/{stem}.DAT", data)
        got = extract_file(bytes(img), f"FIELD/{stem}.DAT")
        if got != data and not (got.startswith(data) or data.startswith(got)):
            # compare decompressed
            if decompress_all_with_header(got) != decompress_all_with_header(data):
                raise SystemExit(f"failed install {stem}")
        print("CSR_D2", stem, "iso", len(got), "src", len(data))

    # Engine path streams + MOVIE_ID grow
    mid = bytearray(extract_file(bytes(img), "MINT/MOVIE_ID.BIN"))
    if len(mid) < 61 * 20:
        mid.extend(b"\x00" * (61 * 20 - len(mid)))

    installed: dict[int, tuple[int, int, tuple[int, int, int], str]] = {}
    for src_id, name in D2_PATH_STREAMS.items():
        _L, eng, a, b, c, n = d2_engine_meta(cd2, src_id)
        new_lba, _iso = append_movie(img, p2, name)
        installed[src_id] = (new_lba, eng, (a, b, c), name)
        print(f"stream {name} eng_src={src_id} -> LBA {new_lba}")

    for src_id, new_id in REMAP.items():
        lba, eng, (a, b, c), name = installed[src_id]
        struct.pack_into("<IIIII", mid, new_id * 20, lba, eng, a, b, c)
        print(f"MOVIE_ID[{new_id}] <- D2 id{src_id} {name}")

    install_grow_form1(img, "MINT/MOVIE_ID.BIN", bytes(mid))

    for stem, need in (
        ("FSHIP_12", 4),
        ("MD8_5", 1),
        ("MD8_52", 1),
    ):
        src = extract_file(cd2, f"FIELD/{stem}.DAT")
        new_dat, n = brute_patch_pmvie(src, REMAP)
        print(f"PMVIE patch {stem}: {n}")
        if n < need:
            raise SystemExit(f"{stem} only {n} PMVIE patches")
        install_grow_form1(img, f"FIELD/{stem}.DAT", new_dat)

    # Verify
    assert 58 in pmvie_set(extract_file(bytes(img), "FIELD/MD8_5.DAT"))
    assert {54, 55, 56, 57} <= pmvie_set(extract_file(bytes(img), "FIELD/FSHIP_12.DAT"))
    assert 59 in pmvie_set(extract_file(bytes(img), "FIELD/MD8_52.DAT"))
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
            raise SystemExit(f"{stem} decompressed != CSR_D2")
    print("VERIFY OK")

    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    work_path.write_bytes(img)
    print("wrote", work_path, len(img))

    pack_dir = ROOT / "builder" / PACK_ID
    layer_dir = pack_dir / "layers"
    layer_dir.mkdir(parents=True, exist_ok=True)
    print("diff vs CSR+movies ...")
    layer = build_layer(
        base_path,
        work_path,
        layer_id=PACK_ID + "-disc1",
        description=(
            "Single-disc on CSR v0.1.25 — cumulative; D2 engine path mids "
            "54-59 (PARASHOT@58); CSR D2 FSHIP_24+BLIN66_6; keeps 0.1.24 path FMVs"
        ),
    )
    (layer_dir / "disc1.layer.json").write_text(
        json.dumps(layer, separators=(",", ":")) + "\n"
    )
    print("records", len(layer["records"]), layer.get("stats"))

    old = json.loads((ROOT / f"builder/{PREV}/pack.json").read_text())
    pack = {
        **{k: v for k, v in old.items() if k not in ("id", "version", "blurb", "betaNote")},
        "id": PACK_ID,
        "version": "0.1.25",
        "name": "Single-disc",
        "blurb": (
            "Play the whole game from one Disc 1 image on CSR. "
            "v0.1.25: PARASHOT on MD8_5 via D2 engine movie ids; "
            "CSR D2 trims on FSHIP_24 and BLIN66_6."
        ),
        "hint": "Use one Disc 1 image for the full CSR game.",
        "beta": True,
        "status": "beta",
        "betaNote": "Single-disc is still playtesting; known freezes and glitches on some paths.",
        "discs": {"1": "./layers/disc1.layer.json"},
    }
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2) + "\n")

    man_path = ROOT / "builder/manifest.json"
    man = json.loads(man_path.read_text())
    entry = {
        "id": PACK_ID,
        "name": "Single-disc",
        "kind": "mod",
        "version": "0.1.25",
        "blurb": pack["blurb"],
        "hint": pack["hint"],
        "format": "ic-layer-v1",
        "compatibleBases": ["csr-v0.14.1"],
        "layout": "global",
        "discs": {"1": "./" + PACK_ID + "/layers/disc1.layer.json"},
        "enabled": True,
        "beta": True,
        "status": "beta",
        "betaNote": pack["betaNote"],
    }
    for a in man["addons"]:
        aid = a.get("id", "")
        if aid.startswith("single-disc-on-csr-v0.1.") and aid != PACK_ID:
            a["enabled"] = False
        aw = a.get("autoIncludeWhen") or {}
        if isinstance(aw.get("addonSelected"), str) and aw["addonSelected"].startswith(
            "single-disc-on-csr-v0.1."
        ):
            aw["addonSelected"] = PACK_ID
            a["autoIncludeWhen"] = aw
    if any(a.get("id") == PACK_ID for a in man["addons"]):
        man["addons"] = [entry if a.get("id") == PACK_ID else a for a in man["addons"]]
    else:
        man["addons"].append(entry)
    man_path.write_text(json.dumps(man, indent=2) + "\n")
    print("manifest ok", PACK_ID)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
