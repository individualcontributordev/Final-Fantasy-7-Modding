#!/usr/bin/env python3
"""v0.1.30: restore v0.1.8/0.1.9 disc-break fields (undo 0.1.27–0.1.29).

Playtest: 0.1.29 BITON + earlier IFUW/AKAO2 forces → black/glitch transition.
Known-good (human OK on 0.1.9): Ask-stripped BLACKBGB, pure CSR D2 LOST2+COS_BTM2.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_layer import apply_layer
from bin_diff_to_layer import build_layer
from psx_mode2_iso import SECTOR, extract_file, find_file, replace_file_within_sectors

CORE = "single-disc-on-csr-v0.1.24"
PACK_ID = "single-disc-on-csr-v0.1.30"
STACK = [
    "single-disc-csr-manip-movies-v0.1.4",
    CORE,
    "single-disc-on-csr-v0.1.26",
    "single-disc-on-csr-v0.1.27",
    "single-disc-on-csr-v0.1.28",
    "single-disc-on-csr-v0.1.29",
]
BB_SHA12 = "617fbce93e71"  # Ask-stripped BLACKBGB from v0.1.9


def rein(img: bytearray, path: str, data: bytes) -> None:
    meta = find_file(img, path)
    nsec = max(1, (meta.size + 2047) // 2048)
    if len(data) > nsec * 2048:
        raise SystemExit(f"{path} too big {len(data)}>{nsec * 2048}")
    replace_file_within_sectors(img, path, data)


def main() -> int:
    csr = Path.home() / "Final-Fantasy-7-CSR/cache/csr"
    cd1 = (csr / "FINALFANTASY7_D1.bin").read_bytes()
    cd2 = (csr / "FINALFANTASY7_D2.bin").read_bytes()

    img9 = bytearray(cd1)
    apply_layer(
        img9,
        json.loads(
            (ROOT / "builder/single-disc-on-csr-v0.1.9/layers/disc1.layer.json").read_text()
        ),
    )
    bb = extract_file(bytes(img9), "FIELD/BLACKBGB.DAT")
    if hashlib.sha256(bb).hexdigest()[:12] != BB_SHA12:
        raise SystemExit("unexpected BLACKBGB from v0.1.9")

    lost = extract_file(cd2, "FIELD/LOST2.DAT")
    cos = extract_file(cd2, "FIELD/COS_BTM2.DAT")

    base = bytearray(cd1)
    for a in STACK:
        p = ROOT / f"builder/{a}/layers/disc1.layer.json"
        if p.is_file():
            apply_layer(base, json.loads(p.read_text()))
    base_path = ROOT / "workspace/iso-extract/_tmp029_for_v030.bin"
    work_path = ROOT / "workspace/iso-extract/sd_v030_work.bin"
    base_path.parent.mkdir(parents=True, exist_ok=True)
    base_path.write_bytes(base)

    img = bytearray(base)
    rein(img, "FIELD/BLACKBGB.DAT", bb)
    rein(img, "FIELD/LOST2.DAT", lost)
    rein(img, "FIELD/COS_BTM2.DAT", cos)
    assert extract_file(bytes(img), "FIELD/LOST2.DAT") == lost
    assert extract_file(bytes(img), "FIELD/COS_BTM2.DAT") == cos
    assert extract_file(bytes(img), "FIELD/BLACKBGB.DAT") == bb

    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - len(img) % SECTOR))
    work_path.write_bytes(img)

    pack_dir = ROOT / "builder" / PACK_ID
    (pack_dir / "layers").mkdir(parents=True, exist_ok=True)
    layer = build_layer(
        base_path,
        work_path,
        layer_id=PACK_ID + "-disc1",
        description="v0.1.30: restore v0.1.9 break (Ask BLACKBGB + pure D2 LOST2/COS_BTM2)",
    )
    (pack_dir / "layers/disc1.layer.json").write_text(
        json.dumps(layer, separators=(",", ":")) + "\n"
    )

    pack = {
        "id": PACK_ID,
        "version": "0.1.30",
        "name": "Single-disc break restore (internal)",
        "blurb": "Internal auto: restore v0.1.9 disc-break fields (undo 0.1.27-29).",
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
        "version": "0.1.30",
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
            a["version"] = "0.1.30"
            a["name"] = "Single-disc"
            a["blurb"] = (
                "Play the whole game from one Disc 1 image on CSR. "
                "v0.1.30: restore known-good disc-break fields (v0.1.9 path)."
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
    print("ok", PACK_ID, layer.get("stats"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
