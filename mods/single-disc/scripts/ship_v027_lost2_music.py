#!/usr/bin/env python3
"""v0.1.27: LOST2 (#634) music — NOP AKAO2 0x9A resume before MUSIC.

CSR D2 LOST2 resumes music (AKAO2 0x9A) then MUSIC. Multi-disc has BLACKBGB
DSKCG pause first. Single-disc Ask-strips DSKCG so resume is a no-op and
MUSIC never audibly starts. JMPF over those AKAO2 ops; keep CSR D2 LOST2.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mods/single-disc/scripts"))

from apply_layer import apply_layer
from bin_diff_to_layer import build_layer
from disc_sources import csr_root
from field_dat import load_field_dat, op_size
from ff7_opcodes import OPCODE_NAMES
from lzs import compress_all_with_header, decompress_all_with_header
from psx_mode2_iso import SECTOR, USER, extract_file, find_file, replace_file_padded, _write_user
from inject_movies_by_disc_id import _patch_dirent_lba_size

CORE, PATH, MOVIES = "single-disc-on-csr-v0.1.24", "single-disc-on-csr-v0.1.26", "single-disc-csr-manip-movies-v0.1.4"
PACK_ID = "single-disc-on-csr-v0.1.27"
AKAO2_RESUME = bytes.fromhex("da0000009a00000000000000000000")


def install_form1(img: bytearray, path: str, data: bytes) -> None:
    meta = find_file(img, path)
    if len(data) <= meta.size:
        replace_file_padded(img, path, data)
        return
    if (len(data) + USER - 1) // USER != (meta.size + USER - 1) // USER:
        raise SystemExit(f"{path}: longer than slot")
    rem, sector, off = len(data), meta.lba, 0
    while rem > 0:
        take = min(USER, rem)
        chunk = data[off : off + take]
        if take < USER:
            user = bytearray(img[sector * SECTOR + 24 : sector * SECTOR + 24 + USER])
            user[:take] = chunk
            user[take:] = b"\x00" * (USER - take)
            _write_user(img, sector, bytes(user))
        else:
            _write_user(img, sector, chunk)
        off += take
        rem -= take
        sector += 1
    _patch_dirent_lba_size(img, path, meta.lba, len(data))


def patch_lost2(dat: bytes) -> tuple[bytes, int]:
    dec = decompress_all_with_header(dat)
    fd = load_field_dat(dat)
    buf = bytearray(dec)
    n = 0
    for sc in fd.scripts:
        if sc.entity != "init" or sc.slot != 0:
            continue
        idx = buf.find(sc.raw)
        if idx < 0:
            raise SystemExit("init/0 missing")
        piece = bytearray(sc.raw)
        pos = 0
        while pos < len(piece):
            op, sz = piece[pos], max(op_size(piece, pos), 1)
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
            if name == "AKAO2" and piece[pos : pos + sz] == AKAO2_RESUME:
                piece[pos] = 0x10  # JMPF
                piece[pos + 1] = 13  # skip rest of 15-byte slot
                piece[pos + 2 : pos + 15] = b"\x00" * 13
                n += 1
            pos += sz
        buf[idx : idx + len(sc.raw)] = piece
    out = compress_all_with_header(bytes(buf))
    fd2 = load_field_dat(out)
    mus = 0
    for sc in fd2.scripts:
        if sc.entity != "init" or sc.slot != 0:
            continue
        pos = 0
        while pos < len(sc.raw):
            op, sz = sc.raw[pos], max(op_size(sc.raw, pos), 1)
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
            if name == "AKAO2" and sc.raw[pos : pos + sz] == AKAO2_RESUME:
                raise SystemExit("still has resume")
            if name == "MUSIC":
                mus += 1
            pos += sz
    if mus < 2:
        raise SystemExit(f"MUSIC {mus}")
    return out, n


def main() -> int:
    csr = csr_root()
    cd1p = Path.home() / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D1.bin"
    cd2p = Path.home() / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D2.bin"
    cd1 = (cd1p if cd1p.is_file() else csr / "cache/csr/FINALFANTASY7_D1.bin").read_bytes()
    cd2 = (cd2p if cd2p.is_file() else csr / "cache/csr/FINALFANTASY7_D2.bin").read_bytes()
    base_path = ROOT / "workspace/iso-extract/_tmp026_for_v027.bin"
    work_path = ROOT / "workspace/iso-extract/sd_v027_work.bin"
    img = bytearray(cd1)
    for a in (MOVIES, CORE, PATH):
        apply_layer(img, json.loads((ROOT / f"builder/{a}/layers/disc1.layer.json").read_text()))
    base_path.write_bytes(img)
    patched, n = patch_lost2(extract_file(cd2, "FIELD/LOST2.DAT"))
    print("NOP AKAO2", n)
    if n != 2:
        raise SystemExit(n)
    install_form1(img, "FIELD/LOST2.DAT", patched)
    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - len(img) % SECTOR))
    work_path.write_bytes(img)
    pack_dir = ROOT / "builder" / PACK_ID
    (pack_dir / "layers").mkdir(parents=True, exist_ok=True)
    layer = build_layer(base_path, work_path, layer_id=PACK_ID + "-disc1",
                        description="v0.1.27 LOST2: JMPF over AKAO2 0x9A before MUSIC")
    (pack_dir / "layers/disc1.layer.json").write_text(json.dumps(layer, separators=(",", ":")) + "\n")
    print("layer", (pack_dir / "layers/disc1.layer.json").stat().st_size, layer.get("stats"))
    pack = {"id": PACK_ID, "version": "0.1.27", "name": "Single-disc LOST2 music (internal)",
            "blurb": "Internal auto: LOST2 #634 music after disc break.", "hint": "Always with Single-disc.",
            "format": "ic-layer-v1", "compatibleBases": ["csr-v0.14.1"], "layout": "global",
            "discs": {"1": "./layers/disc1.layer.json"}, "enabled": True, "uiHidden": True, "hidden": True,
            "beta": True, "status": "beta", "autoIncludeWhen": {"addonSelected": CORE}}
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2) + "\n")
    man = json.loads((ROOT / "builder/manifest.json").read_text())
    entry = {"id": PACK_ID, "name": pack["name"], "kind": "mod", "version": "0.1.27", "blurb": pack["blurb"],
             "hint": pack["hint"], "format": "ic-layer-v1", "compatibleBases": ["csr-v0.14.1"], "layout": "global",
             "discs": {"1": "./" + PACK_ID + "/layers/disc1.layer.json"}, "enabled": True, "uiHidden": True,
             "hidden": True, "beta": True, "status": "beta", "autoIncludeWhen": {"addonSelected": CORE}}
    out, found = [], False
    for a in man["addons"]:
        if a.get("id") == CORE:
            a = dict(a); a["version"] = "0.1.27"; a["name"] = "Single-disc"
            a["blurb"] = "Play the whole game from one Disc 1 image on CSR. v0.1.27: LOST2 break music fix."
            out.append(a)
        elif a.get("id") == PACK_ID:
            out.append(entry); found = True
        else:
            out.append(a)
    if not found:
        out.append(entry)
    man["addons"] = out
    (ROOT / "builder/manifest.json").write_text(json.dumps(man, indent=2) + "\n")
    print("ok", PACK_ID)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
