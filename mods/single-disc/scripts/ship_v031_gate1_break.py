#!/usr/bin/env python3
"""v0.1.31 Gate1: LOST2 a455 -> COS_BTM2; open COS break for a455; disable 27-30."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_layer import apply_layer
from bin_diff_to_layer import build_layer
from field_dat import load_field_dat, op_size
from ff7_opcodes import OPCODE_NAMES
from lzs import compress_all_with_header, decompress_all_with_header
from psx_mode2_iso import SECTOR, extract_file, find_file, replace_file_within_sectors

CORE = "single-disc-on-csr-v0.1.24"
PACK_ID = "single-disc-on-csr-v0.1.31"
STACK = [
    "single-disc-csr-manip-movies-v0.1.4",
    CORE,
    "single-disc-on-csr-v0.1.26",
]
DISABLE = {
    "single-disc-on-csr-v0.1.27",
    "single-disc-on-csr-v0.1.28",
    "single-disc-on-csr-v0.1.29",
    "single-disc-on-csr-v0.1.30",
}
BB_SHA12 = "617fbce93e71"


def rein(img: bytearray, path: str, data: bytes) -> None:
    meta = find_file(img, path)
    nsec = max(1, (meta.size + 2047) // 2048)
    if len(data) > nsec * 2048:
        raise SystemExit(f"{path} too big")
    replace_file_within_sectors(img, path, data)


def patch_lzs(dat: bytes, mut) -> bytes:
    dec = bytearray(decompress_all_with_header(dat))
    mut(dec)
    out = compress_all_with_header(bytes(dec))
    if decompress_all_with_header(out) != bytes(dec):
        raise SystemExit("LZS roundtrip fail")
    load_field_dat(out)
    return out


def mut_lost2(dec: bytearray) -> None:
    seq = (
        bytes.fromhex("1820000055a40112")
        + bytes.fromhex("da0000009a00000000000000000000")
        + bytes.fromhex("f00100")
        + bytes.fromhex("1820000055a4000b")
        + bytes.fromhex("600e02")
    )
    j = bytes(dec).find(seq)
    if j < 0:
        raise SystemExit("LOST2 IFUW site not found")
    if dec[j + 7] != 0x12:
        raise SystemExit("unexpected E")
    dec[j + 7] = 0x13


def mut_cos(dec: bytearray) -> None:
    pat = bytes.fromhex("1620000002020405")
    n = 0
    start = 0
    while True:
        i = bytes(dec).find(pat, start)
        if i < 0:
            break
        if dec[i + 8 : i + 13] == bytes.fromhex("8050030100"):
            dec[i + 6] = 0x00
            n += 1
        start = i + 1
    if n != 1:
        raise SystemExit(f"COS patches {n}")


def sim_lost2(dat: bytes, gm: int, bit84: int = 0) -> str:
    fd = load_field_dat(dat)
    for sc in fd.scripts:
        if sc.entity != "init" or sc.slot != 0:
            continue
        raw, pos = sc.raw, 0
        for _ in range(100):
            op = raw[pos]
            sz = max(op_size(raw, pos), 1)
            chunk = raw[pos : pos + sz]
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
            if name == "IFUB":
                c, e, v = chunk[4], chunk[5], chunk[3]
                cond = bool(bit84 & (1 << v)) if c == 9 else False
                fail = (pos + sz - 1) + e
                pos = fail if not cond else pos + sz
                continue
            if name == "IFUW":
                v = int.from_bytes(chunk[4:6], "little")
                c, e = chunk[6], chunk[7]
                table = {0: gm == v, 1: gm != v, 2: gm > v, 3: gm < v, 4: gm >= v, 5: gm <= v}
                cond = table.get(c, False)
                fail = (pos + sz - 1) + e
                pos = fail if not cond else pos + sz
                continue
            if name == "JMPF":
                pos = pos + sz + chunk[1]
                continue
            if name == "RET":
                return "RET"
            if name.startswith("MAPJUMP"):
                return f"MJ{int.from_bytes(chunk[1:3], 'little')}"
            if name == "MUSIC":
                return f"MUSIC{chunk[1]}"
            pos += sz
    return "miss"


def main() -> int:
    csr = Path.home() / "Final-Fantasy-7-CSR/cache/csr"
    cd1 = (csr / "FINALFANTASY7_D1.bin").read_bytes()
    cd2 = (csr / "FINALFANTASY7_D2.bin").read_bytes()
    img9 = bytearray(cd1)
    apply_layer(
        img9,
        json.loads((ROOT / "builder/single-disc-on-csr-v0.1.9/layers/disc1.layer.json").read_text()),
    )
    bb = extract_file(bytes(img9), "FIELD/BLACKBGB.DAT")
    if hashlib.sha256(bb).hexdigest()[:12] != BB_SHA12:
        raise SystemExit("BLACKBGB hash")

    lost = patch_lzs(extract_file(cd2, "FIELD/LOST2.DAT"), mut_lost2)
    cos = patch_lzs(extract_file(cd2, "FIELD/COS_BTM2.DAT"), mut_cos)
    if sim_lost2(lost, 0xA455) != "MJ526":
        raise SystemExit("sim a455")
    if sim_lost2(lost, 0x300) != "MUSIC1":
        raise SystemExit("sim 300")

    base = bytearray(cd1)
    for a in STACK:
        apply_layer(base, json.loads((ROOT / f"builder/{a}/layers/disc1.layer.json").read_text()))
    base_path = ROOT / "workspace/iso-extract/_tmp026_for_v031.bin"
    work_path = ROOT / "workspace/iso-extract/sd_v031_work.bin"
    base_path.parent.mkdir(parents=True, exist_ok=True)
    base_path.write_bytes(base)
    img = bytearray(base)
    rein(img, "FIELD/BLACKBGB.DAT", bb)
    rein(img, "FIELD/LOST2.DAT", lost)
    rein(img, "FIELD/COS_BTM2.DAT", cos)
    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - len(img) % SECTOR))
    work_path.write_bytes(img)

    pack_dir = ROOT / "builder" / PACK_ID
    (pack_dir / "layers").mkdir(parents=True, exist_ok=True)
    layer = build_layer(
        base_path,
        work_path,
        layer_id=PACK_ID + "-disc1",
        description="v0.1.31 Gate1 LOST2->COS_BTM2 + COS open a455",
    )
    (pack_dir / "layers/disc1.layer.json").write_text(json.dumps(layer, separators=(",", ":")) + "\n")
    pack = {
        "id": PACK_ID,
        "version": "0.1.31",
        "name": "Single-disc break (internal)",
        "blurb": "Internal auto: Gate1 LOST2 to COS_BTM2 break.",
        "hint": "Always with Single-disc.",
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

    man = json.loads((ROOT / "builder/manifest.json").read_text())
    entry = {
        "id": PACK_ID,
        "name": pack["name"],
        "kind": "mod",
        "version": "0.1.31",
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
    out, found = [], False
    for a in man["addons"]:
        aid = a.get("id")
        if aid == CORE:
            a = dict(a)
            a["version"] = "0.1.31"
            a["name"] = "Single-disc"
            a["blurb"] = (
                "Play the whole game from one Disc 1 image on CSR. "
                "v0.1.31: disc1 to disc2 break scene (COS_BTM2)."
            )
            out.append(a)
        elif aid in DISABLE:
            a = dict(a)
            a["enabled"] = False
            a["autoIncludeWhen"] = {}
            a["uiHidden"] = True
            a["hidden"] = True
            out.append(a)
        elif aid == PACK_ID:
            out.append(entry)
            found = True
        else:
            out.append(a)
    if not found:
        out.append(entry)
    man["addons"] = out
    (ROOT / "builder/manifest.json").write_text(json.dumps(man, indent=2) + "\n")
    print("ok", PACK_ID, layer.get("stats"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
