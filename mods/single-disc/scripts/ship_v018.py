#!/usr/bin/env python3
"""Build single-disc-on-csr-v0.1.8: restore CSR D2 LOST2+COS_BTM2 (undo 0.1.6/0.1.7 force)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from disc_sources import csr_root, pristine_bin  # noqa: E402


def main() -> int:
    csr = csr_root()
    base_path = ROOT / "workspace/iso-extract/_csr_d1_baseline_for_sd017.bin"
    work = ROOT / "workspace/iso-extract/sd_v018_lost2_restore.bin"
    if not work.is_file():
        raise SystemExit(f"missing work bin {work}")

    if not base_path.is_file() or base_path.stat().st_size != 747435024:
        print("building CSR baseline...")
        img = bytearray(pristine_bin(1).read_bytes())
        apply_layer(
            img,
            json.loads(
                (csr / "builder/csr-v0.14.1/layers/disc1.layer.json").read_text()
            ),
        )
        base_path.write_bytes(img)
        print("wrote", base_path, len(img))

    pack_id = "single-disc-on-csr-v0.1.8"
    pack_dir = ROOT / "builder" / pack_id
    layer_dir = pack_dir / "layers"
    layer_dir.mkdir(parents=True, exist_ok=True)
    layer_path = layer_dir / "disc1.layer.json"

    print("diffing (slow)...")
    layer = build_layer(
        base_path,
        work,
        layer_id=pack_id + "-disc1",
        description=(
            "Single-disc on CSR v0.1.8 — restore CSR D2 LOST2+COS_BTM2 "
            "(undo forced MAPJUMP/IFUW that black-screened break)"
        ),
    )
    layer_path.write_text(json.dumps(layer, separators=(",", ":")) + "\n")
    print("layer records", len(layer["records"]), "stats", layer.get("stats"))
    print("layer MB", round(layer_path.stat().st_size / 1e6, 2))

    old = json.loads(
        (ROOT / "builder/single-disc-on-csr-v0.1.7/pack.json").read_text()
    )
    pack = {
        **{k: v for k, v in old.items() if k not in ("id", "version", "blurb", "betaNote")},
        "id": pack_id,
        "version": "0.1.8",
        "name": "Single-disc",
        "blurb": (
            "Play the whole game from one Disc 1 image on CSR. "
            "Disc1→2 lands CSR D2 LOST2 (no forced cos_btm2). "
            "Cosmo/post-Hojo fixes included. Endings auto-apply."
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
        "version": "0.1.8",
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
    ids = {a["id"] for a in man["addons"]}
    for a in man["addons"]:
        if a["id"] in (
            "single-disc-on-csr-v0.1.6",
            "single-disc-on-csr-v0.1.7",
        ):
            a["enabled"] = False
    if pack_id in ids:
        man["addons"] = [entry if a["id"] == pack_id else a for a in man["addons"]]
    else:
        idx = next(
            i
            for i, a in enumerate(man["addons"])
            if a["id"] == "single-disc-on-csr-v0.1.7"
        )
        man["addons"].insert(idx + 1, entry)

    prev = "single-disc-on-csr-v0.1.7"
    for a in man["addons"]:
        rule = a.get("autoIncludeWhen")
        if not rule:
            continue
        if rule.get("addonSelected") == prev:
            rule["addonSelected"] = pack_id
        any_list = rule.get("addonSelectedAny")
        if isinstance(any_list, list) and prev in any_list:
            rule["addonSelectedAny"] = [
                pack_id if x == prev else x for x in any_list
            ]
        # also rewrite older ids still pointing at 0.1.6
        if rule.get("addonSelected") == "single-disc-on-csr-v0.1.6":
            rule["addonSelected"] = pack_id
        any_list = rule.get("addonSelectedAny")
        if isinstance(any_list, list) and "single-disc-on-csr-v0.1.6" in any_list:
            rule["addonSelectedAny"] = [
                pack_id if x == "single-disc-on-csr-v0.1.6" else x for x in any_list
            ]

    man_path.write_text(json.dumps(man, indent=2) + "\n")
    (ROOT / "mods/single-disc/VERSION").write_text("0.1.8\n")
    print("manifest + VERSION ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
