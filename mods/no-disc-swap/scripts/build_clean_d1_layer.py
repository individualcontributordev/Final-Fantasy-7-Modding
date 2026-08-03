#!/usr/bin/env python3
"""Diff a combined no-disc-swap work bin against pristine D1 into ic-layer-v1.

Work bin must already include Makou Ask removals + SNOVA inject v3.
Does not commit images. Layer JSON may be large (SNOVA + BATTLE.X).

  python3 mods/no-disc-swap/scripts/build_clean_d1_layer.py \
    --work workspace/iso-extract/ff7_d1_noswap_work.bin \
    --pristine workspace/pristine/FINALFANTASY7_D1.bin
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))

from bin_diff_to_layer import build_layer  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", type=Path, required=True, help="Combined no-disc-swap D1 .bin")
    ap.add_argument("--pristine", type=Path, required=True, help="Pristine D1 .bin")
    ap.add_argument(
        "--version",
        default=None,
        help="Pack version override (default: mods/no-disc-swap/VERSION)",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Override builder pack dir",
    )
    args = ap.parse_args()

    mod = Path(__file__).resolve().parents[1]
    ver = (args.version or (mod / "VERSION").read_text().strip()).lstrip("v")
    pack_id = "no-disc-swap-clean-v%s" % ver
    out_dir = args.out_dir or (_ROOT / "builder" / pack_id)
    layer_path = out_dir / "layers" / "disc1.layer.json"

    if not args.work.is_file():
        raise SystemExit("missing work bin: %s" % args.work)
    if not args.pristine.is_file():
        raise SystemExit("missing pristine: %s" % args.pristine)
    if args.work.stat().st_size < args.pristine.stat().st_size:
        raise SystemExit("work bin smaller than pristine — expected SNOVA growth")

    layer_id = "%s-disc1" % pack_id
    desc = (
        "No-disc-swap Clean D1: Makou Ask-for-disc removal + SNOVA/BATTLE.X LBA v3 "
        "(NTSC-U Disc 1 against clean)"
    )
    print("diff %s vs %s ..." % (args.work, args.pristine))
    layer = build_layer(
        args.pristine,
        args.work,
        layer_id=layer_id,
        description=desc,
    )
    layer_path.parent.mkdir(parents=True, exist_ok=True)
    layer_path.write_text(json.dumps(layer, indent=2) + "\n", encoding="utf-8")
    st = layer["stats"]
    print("wrote %s" % layer_path)
    print(
        "  records=%s changedBytes=%s originalBytes=%s modifiedBytes=%s"
        % (st["records"], st["changedBytes"], st["originalBytes"], st["modifiedBytes"])
    )

    man_path = _ROOT / "builder" / "manifest.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    entry = {
        "id": pack_id,
        "name": "No-disc-swap (Clean D1) v%s" % ver,
        "kind": "mod",
        "blurb": "Disc-1 only: skip Ask-for-disc, Supernova on D1. WIP — console pending.",
        "format": "ic-layer-v1",
        "exclusiveGroup": "no-disc-swap",
        "compatibleBases": ["clean"],
        "discs": {"1": "./%s/layers/disc1.layer.json" % pack_id},
        "enabled": False,
        "groupLabel": "No-disc-swap",
        "optionLabel": "Clean D1 v%s (dev)" % ver,
    }
    addons = man.setdefault("addons", [])
    for i, a in enumerate(addons):
        if a.get("id") == pack_id:
            entry["enabled"] = bool(a.get("enabled"))
            addons[i] = entry
            break
    else:
        addons.append(entry)
    man_path.write_text(json.dumps(man, indent=2) + "\n", encoding="utf-8")
    print("manifest: %s enabled=%s" % (pack_id, entry["enabled"]))
    print("Ship gate: full-run + console before setting enabled true.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
