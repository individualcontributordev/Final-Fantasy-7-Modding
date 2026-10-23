#!/usr/bin/env python3
"""Build and register the New Game+ layer for CSR+ disc 1.

Reconstructs the exact builder parent (pristine + CSR+ base layer), applies the
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

PACK_ID = "new-game-plus-on-csr-plus"
DISC = 1
DISPLAY = "New Game+"
BLURB = (
	"Finishing the game adds a NEW GAME+ title item. It keeps characters, items, "
	"materia and gil, and restarts from the beginning."
)
HINT = "Finish the game, then pick NEW GAME+ on the title screen."
fb.HINT = HINT  # the shared pack/manifest writers read this module global
WORK_ROOT = _ROOT / "workspace" / "iso-extract" / "_new_game_plus"


def main() -> int:
	ap = argparse.ArgumentParser(description="Build the New Game+ builder pack")
	ap.add_argument("--against", default="csr-plus", help="only csr-plus is supported")
	ap.add_argument("--discs", default="1")
	ap.add_argument("--version", default=None)
	ap.add_argument("--csr-root", type=Path)
	ap.add_argument("--keep-work", action="store_true")
	args = ap.parse_args()
	if args.against != "csr-plus" or fb.parse_discs(args.discs) != [DISC]:
		raise SystemExit("New Game+ is built for csr-plus disc 1 only")
	timer = Timer()
	version = args.version or (_MOD / "VERSION").read_text(encoding="utf-8").split()[0]

	manifest_path = fb.csr_manifest_path(args.csr_root)
	csr_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
	base_id = fb.resolve_base_id("csr-plus", csr_manifest)
	entry = next((b for b in csr_manifest["bases"] if str(b.get("id")) == base_id), {})
	base_version = str(entry.get("version") or "").strip()
	if not base_version:
		raise SystemExit(f"CSR manifest has no version for base {base_id!r}")

	pristine = fb.PRISTINE_DIR / f"FINALFANTASY7_D{DISC}.bin"
	if not pristine.is_file():
		raise SystemExit(f"Missing pristine: {pristine}")
	work = WORK_ROOT / f"d{DISC}"
	if work.exists():
		shutil.rmtree(work)
	work.mkdir(parents=True)

	layer = fb.load_layer(fb.resolve_layer_path(manifest_path, base_id, DISC, csr_manifest))
	base_bin = work / "base.bin"
	with timer.stage("apply_base"):
		fb.make_base_image(pristine, layer, base_bin)

	with timer.stage("patch"):
		img = bytearray(base_bin.read_bytes())
		print(f"=== apply New Game+ sites: {apply_patch(img)} bytes ===")
		patched = work / "patched.bin"
		patched.write_bytes(img)
	repaired = work / "patched.repaired.bin"
	with timer.stage("repair"):
		repair(base_bin, patched, repaired)

	out_path = _ROOT / "builder" / PACK_ID / "layers" / f"disc{DISC}.layer.json"
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with timer.stage("diff"):
		built = build_layer(
			base_bin,
			repaired,
			layer_id=f"{PACK_ID}-disc{DISC}-v{version}",
			description=f"New Game+ v{version} -- NTSC-U Disc {DISC} (on {base_id} {base_version})",
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

	meta = dict(
		pack_id=PACK_ID, version=version, base_version=base_version,
		display=DISPLAY, blurb=BLURB, compatible=[base_id], discs=[DISC],
	)
	fb.write_pack_json(_ROOT / "builder" / PACK_ID, **meta)
	fb.update_manifest(**meta)
	print(f"Updated pack + manifest: {PACK_ID}")

	if not args.keep_work:
		shutil.rmtree(work)
	timer.total()
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
