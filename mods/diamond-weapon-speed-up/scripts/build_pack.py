#!/usr/bin/env python3
"""Publish the patched CSR+ Disc 1 as builder pack ``diamond-weapon-speed-up-on-csr-plus``.

Diffs the vanilla CSR+ Disc 1 image against the one ``patch_disc.py`` wrote into an
``ic-layer-v1`` layer, then writes pack.json, VERSION and the manifest add-on entry.

  python build_pack.py base_D1.bin patched_D1.bin --base-version 0.3.8"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))

from libs.layer import apply_layer, build_layer  # noqa: E402

PACK_ID = "diamond-weapon-speed-up-on-csr-plus"
VERSION = "0.2.3"
NAME = "Diamond Weapon Speed Up"
BLURB = "Diamond Weapon reaches Midgar in about 15 seconds instead of about 67."
HINT = "Diamond Weapon marches to Midgar roughly twice as fast."
BASE = "csr-plus"


def main() -> int:
	ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	ap.add_argument("base", type=Path, help="Unpatched CSR+ Disc 1 BIN")
	ap.add_argument("patched", type=Path, help="Output of patch_disc.py")
	ap.add_argument("--base-version", required=True, help="Current csr-plus base version")
	args = ap.parse_args()

	base = args.base.read_bytes()
	layer = build_layer(
		args.base, args.patched, layer_id=f"{PACK_ID}-disc1-v{VERSION}",
		description="Diamond Weapon speed up -- NTSC-U Disc 1 (against csr-plus)",
	)
	check = bytearray(base)
	apply_layer(check, layer)
	if bytes(check) != args.patched.read_bytes():
		raise SystemExit("VERIFY FAIL -- layer apply does not match patched image")

	pack_dir = _ROOT / "builder" / PACK_ID
	(pack_dir / "layers").mkdir(parents=True, exist_ok=True)
	layer_path = pack_dir / "layers" / "disc1.layer.json"
	layer_path.write_text(json.dumps(layer, indent=2) + "\n", encoding="utf-8", newline="\n")
	stats = layer["stats"]
	print(f"records={stats['records']} changedBytes={stats['changedBytes']}")

	entry = {
		"id": PACK_ID, "name": NAME, "kind": "mod", "version": VERSION,
		"blurb": BLURB, "hint": HINT, "format": "ic-layer-v1",
		"compatibleBases": [BASE], "discs": {"1": "./layers/disc1.layer.json"},
		"discDigests": {"1": hashlib.sha256(layer_path.read_bytes()).hexdigest()},
		"baseVersion": args.base_version,
	}
	(pack_dir / "VERSION").write_text(VERSION + "\n", encoding="utf-8", newline="\n")
	(pack_dir / "pack.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8", newline="\n")

	manifest_path = _ROOT / "builder" / "manifest.json"
	manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
	entry["discs"] = {"1": f"./{PACK_ID}/layers/disc1.layer.json"}
	entry["enabled"] = True
	addons = manifest.setdefault("addons", [])
	addons[:] = [a for a in addons if a.get("id") != PACK_ID]
	addons.append(entry)
	manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
	print(f"pack + manifest updated: {PACK_ID}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
