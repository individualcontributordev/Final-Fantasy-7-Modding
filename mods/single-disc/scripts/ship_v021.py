#!/usr/bin/env python3
"""Build single-disc-on-csr-v0.1.21: D2 NRCRLB into D1 mid53 for MD8_5 (#731).

CSR Highwind path without COTA skip:
  FSHIP_24 (#71) -> FSHIP_12 (#67) ASK leave -> MD8_5 (#731).
MD8_5 dir/0 plays PMVIE mid=53. On D2 that is NRCRLB.MOV; on D1 it is
NIVLSFS.MOV. Wrong stream can hang before SETWORD advances the scene —
looks like "67 -> 731 broken" while MAPJUMP bytes are fine.

Does not touch LOSIN2/LOST2/CANON_2/BLACKBGB/WHITE2/FSHIP FIELD.
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
from psx_mode2_iso import extract_file  # noqa: E402


def main() -> int:
    csr = csr_root()
    prev = ROOT / "builder/single-disc-on-csr-v0.1.20/layers/disc1.layer.json"
    base_path = ROOT / "workspace/iso-extract/_csr_d1_baseline_for_sd021.bin"
    work = ROOT / "workspace/iso-extract/sd_v021_nrcrlb_mid53.bin"

    print("CSR D1 baseline...")
    img = bytearray(pristine_bin(1).read_bytes())
    apply_layer(
        img,
        json.loads((csr / "builder/csr-v0.14.1/layers/disc1.layer.json").read_text()),
    )
    base_path.write_bytes(img)
    print("wrote", base_path, len(img))

    print("apply single-disc 0.1.20...")
    apply_layer(img, json.loads(prev.read_text()))

    d2 = pristine_bin(2).read_bytes()
    print("inject NRCRLB -> D1 mid53 (NIVLSFS slot)...")
    note = inject_one(img, d2, "NRCRLB.MOV", 2, target_d1="NIVLSFS.MOV")
    print(note)

    # Sanity: field MAPJUMPs untouched vs 0.1.20
    img20 = bytearray(base_path.read_bytes())
    apply_layer(img20, json.loads(prev.read_text()))
    for stem in ("FSHIP_12", "FSHIP_24", "MD8_5", "CANON_2", "LOSIN2", "LOST2", "BLACKBGB"):
        a = extract_file(bytes(img20), f"FIELD/{stem}.DAT")
        b = extract_file(bytes(img), f"FIELD/{stem}.DAT")
        if a != b:
            raise SystemExit(f"FIELD changed unexpectedly: {stem}")
    print("FIELD sanity: prefer/path maps unchanged vs 0.1.20")

    work.write_bytes(img)
    print("wrote work", work, len(img))

    pack_id = "single-disc-on-csr-v0.1.21"
    pack_dir = ROOT / "builder" / pack_id
    layer_dir = pack_dir / "layers"
    layer_dir.mkdir(parents=True, exist_ok=True)
    layer_path = layer_dir / "disc1.layer.json"

    print("diffing layer (slow)...")
    layer = build_layer(
        base_path,
        work,
        layer_id=pack_id + "-disc1",
        description=(
            "Single-disc on CSR v0.1.21 — D2 NRCRLB into D1 movie mid53 "
            "(MD8_5 #731 Diamond Weapon approach FMV after FSHIP_12 leave)"
        ),
    )
    layer_path.write_text(json.dumps(layer, separators=(",", ":")) + "\n")
    print("layer records", len(layer["records"]), "stats", layer.get("stats"))

    old = json.loads((ROOT / "builder/single-disc-on-csr-v0.1.20/pack.json").read_text())
    pack = {
        **{k: v for k, v in old.items() if k not in ("id", "version", "blurb", "betaNote")},
        "id": pack_id,
        "version": "0.1.21",
        "name": "Single-disc",
        "blurb": (
            "Play the whole game from one Disc 1 image on CSR. "
            "v0.1.21: NRCRLB FMV on MD8_5 (mid53) so Highwind 71->67->731 works. "
            "Hojo CANON_2 / LOSIN2 break path unchanged."
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
        "version": "0.1.21",
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
        # movies pack still auto on single-disc prefix
        if aid.startswith("single-disc-on-csr") and "autoIncludeWhen" in a:
            pass
    ids = {a["id"] for a in man["addons"]}
    if pack_id in ids:
        man["addons"] = [entry if a.get("id") == pack_id else a for a in man["addons"]]
    else:
        man["addons"].append(entry)
    # Point manip-movies autoInclude at latest single-disc id
    for a in man["addons"]:
        aw = a.get("autoIncludeWhen") or {}
        if aw.get("addonSelected", "").startswith("single-disc-on-csr-v0.1."):
            aw["addonSelected"] = pack_id
            a["autoIncludeWhen"] = aw
    man_path.write_text(json.dumps(man, indent=2) + "\n")
    print("manifest ok", pack_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
