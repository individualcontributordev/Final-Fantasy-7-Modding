#!/usr/bin/env python3
"""Build the hidden "Party Recolor + Masamune" fixup packs.

Both mods rewrite ENEMY6/CLOUD.LZS and HICLOUD.LZS, and layers are plain byte overwrites, so selecting
both in the builder leaves a mix of two compressed streams. This pack is the diff from
(base + masamune layer + party-recolor layer, as the site applies them) to (base with both patches
run), so it only holds the rewritten Cloud sectors. The site adds it automatically
(``autoIncludeWhen``) when both mods are selected, and its id sorts after both so it applies last.
Rebuild it whenever either of those packs is rebuilt."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "mods" / "party-recolor" / "scripts"))
sys.path.insert(0, str(_HERE))

import build_on_base as mb  # noqa: E402  (masamune; also loads the fanfare-skip writers as mb.fb)
import apply_masamune  # noqa: E402
import apply_party_recolor  # noqa: E402
from libs.layer import apply_layer, build_layer  # noqa: E402
from repair_mode2_edc import repair  # noqa: E402
from psx_mode2_iso import walk_tree  # noqa: E402

fb = mb.fb
RECOLOR_IDS = {"clean": "party-recolor", "csr": "party-recolor-on-csr",
	"csr-plus": "party-recolor-on-csr-plus", "highwind": "party-recolor-on-highwind"}
FIXUP_IDS = {k: v.replace("party-recolor", "party-recolor-with-masamune", 1) for k, v in RECOLOR_IDS.items()}
WORK_ROOT = _ROOT / "workspace" / "iso-extract" / "_masamune_recolor"
FILES = ("/ENEMY6/CLOUD.LZS", "/ENEMY6/HICLOUD.LZS", "/INIT/KERNEL.BIN")  # KERNEL: older clean masamune layer holds different (equivalent) gzip bytes


def layer_of(pack_id, disc):
	return fb.load_layer(_ROOT / "builder" / pack_id / "layers" / f"disc{disc}.layer.json")


def build_disc(against, disc, version, csr_manifest, manifest_path, timer):
	pack_id = FIXUP_IDS[against]
	base_id, base_version, layer = "clean", "", None
	if against != "clean":
		base_id = fb.resolve_base_id(against, csr_manifest)
		base_version = str(next(b for b in csr_manifest["bases"] if str(b.get("id")) == base_id).get("version") or "")
		layer = fb.load_layer(fb.resolve_layer_path(manifest_path, base_id, disc, csr_manifest))
	work = WORK_ROOT / f"{against}-d{disc}"
	if work.exists():
		shutil.rmtree(work, ignore_errors=True)
	work.mkdir(parents=True)
	base_bin = work / "base.bin"
	fb.make_base_image(fb.PRISTINE_DIR / f"FINALFANTASY7_D{disc}.bin", layer, base_bin)

	parent = bytearray(base_bin.read_bytes())  # what the site has before the fixup
	for pid in (mb.PACK_IDS[against], RECOLOR_IDS[against]):
		apply_layer(parent, layer_of(pid, disc))
	(work / "parent.bin").write_bytes(parent)

	img = bytearray(base_bin.read_bytes())  # both patches run on the same image
	apply_masamune.apply_patch(img)
	apply_party_recolor.apply_patch(img)
	(work / "patched.bin").write_bytes(img)
	repaired = work / "patched.repaired.bin"
	repair(base_bin, work / "patched.bin", repaired)

	built = build_layer(
		work / "parent.bin", repaired,
		layer_id=f"{pack_id}-disc{disc}-v{version}",
		description=f"Party Recolor + Masamune v{version} -- NTSC-U Disc {disc} (on {base_id} {base_version})".replace(" )", ")"),
	)
	if not built["stats"]["changedBytes"]:
		raise SystemExit("Empty fixup layer")
	# Only these files may differ from what the site would have produced.
	tree = walk_tree(parent)
	spans = [(tree[p].lba * 2352, (tree[p].lba + -(-tree[p].size // 2048)) * 2352) for p in FILES]
	bad = [r["offset"] for r in built["records"] if not any(a <= r["offset"] < b for a, b in spans)]
	if bad:
		raise SystemExit(f"fixup touches bytes outside the Cloud models: {bad[:5]}")
	out = _ROOT / "builder" / pack_id / "layers" / f"disc{disc}.layer.json"
	out.parent.mkdir(parents=True, exist_ok=True)
	out.write_text(json.dumps(built, indent=2) + "\n", encoding="utf-8", newline="\n")
	check = bytearray(parent)
	apply_layer(check, built)
	if bytes(check) != repaired.read_bytes():
		raise SystemExit("VERIFY FAIL -- fixup does not reproduce the combined image")
	print(f"  {pack_id} d{disc}: records={built['stats']['records']} changedBytes={built['stats']['changedBytes']} verify OK")
	shutil.rmtree(work, ignore_errors=True)
	return base_id, base_version


def main() -> int:
	ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	ap.add_argument("--against", required=True, choices=sorted(FIXUP_IDS))
	ap.add_argument("--csr-root", type=Path)
	args = ap.parse_args()
	against = args.against
	discs = [1] if against in mb.ONE_DISC else [1, 2, 3]
	version = (mb._MOD / "VERSION").read_text(encoding="utf-8").split()[0]
	manifest_path = csr_manifest = None
	if against != "clean":
		manifest_path = fb.csr_manifest_path(args.csr_root)
		csr_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
	timer = None
	for disc in discs:
		base_id, base_version = build_disc(against, disc, version, csr_manifest, manifest_path, timer)

	pack_id = FIXUP_IDS[against]
	meta = dict(pack_id=pack_id, version=version, base_version=base_version,
		display="Party Recolor + Masamune", blurb="Merges Party Recolor with the Masamune mod.",
		compatible=[base_id], discs=discs)
	fb.write_pack_json(_ROOT / "builder" / pack_id, **meta)
	fb.update_manifest(**meta)
	extra = {"hidden": True, "autoIncludeWhen": {"bases": [base_id], "addonSelected": mb.PACK_IDS[against],
		"addonSelectedAny": [RECOLOR_IDS[against]]}}
	pj = _ROOT / "builder" / pack_id / "pack.json"
	for path in (pj, _ROOT / "builder" / "manifest.json"):
		data = json.loads(path.read_text(encoding="utf-8"))
		tgt = data if path == pj else next(a for a in data["addons"] if a["id"] == pack_id)
		tgt.update(extra)
		path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
	print(f"Updated pack + manifest: {pack_id}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
