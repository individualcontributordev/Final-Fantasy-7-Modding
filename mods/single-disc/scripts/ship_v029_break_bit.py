#!/usr/bin/env python3
"""v0.1.29: fix disc1→2 break — set LOST2 gate bit on BLACKBGB; restore CSR D2 fields.

Root cause (sim with correct IF compare types):
  LOST2 only MAPJUMPs cos_btm2 (#526) when bank3[0x84] bit4 is set AND GM==0xa455.
  LOSIN2 sets GM 0xa455 but BITOFFs 0x84 bit4. Nothing on BLACKBGB LOST2 path sets
  bit4 → LOST2 init hits RET with no music/break. Forcing COS_BTM2 (v0.1.6–7/28)
  blacks the scene when GM>=0x0202 (v0.1.8 finding).

Fix:
  1) Restore pure CSR D2 LOST2 + COS_BTM2 (undo v0.1.27/28 script forces)
  2) BLACKBGB: before each MAPJUMP #634, same-length swap so LZS size stays valid:
       WAIT 04 + WAIT 08 + BITON 0x89/1  (10 bytes)
     → BITON 0x84/4 + BITON 0x89/1 + JMPF 0 (10 bytes, JMPF0 = 2-byte nop)
     Path2 keeps its trailing WAIT 08 before MAPJUMP.
"""
from __future__ import annotations

import json
import sys
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
from psx_mode2_iso import SECTOR, extract_file, find_file, replace_file_within_sectors

CORE = "single-disc-on-csr-v0.1.24"
STACK = [
    "single-disc-csr-manip-movies-v0.1.4",
    CORE,
    "single-disc-on-csr-v0.1.26",
    "single-disc-on-csr-v0.1.27",
    "single-disc-on-csr-v0.1.28",
]
PACK_ID = "single-disc-on-csr-v0.1.29"

# WAIT04 + WAIT08 + BITON bank3/0x89#1  →  BITON bank3/0x84#4 + BITON 0x89#1 + JMPF 0
# Same 10 bytes. Anchor: only at sites that lead into MAPJUMP #634 (path1 direct, path2 via WAIT08).
OLD = bytes.fromhex("24040024080082308901")
NEW = bytes.fromhex("82308404823089011000")  # BITON 84/4, BITON 89/1, JMPF +0
MJ634 = bytes.fromhex("607a02fdfeb213710000")
WAIT08 = bytes.fromhex("240800")


def patch_blackbgb(dat: bytes) -> tuple[bytes, int]:
    dec = bytearray(decompress_all_with_header(dat))
    if len(OLD) != len(NEW):
        raise SystemExit(f"length mismatch {len(OLD)}!={len(NEW)}")
    n = 0
    start = 0
    while True:
        j = bytes(dec).find(OLD, start)
        if j < 0:
            break
        after = j + len(OLD)
        # path1: OLD | MJ634   path2: OLD | WAIT08 | MJ634
        ok_site = dec[after : after + len(MJ634)] == MJ634 or (
            dec[after : after + len(WAIT08)] == WAIT08
            and dec[after + len(WAIT08) : after + len(WAIT08) + len(MJ634)] == MJ634
        )
        if ok_site:
            dec[j : j + len(OLD)] = NEW
            n += 1
            start = j + len(NEW)
        else:
            start = j + 1
    if n < 2:
        raise SystemExit(f"expected 2 BLACKBGB LOST2 sites, got {n}")
    out = compress_all_with_header(bytes(dec))
    # round-trip integrity
    rt = decompress_all_with_header(out)
    if rt != bytes(dec):
        raise SystemExit(f"LZS roundtrip mismatch {len(rt)} vs {len(dec)}")
    fd = load_field_dat(out)
    ok = 0
    for sc in fd.scripts:
        if sc.entity != "init" or sc.slot != 0:
            continue
        pos = 0
        while pos < len(sc.raw):
            op = sc.raw[pos]
            sz = max(op_size(sc.raw, pos), 1)
            chunk = sc.raw[pos : pos + sz]
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
            if name == "BITON" and chunk.hex() == "82308404":
                ok += 1
            pos += sz
    if ok < 2:
        raise SystemExit(f"BITON 84/04 count in init={ok}, want >=2")
    return out, n


def reinstall(img: bytearray, path: str, data: bytes) -> None:
    meta = find_file(img, path)
    nsec = max(1, (meta.size + 2047) // 2048)
    if len(data) > nsec * 2048:
        raise SystemExit(f"{path} too big {len(data)}>{nsec*2048}")
    replace_file_within_sectors(img, path, data)


def main() -> int:
    csr = csr_root()
    cd1p = Path.home() / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D1.bin"
    cd2p = Path.home() / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D2.bin"
    cd1 = (cd1p if cd1p.is_file() else csr / "cache/csr/FINALFANTASY7_D1.bin").read_bytes()
    cd2 = (cd2p if cd2p.is_file() else csr / "cache/csr/FINALFANTASY7_D2.bin").read_bytes()

    base_path = ROOT / "workspace/iso-extract/_tmp028_for_v029.bin"
    work_path = ROOT / "workspace/iso-extract/sd_v029_work.bin"
    img = bytearray(cd1)
    for a in STACK:
        p = ROOT / f"builder/{a}/layers/disc1.layer.json"
        if p.is_file():
            apply_layer(img, json.loads(p.read_text()))
    base_path.write_bytes(img)
    print("base", len(img))

    # Restore pure CSR D2 LOST2 + COS_BTM2
    reinstall(img, "FIELD/LOST2.DAT", extract_file(cd2, "FIELD/LOST2.DAT"))
    reinstall(img, "FIELD/COS_BTM2.DAT", extract_file(cd2, "FIELD/COS_BTM2.DAT"))
    print("restored CSR D2 LOST2 + COS_BTM2")

    bb = extract_file(bytes(img), "FIELD/BLACKBGB.DAT")
    bb2, n = patch_blackbgb(bb)
    print("BLACKBGB BITON patches", n)
    reinstall(img, "FIELD/BLACKBGB.DAT", bb2)

    # Sim: LOST2 with GM=a455 and bit4 set must MAPJUMP 526
    from field_dat import load_field_dat as LF

    def sim(dat, gm, bit84):
        fd = LF(dat)
        for sc in fd.scripts:
            if sc.entity != "init" or sc.slot != 0:
                continue
            raw = sc.raw
            pos = 0
            for _ in range(80):
                op = raw[pos]
                sz = max(op_size(raw, pos), 1)
                chunk = raw[pos : pos + sz]
                name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
                if name == "IFUB":
                    C, E, V = chunk[4], chunk[5], chunk[3]
                    if C == 9:
                        cond = bool(bit84 & (1 << V))
                    else:
                        cond = False
                    fail = (pos + sz - 1) + E
                    pos = fail if not cond else pos + sz
                    continue
                if name == "IFUW":
                    V = int.from_bytes(chunk[4:6], "little")
                    C, E = chunk[6], chunk[7]
                    table = {
                        0: gm == V,
                        1: gm != V,
                        2: gm > V,
                        3: gm < V,
                        4: gm >= V,
                        5: gm <= V,
                    }
                    cond = table.get(C, False)
                    fail = (pos + sz - 1) + E
                    pos = fail if not cond else pos + sz
                    continue
                if name == "JMPF":
                    pos = pos + sz + chunk[1]
                    continue
                if name == "RET":
                    return "RET"
                if name.startswith("MAPJUMP"):
                    return f"MJ{int.from_bytes(chunk[1:3], 'little')}"
                pos += sz
            return "timeout"

    lost = extract_file(bytes(img), "FIELD/LOST2.DAT")
    r = sim(lost, 0xA455, (1 << 4))
    print("sim a455+bit4", r)
    if r != "MJ526":
        raise SystemExit(f"expected MJ526 got {r}")
    r2 = sim(lost, 0xA455, 0)
    print("sim a455 no bit", r2)

    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - len(img) % SECTOR))
    work_path.write_bytes(img)

    pack_dir = ROOT / "builder" / PACK_ID
    (pack_dir / "layers").mkdir(parents=True, exist_ok=True)
    layer = build_layer(
        base_path,
        work_path,
        layer_id=PACK_ID + "-disc1",
        description="v0.1.29: BLACKBGB BITON 84/4 before LOST2; pure CSR D2 LOST2+COS_BTM2",
    )
    (pack_dir / "layers/disc1.layer.json").write_text(
        json.dumps(layer, separators=(",", ":")) + "\n"
    )
    print("layer", (pack_dir / "layers/disc1.layer.json").stat().st_size, layer.get("stats"))

    pack = {
        "id": PACK_ID,
        "version": "0.1.29",
        "name": "Single-disc break bit (internal)",
        "blurb": "Internal auto: set LOST2 break gate bit on BLACKBGB; CSR D2 LOST2/COS_BTM2.",
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
        "version": "0.1.29",
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
        if a.get("id") == CORE:
            a = dict(a)
            a["version"] = "0.1.29"
            a["name"] = "Single-disc"
            a["blurb"] = (
                "Play the whole game from one Disc 1 image on CSR. "
                "v0.1.29: disc-break gate bit on BLACKBGB (LOST2→COS_BTM2)."
            )
            out.append(a)
        elif a.get("id") == PACK_ID:
            out.append(entry)
            found = True
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
