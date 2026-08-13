#!/usr/bin/env python3
"""v0.1.28: restore disc1→2 break scene (LOST2→COS_BTM2) + music path.

Regression: later packs restored pure CSR D2 LOST2 and dropped v0.1.6/0.1.7 forces.
BLACKBGB Ask-strips DSKCG then MAPJUMP LOST2. CSR D2 LOST2 only MAPJUMPs
cos_btm2 (#526) when IFUW GM==0xa455 takes the fall-through; on single-disc the
else (+0x0B) skips → stay in LOST2 forest, no break, odd music.

Fix (same as v0.1.6/0.1.7):
  - LOST2: IFUW 1820000055a4 else 0x0B → 0 so MAPJUMP cos_btm2 always after music
  - COS_BTM2: clear large IFUW 55a4 else-jumps (disc-id gate)
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

CORE, P26, P27 = (
    "single-disc-on-csr-v0.1.24",
    "single-disc-on-csr-v0.1.26",
    "single-disc-on-csr-v0.1.27",
)
MOVIES = "single-disc-csr-manip-movies-v0.1.4"
PACK_ID = "single-disc-on-csr-v0.1.28"
PAT = bytes.fromhex("1820000055a4")


AKAO2_RESUME = bytes.fromhex("da0000009a00000000000000000000")


def force_lost2(dec: bytearray) -> tuple[int, int]:
    """IFUW else 0x0B→0 before MAPJUMP cos_btm2; JMPF over AKAO2 0x9A resume."""
    n_ifuw = 0
    i = 0
    while True:
        j = bytes(dec).find(PAT, i)
        if j < 0:
            break
        if j + 8 <= len(dec) and dec[j + 7] == 0x0B:
            window = bytes(dec[j : j + 24])
            if b"\x60\x0e\x02" in window or b"\x0e\x02" in window[8:20]:
                dec[j + 7] = 0
                n_ifuw += 1
        i = j + 1
    # AKAO2 resume before MUSIC (silences without DSKCG)
    n_akao = 0
    i = 0
    while True:
        j = bytes(dec).find(AKAO2_RESUME, i)
        if j < 0:
            break
        dec[j] = 0x10
        dec[j + 1] = 13
        dec[j + 2 : j + 15] = b"\x00" * 13
        n_akao += 1
        i = j + 1
    return n_ifuw, n_akao


def force_cos_btm2(dec: bytearray) -> list[tuple[int, int]]:
    forced = []
    i = 0
    while True:
        j = bytes(dec).find(PAT, i)
        if j < 0:
            break
        ej = dec[j + 7]
        if ej >= 0x08:
            dec[j + 7] = 0
            forced.append((j, ej))
        i = j + 1
    return forced


def reinstall(img: bytearray, path: str, new_raw: bytes) -> None:
    meta = find_file(img, path)
    nsec = max(1, (meta.size + 2047) // 2048)
    if len(new_raw) > nsec * 2048:
        raise SystemExit(f"{path}: {len(new_raw)} > slot {nsec*2048}")
    replace_file_within_sectors(img, path, new_raw)


def main() -> int:
    csr = csr_root()
    cd1p = Path.home() / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D1.bin"
    cd2p = Path.home() / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D2.bin"
    cd1 = (cd1p if cd1p.is_file() else csr / "cache/csr/FINALFANTASY7_D1.bin").read_bytes()
    cd2 = (cd2p if cd2p.is_file() else csr / "cache/csr/FINALFANTASY7_D2.bin").read_bytes()

    base_path = ROOT / "workspace/iso-extract/_tmp027_for_v028.bin"
    work_path = ROOT / "workspace/iso-extract/sd_v028_work.bin"
    img = bytearray(cd1)
    for a in (MOVIES, CORE, P26, P27):
        p = ROOT / f"builder/{a}/layers/disc1.layer.json"
        if p.is_file():
            apply_layer(img, json.loads(p.read_text()))
    base_path.write_bytes(img)

    # LOST2 from pure CSR D2 + force break MAPJUMP
    lost_raw = extract_file(cd2, "FIELD/LOST2.DAT")
    lost_dec = bytearray(decompress_all_with_header(lost_raw))
    n_ifuw, n_akao = force_lost2(lost_dec)
    print("LOST2 IFUW else cleared", n_ifuw, "AKAO2 resume JMPF", n_akao)
    if n_ifuw < 1:
        raise SystemExit("LOST2 break IFUW not found")
    if n_akao < 2:
        raise SystemExit(f"LOST2 AKAO2 resume NOP count {n_akao}")
    lost_new = compress_all_with_header(bytes(lost_dec))
    reinstall(img, "FIELD/LOST2.DAT", lost_new)

    # verify MAPJUMP 526 reachable: simulate no RET before MJ when GM set
    fd = load_field_dat(lost_new)
    ok = False
    for sc in fd.scripts:
        if sc.entity != "init" or sc.slot != 0:
            continue
        pos = 0
        while pos < len(sc.raw):
            op, sz = sc.raw[pos], max(op_size(sc.raw, pos), 1)
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
            chunk = sc.raw[pos : pos + sz]
            if name == "IFUW" and chunk.startswith(PAT) and chunk[-1] == 0x0B:
                raise SystemExit("LOST2 still has else 0x0B")
            if name.startswith("MAPJUMP") and int.from_bytes(chunk[1:3], "little") == 526:
                ok = True
            pos += sz
    if not ok:
        raise SystemExit("no MAPJUMP 526")
    print("LOST2 MAPJUMP cos_btm2 OK")

    # COS_BTM2 from CSR D2 + force gates (built stack may have D1-sized hybrid)
    cos_raw = extract_file(cd2, "FIELD/COS_BTM2.DAT")
    cos_dec = bytearray(decompress_all_with_header(cos_raw))
    forced = force_cos_btm2(cos_dec)
    print("COS_BTM2 IFUW forced", len(forced), forced[:6])
    if len(forced) < 1:
        raise SystemExit("COS_BTM2 no gates")
    cos_new = compress_all_with_header(bytes(cos_dec))
    reinstall(img, "FIELD/COS_BTM2.DAT", cos_new)
    print("COS_BTM2 installed", len(cos_new))

    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - len(img) % SECTOR))
    work_path.write_bytes(img)

    pack_dir = ROOT / "builder" / PACK_ID
    (pack_dir / "layers").mkdir(parents=True, exist_ok=True)
    layer = build_layer(
        base_path,
        work_path,
        layer_id=PACK_ID + "-disc1",
        description="v0.1.28 break: LOST2 force MAPJUMP cos_btm2 + COS_BTM2 IFUW open",
    )
    (pack_dir / "layers/disc1.layer.json").write_text(
        json.dumps(layer, separators=(",", ":")) + "\n"
    )
    print("layer", (pack_dir / "layers/disc1.layer.json").stat().st_size, layer.get("stats"))

    pack = {
        "id": PACK_ID,
        "version": "0.1.28",
        "name": "Single-disc break scene (internal)",
        "blurb": "Internal auto: LOST2→COS_BTM2 break after disc transition.",
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
        "version": "0.1.28",
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
            a["version"] = "0.1.28"
            a["name"] = "Single-disc"
            a["blurb"] = (
                "Play the whole game from one Disc 1 image on CSR. "
                "v0.1.28: disc-break scene COS_BTM2 + LOST2 music path."
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
