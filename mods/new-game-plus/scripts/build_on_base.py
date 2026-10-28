#!/usr/bin/env python3
"""Build and register the New Game+ layers (CSR+ and Highwind disc 1; CSR and clean discs 1-3).

Reconstructs the exact builder parent (pristine, plus the CSR+ base layer for csr-plus), applies the
fixed-site patch from ``apply_new_game_plus.py``, repairs footers against that
parent, and diffs the result into ``ic-layer-v1``. Pack JSON and the manifest
entry reuse the fanfare-skip writers. Same CLI shape as the other
``build_on_base.py`` scripts so ``rebuild_on_base.py`` can drive it."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_MOD = _HERE.parent
_ROOT = _MOD.parent.parent
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_HERE))

from libs.layer import apply_layer, build_layer  # noqa: E402
from libs.timing import Timer  # noqa: E402
from repair_mode2_edc import repair  # noqa: E402
from apply_new_game_plus import apply_patch  # noqa: E402

_spec = importlib.util.spec_from_file_location(
	"fanfare_build_on_base", _ROOT / "mods" / "fanfare-skip" / "scripts" / "build_on_base.py"
)
fb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fb)

PACK_IDS = {"csr-plus": "new-game-plus-on-csr-plus", "csr": "new-game-plus-on-csr",
	"highwind": "new-game-plus-on-highwind", "clean": "new-game-plus"}
ONE_DISC = ("csr-plus", "highwind")  # bases that only ship disc 1
DISPLAY = "New Game+"
BLURB = (
	"Finishing the game adds a NEW GAME+ title item. It keeps characters, items, "
	"materia and gil, and restarts from the beginning."
)
HINT = "Finish the game, then pick NEW GAME+ on the title screen."
fb.HINT = HINT  # the shared pack/manifest writers read this module global
WORK_ROOT = _ROOT / "workspace" / "iso-extract" / "_new_game_plus"


def build_disc(against, disc, version, csr_manifest, manifest_path, keep_work, timer):
	pack_id = PACK_IDS[against]
	clean = against == "clean"
	base_id, base_version, layer = "clean", "", None
	if not clean:
		base_id = fb.resolve_base_id(against, csr_manifest)
		entry = next((b for b in csr_manifest["bases"] if str(b.get("id")) == base_id), {})
		base_version = str(entry.get("version") or "").strip()
		if not base_version:
			raise SystemExit(f"CSR manifest has no version for base {base_id!r}")
		layer = fb.load_layer(fb.resolve_layer_path(manifest_path, base_id, disc, csr_manifest))

	pristine = fb.PRISTINE_DIR / f"FINALFANTASY7_D{disc}.bin"
	if not pristine.is_file():
		raise SystemExit(f"Missing pristine: {pristine}")
	work = WORK_ROOT / f"{against}-d{disc}"
	if work.exists():
		shutil.rmtree(work)
	work.mkdir(parents=True)

	base_bin = work / "base.bin"
	with timer.stage("apply_base"):
		fb.make_base_image(pristine, layer, base_bin)

	with timer.stage("patch"):
		img = bytearray(base_bin.read_bytes())
		# MOVIE_ID.BIN: CSR+ disc 1 only; retail disc 3 already holds those bytes.
		patched_bytes = apply_patch(img, movie_row=against == "csr-plus")
		print(f"=== apply New Game+ sites ({against} d{disc}): {patched_bytes} bytes ===")
		patched = work / "patched.bin"
		patched.write_bytes(img)
	repaired = work / "patched.repaired.bin"
	with timer.stage("repair"):
		repair(base_bin, patched, repaired)

	out_path = _ROOT / "builder" / pack_id / "layers" / f"disc{disc}.layer.json"
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with timer.stage("diff"):
		built = build_layer(
			base_bin,
			repaired,
			layer_id=f"{pack_id}-disc{disc}-v{version}",
			description=f"New Game+ v{version} -- NTSC-U Disc {disc} (on {base_id} {base_version})".replace(" )", ")"),
		)
	stats = built["stats"]
	if not stats["changedBytes"]:
		raise SystemExit(
			"Empty layer -- the base already contains New Game+ (or the patch did nothing); "
			"nothing written"
		)
	out_path.write_text(json.dumps(built, indent=2) + "\n", encoding="utf-8", newline="\n")
	print(f"  wrote {out_path.relative_to(_ROOT)}  records={stats['records']} changedBytes={stats['changedBytes']}")

	with timer.stage("verify"):
		check = bytearray(base_bin.read_bytes())
		apply_layer(check, built)
		if bytes(check) != repaired.read_bytes():
			raise SystemExit("VERIFY FAIL -- layer apply does not match patched image")
	print("  verify OK")
	if not keep_work:
		shutil.rmtree(work)
	return pack_id, base_id, base_version


def main() -> int:
	ap = argparse.ArgumentParser(description="Build the New Game+ builder pack")
	ap.add_argument("--against", default="csr-plus", help="csr-plus | csr | highwind | clean")
	ap.add_argument("--discs", default=None, help="default: 1 for csr-plus, 1,2,3 otherwise")
	ap.add_argument("--version", default=None)
	ap.add_argument("--csr-root", type=Path)
	ap.add_argument("--keep-work", action="store_true")
	args = ap.parse_args()
	if args.against not in PACK_IDS:
		raise SystemExit("New Game+ is built for csr-plus, csr, highwind or clean only")
	clean = args.against == "clean"
	discs = fb.parse_discs(args.discs or ("1" if args.against in ONE_DISC else "1,2,3"))
	if args.against in ONE_DISC and discs != [1]:
		raise SystemExit(f"New Game+ on {args.against} is disc 1 only")
	timer = Timer()
	version = args.version or (_MOD / "VERSION").read_text(encoding="utf-8").split()[0]

	manifest_path = csr_manifest = None
	if not clean:
		manifest_path = fb.csr_manifest_path(args.csr_root)
		csr_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

	for disc in discs:
		pack_id, base_id, base_version = build_disc(
			args.against, disc, version, csr_manifest, manifest_path, args.keep_work, timer
		)
	meta = dict(
		pack_id=pack_id, version=version, base_version=base_version,
		display=DISPLAY, blurb=BLURB, compatible=[base_id], discs=discs,
	)
	fb.write_pack_json(_ROOT / "builder" / pack_id, **meta)
	fb.update_manifest(**meta)
	print(f"Updated pack + manifest: {pack_id}")
	timer.total()
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
