#!/usr/bin/env python3
"""single-disc-on-csr-v0.1.22: MD8_52 NRCRL movie restore + inject.

CSR multi-disc MD8_52 (#779) plays PMVIE mid=52 (D2 NRCRL.MOV) then MAPJUMPs to
FSHIP_25 (#72) — FMV positions Cloud. Single-disc had stripped Set+Play
(movie-trim because D1 mid52 was wrong MTNVL2), so jump ran with no FMV.

Restores CSR MD8_52.DAT (same on CSR D1/D2) and injects D2 NRCRL into D1 mid52.
Keeps 0.1.21 NRCRLB mid53. Does not touch LOSIN2/LOST2/CANON_2/BLACKBGB/WHITE2.
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
from put_field_dat import main as _unused  # noqa: E402 — ensure import path
from psx_mode2_iso import replace_file_padded  # noqa: E402


def main() -> int:
    csr = csr_root()
    prev = ROOT / "builder/single-disc-on-csr-v0.1.21/layers/disc1.layer.json"
    base_path = ROOT / "workspace/iso-extract/_csr_d1_baseline_for_sd022.bin"
    work = ROOT / "workspace/iso-extract/sd_v022_md8_52_nrcrl.bin"

    print("CSR D1 baseline...")
    img = bytearray(pristine_bin(1).read_bytes())
    apply_layer(
        img,
        json.loads((csr / "builder/csr-v0.14.1/layers/disc1.layer.json").read_text()),
    )
    base_path.write_bytes(img)
    print("wrote", base_path, len(img))

    print("apply single-disc 0.1.21...")
    apply_layer(img, json.loads(prev.read_text()))

    csr_d2 = Path.home() / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D2.bin"
    if not csr_d2.is_file():
        csr_d2 = csr / "cache/csr/FINALFANTASY7_D2.bin"
    cd2 = csr_d2.read_bytes()
    csr_md8 = extract_file(cd2, "FIELD/MD8_52.DAT")
    sd_before = extract_file(bytes(img), "FIELD/MD8_52.DAT")
    print("MD8_52 before", len(sd_before), "csr", len(csr_md8), "same", sd_before == csr_md8)

    print("restore CSR MD8_52.DAT...")
    replace_file_padded(img, "FIELD/MD8_52.DAT", csr_md8)
    got = extract_file(bytes(img), "FIELD/MD8_52.DAT")
    if not got.startswith(csr_md8):
        raise SystemExit("MD8_52 put failed")
    print("MD8_52 restored", len(csr_md8))

    d2 = pristine_bin(2).read_bytes()
    print("inject NRCRL -> D1 mid52 (MTNVL2 slot)...")
    note = inject_one(img, d2, "NRCRL.MOV", 2, target_d1="MTNVL2.STR")
    print(note)

    # Keep NRCRLB (mid53) from 0.1.21
    nrcrlb = extract_file(d2, "MOVIE/NRCRLB.MOV")
    slot53 = extract_file(bytes(img), "MOVIE/NIVLSFS.MOV")
    if slot53 != nrcrlb and not slot53.startswith(nrcrlb):
        print("re-inject NRCRLB mid53...")
        print(inject_one(img, d2, "NRCRLB.MOV", 2, target_d1="NIVLSFS.MOV"))

    # Prefer-list / prior fixes unchanged
    img21 = bytearray(base_path.read_bytes())
    apply_layer(img21, json.loads(prev.read_text()))
    for stem in ("FSHIP_12", "FSHIP_24", "MD8_5", "CANON_2", "LOSIN2", "LOST2", "BLACKBGB"):
        a = extract_file(bytes(img21), f"FIELD/{stem}.DAT")
        b = extract_file(bytes(img), f"FIELD/{stem}.DAT")
        if a != b:
            raise SystemExit(f"FIELD changed unexpectedly: {stem}")
    print("FIELD sanity vs 0.1.21: prefer maps unchanged (MD8_52 intentionally restored)")

    work.write_bytes(img)
    print("wrote work", work, len(img))

    pack_id = "single-disc-on-csr-v0.1.22"
    pack_dir = ROOT / "builder" / pack_id
    layer_dir = pack_dir / "layers"
    layer_dir.mkdir(parents=True, exist_ok=True)

    print("diffing layer...")
    layer = build_layer(
        base_path,
        work,
        layer_id=pack_id + "-disc1",
        description=(
            "Single-disc on CSR v0.1.22 — restore MD8_52 Set+Play + D2 NRCRL mid52 "
            "(Cloud-position FMV before FSHIP_25)"
        ),
    )
    (layer_dir / "disc1.layer.json").write_text(
        json.dumps(layer, separators=(",", ":")) + "\n"
    )
    print("layer records", len(layer["records"]), layer.get("stats"))

    old = json.loads((ROOT / "builder/single-disc-on-csr-v0.1.21/pack.json").read_text())
    pack = {
        **{k: v for k, v in old.items() if k not in ("id", "version", "blurb", "betaNote")},
        "id": pack_id,
        "version": "0.1.22",
        "name": "Single-disc",
        "blurb": (
            "Play the whole game from one Disc 1 image on CSR. "
            "v0.1.22: MD8_52 plays NRCRL (Cloud position) then Highwind. "
            "MD8_5 NRCRLB kept. Hojo/break path unchanged."
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
        "version": "0.1.22",
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
    ids = {a["id"] for a in man["addons"]}
    if pack_id in ids:
        man["addons"] = [entry if a.get("id") == pack_id else a for a in man["addons"]]
    else:
        man["addons"].append(entry)
    man_path.write_text(json.dumps(man, indent=2) + "\n")
    print("manifest ok", pack_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
