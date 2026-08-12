#!/usr/bin/env python3
"""single-disc-on-csr-v0.1.23: FSHIP_12 PARASHOT (+ meteo pair) restore.

User: CSR D2 plays PARASHOT positioning Cloud; CSR+single-disc cut/broken.

CSR FSHIP_12 (#67) ad/3: PMVIE 59 PARASHOT, 50 METEOFIX, 51 METEOSKY then
MAPJUMP blin70_4. Single-disc stripped those Plays (movie trim).

Restore CSR FSHIP_12.DAT + inject D2 streams into D1 mids 59/50/51.
Keeps MD8_5 NRCRLB (0.1.21) and MD8_52 NRCRL (0.1.22).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mods/single-disc/scripts"))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from disc_sources import csr_root, pristine_bin  # noqa: E402
from inject_movies_by_disc_id import inject_one  # noqa: E402
from psx_mode2_iso import extract_file, replace_file_padded  # noqa: E402


def main() -> int:
    csr = csr_root()
    prev = ROOT / "builder/single-disc-on-csr-v0.1.22/layers/disc1.layer.json"
    base_path = ROOT / "workspace/iso-extract/_csr_d1_baseline_for_sd023.bin"
    work = ROOT / "workspace/iso-extract/sd_v023_fship12_parashot.bin"

    print("CSR D1 baseline...")
    img = bytearray(pristine_bin(1).read_bytes())
    apply_layer(
        img,
        json.loads((csr / "builder/csr-v0.14.1/layers/disc1.layer.json").read_text()),
    )
    base_path.write_bytes(img)

    print("apply single-disc 0.1.22...")
    apply_layer(img, json.loads(prev.read_text()))

    csr_d2 = Path.home() / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D2.bin"
    if not csr_d2.is_file():
        csr_d2 = csr / "cache/csr/FINALFANTASY7_D2.bin"
    cd2 = csr_d2.read_bytes()
    csr_f12 = extract_file(cd2, "FIELD/FSHIP_12.DAT")
    before = extract_file(bytes(img), "FIELD/FSHIP_12.DAT")
    print("FSHIP_12 before==CSR?", before == csr_f12, len(before), len(csr_f12))

    print("restore CSR FSHIP_12.DAT...")
    replace_file_padded(img, "FIELD/FSHIP_12.DAT", csr_f12)
    if not extract_file(bytes(img), "FIELD/FSHIP_12.DAT").startswith(csr_f12):
        raise SystemExit("FSHIP_12 put failed")

    d2 = pristine_bin(2).read_bytes()
    # Same ad/3 sequence on CSR: 59, 50, 51
    injects = [
        ("PARASHOT.MOV", "OPENINGE.MOV"),
        ("METEOFIX.MOV", "MTCRL.STR"),
        ("METEOSKY.MOV", "MTNVL.STR"),
    ]
    for src, dst in injects:
        print("inject", src, "->", dst)
        print(inject_one(img, d2, src, 2, target_d1=dst))

    # Sanity: prior path fields unchanged except FSHIP_12
    img22 = bytearray(base_path.read_bytes())
    apply_layer(img22, json.loads(prev.read_text()))
    for stem in ("MD8_52", "MD8_5", "CANON_2", "LOSIN2", "LOST2", "BLACKBGB", "FSHIP_24"):
        a = extract_file(bytes(img22), f"FIELD/{stem}.DAT")
        b = extract_file(bytes(img), f"FIELD/{stem}.DAT")
        if a != b:
            raise SystemExit(f"FIELD changed unexpectedly: {stem}")
    print("FIELD sanity: MD8_*/prefer/FSHIP_24 unchanged vs 0.1.22")

    # payloads
    for src, dst in injects:
        s = extract_file(d2, "MOVIE/" + src)
        g = extract_file(bytes(img), "MOVIE/" + dst)
        if g != s and not g.startswith(s):
            raise SystemExit(f"payload mismatch {src} -> {dst}")
    print("movie payloads OK")

    work.write_bytes(img)
    print("wrote", work, len(img))

    pack_id = "single-disc-on-csr-v0.1.23"
    pack_dir = ROOT / "builder" / pack_id
    layer_dir = pack_dir / "layers"
    layer_dir.mkdir(parents=True, exist_ok=True)

    print("diffing...")
    layer = build_layer(
        base_path,
        work,
        layer_id=pack_id + "-disc1",
        description=(
            "Single-disc on CSR v0.1.23 — restore FSHIP_12 Set+Play + "
            "PARASHOT/METEOFIX/METEOSKY (Cloud-position Highwind deck FMV)"
        ),
    )
    (layer_dir / "disc1.layer.json").write_text(
        json.dumps(layer, separators=(",", ":")) + "\n"
    )
    print("records", len(layer["records"]), layer.get("stats"))

    old = json.loads((ROOT / "builder/single-disc-on-csr-v0.1.22/pack.json").read_text())
    pack = {
        **{k: v for k, v in old.items() if k not in ("id", "version", "blurb", "betaNote")},
        "id": pack_id,
        "version": "0.1.23",
        "name": "Single-disc",
        "blurb": (
            "Play the whole game from one Disc 1 image on CSR. "
            "v0.1.23: FSHIP_12 plays PARASHOT (+ meteo) like CSR D2. "
            "MD8_52 NRCRL / MD8_5 NRCRLB kept. Hojo/break unchanged."
        ),
        "hint": "Use one Disc 1 image for the full CSR game.",
        "beta": True,
        "status": "beta",
        "betaNote": (
            "Single-disc is still playtesting; known freezes and glitches on some paths."
        ),
        "discs": {"1": "./layers/disc1.layer.json"},
    }
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2) + "\n")

    man_path = ROOT / "builder/manifest.json"
    man = json.loads(man_path.read_text())
    entry = {
        "id": pack_id,
        "name": "Single-disc",
        "kind": "mod",
        "version": "0.1.23",
        "blurb": pack["blurb"],
        "hint": pack["hint"],
        "format": "ic-layer-v1",
        "compatibleBases": ["csr-v0.14.1"],
        "layout": "global",
        "discs": {"1": "./" + pack_id + "/layers/disc1.layer.json"},
        "enabled": True,
        "beta": True,
        "status": "beta",
        "betaNote": pack["betaNote"],
    }
    for a in man["addons"]:
        aid = a.get("id", "")
        if aid.startswith("single-disc-on-csr-v0.1.") and aid != pack_id:
            a["enabled"] = False
        aw = a.get("autoIncludeWhen") or {}
        if aw.get("addonSelected", "").startswith("single-disc-on-csr-v0.1."):
            aw["addonSelected"] = pack_id
            a["autoIncludeWhen"] = aw
    if any(a.get("id") == pack_id for a in man["addons"]):
        man["addons"] = [entry if a.get("id") == pack_id else a for a in man["addons"]]
    else:
        man["addons"].append(entry)
    man_path.write_text(json.dumps(man, indent=2) + "\n")
    print("manifest ok", pack_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
