#!/usr/bin/env python3
"""Build and register fanfare-skip layers for clean and CSR-family bases.

For each requested disc, the command reconstructs the exact builder parent,
patches BATRES.X, zero-pads it into its existing ISO slot, and diffs the result
into ``ic-layer-v1``. Stable pack ids, pack JSON, and manifest entries are
written under ``builder/``. CSR layers are local-only inputs from
``--csr-root``/``FF7_CSR_ROOT``; generated work is deleted unless retained."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

_MOD_SCRIPTS = Path(__file__).resolve().parent
_MOD = _MOD_SCRIPTS.parent
_ROOT = _MOD.parent.parent
_SHARED = _ROOT / "scripts"
for pth in (_SHARED, _MOD_SCRIPTS):
	if str(pth) not in sys.path:
		sys.path.insert(0, str(pth))

from libs.layer import apply_layer, build_layer  # noqa: E402
from build_batres_x import build as build_batres  # noqa: E402
from psx_mode2_iso import extract_file, find_file, replace_file_padded  # noqa: E402
from repair_mode2_edc import repair  # noqa: E402

PRISTINE_DIR = _ROOT / "workspace" / "pristine"
WORK_ROOT = _ROOT / "workspace" / "iso-extract" / "_fanfare_skip"
MANIFEST_PATH = _ROOT / "builder" / "manifest.json"
VERSION_FILE = _MOD / "VERSION"
BATRES_PATH = "BATTLE/BATRES.X"
HINT = 'No victory fanfare or win poses -- loot and exp still apply.'

AGAINST = {
	"clean": {
		"base_id": "clean",
		"prefix_stem": "fanfare-skip",
		"on_label": "",
		"compatible": ["clean"],
	},
	"csr": {
		"base_id": "csr",
		"prefix_stem": "fanfare-skip-on-csr",
		"on_label": " (on CSR)",
		"compatible": ["csr"],
	},
	"csr-plus": {
		"base_id": "csr-plus",
		"prefix_stem": "fanfare-skip-on-csr-plus",
		"on_label": " (on CSR+)",
		"compatible": ["csr-plus"],
	},
	"highwind": {
		"base_id": "highwind",
		"prefix_stem": "fanfare-skip-on-highwind",
		"on_label": " (on Highwind)",
		"compatible": ["highwind"],
	},
}


def parse_discs(spec: str) -> list[int]:
	"""Parse a 1,2,3 disc list; each value must be a retail NTSC-U disc number."""
	discs: list[int] = []
	for part in spec.split(","):
		part = part.strip()
		if not part:
			continue
		disc = int(part)
		if disc not in (1, 2, 3):
			raise SystemExit(f"Disc must be 1, 2, or 3 -- got {disc}")
		discs.append(disc)
	if not discs:
		raise SystemExit("Pass at least one disc, e.g. --discs 1")
	return discs


def read_version() -> str:
	"""Read the mod VERSION file; this is pack metadata, not part of the stable id."""
	version = VERSION_FILE.read_text(encoding="utf-8").strip().splitlines()[0].strip()
	if not re.fullmatch(r"[0-9]+(\.[0-9]+)*", version):
		raise SystemExit(f"Bad version in VERSION: {version!r}")
	return version


def csr_manifest_path(cli_root: Path | None) -> Path:
	"""Resolve the CSR manifest only from an explicit local repository root."""
	root = cli_root
	if root is None:
		env_root = os.environ.get("FF7_CSR_ROOT")
		root = Path(env_root) if env_root else None
	if root is None:
		raise SystemExit("Pass --csr-root or set FF7_CSR_ROOT")
	path = root.expanduser().resolve() / "builder" / "manifest.json"
	if not path.is_file():
		raise SystemExit(f"Missing CSR manifest: {path}")
	return path


def resolve_base_id(against: str, manifest: dict) -> str:
	"""Choose the concrete enabled id for a requested CSR base family."""
	if against == "clean":
		return "clean"
	bases = [b for b in (manifest.get("bases") or []) if b.get("enabled") is not False]
	ids = [str(b.get("id", "")) for b in bases]
	if against == "highwind":
		cands = [i for i in ids if i == "highwind" or i.startswith("highwind-v")]
	elif against == "csr":
		cands = [i for i in ids if i == "csr" or (i.startswith("csr-v") and "plus" not in i)]
		if not cands:
			cands = [i for i in ids if i.startswith("csr") and "plus" not in i]
	elif against == "csr-plus":
		cands = [i for i in ids if i == "csr-plus" or i.startswith("csr-plus-v")]
	else:
		raise SystemExit(f"unknown against {against}")
	if not cands:
		return AGAINST[against]["base_id"]
	cands.sort()
	return cands[-1]


def resolve_layer_path(
	manifest_path: Path, base_id: str, disc: int, manifest: dict
) -> Path:
	"""Resolve one base layer from the local CSR manifest."""
	bases = manifest.get("bases") or []
	base = next((b for b in bases if str(b.get("id")) == base_id), None)
	if base is None:
		raise SystemExit(f"base {base_id} not in remote manifest")
	discs = base.get("discs") or {}
	rel = discs.get(str(disc)) or discs.get(disc)
	if not rel:
		raise SystemExit(f"{base_id} has no layer for disc {disc}")
	path = (manifest_path.parent / str(rel).lstrip("./")).resolve()
	if not path.is_file():
		raise SystemExit(f"Missing base layer: {path}")
	return path


def load_layer(path: Path | str) -> dict:
	"""Load a local ic-layer-v1 JSON; path is never fetched over the network."""
	path = Path(path).expanduser().resolve()
	if not path.is_file():
		raise SystemExit(f"Missing layer file: {path}")
	print(f"  read {path}")
	return json.loads(path.read_text(encoding="utf-8"))


def make_base_image(pristine: Path, layer: dict | None, out_bin: Path) -> None:
	"""Reconstruct the exact builder-side parent for the add-on diff."""
	print(f"=== apply base -> {out_bin.name} ===")
	image = bytearray(pristine.read_bytes())
	if layer is not None:
		apply_layer(image, layer)
		print(f"  applied {len(layer.get('records') or [])} records")
	else:
		print("  (clean -- no base layer)")
	out_bin.parent.mkdir(parents=True, exist_ok=True)
	out_bin.write_bytes(image)
	print(f"  wrote {out_bin} ({len(image)} bytes)")


def patch_and_inject(
	base_bin: Path,
	work_dir: Path,
) -> Path:
	"""Patch BATRES.X and inject it only if it fits its ISO slot."""
	patched = work_dir / "patched.bin"
	shutil.copy2(base_bin, patched)
	img = bytearray(patched.read_bytes())

	print(f"=== extract {BATRES_PATH} ===")
	meta = find_file(img, BATRES_PATH)
	batres_path = work_dir / "BATRES.X"
	batres_path.write_bytes(extract_file(img, BATRES_PATH))

	print("=== patch BATRES.X ===")
	batres_new = build_batres(
		batres_path, work_dir / "BATRES.X.new", keep_dec=False
	)
	new_bytes = batres_new.read_bytes()
	if len(new_bytes) > meta.size:
		raise SystemExit(
			f"patched BATRES.X ({len(new_bytes)}) larger than slot ({meta.size})"
		)
	replace_file_padded(img, BATRES_PATH, new_bytes)

	patched.write_bytes(img)
	print(f"  wrote {patched}")
	return patched


def disc_digests(pack_dir: Path, discs: list[int]) -> dict[str, str]:
	"""sha256 per published layer file.

	The builder keys its layer cache on these, so republished bytes always
	invalidate even when the version string does not move.
	"""
	digests = {}
	for disc in discs:
		path = pack_dir / "layers" / f"disc{disc}.layer.json"
		digests[str(disc)] = hashlib.sha256(path.read_bytes()).hexdigest()
	return digests


def write_pack_json(
	pack_dir: Path,
	*,
	pack_id: str,
	version: str,
	base_version: str,
	display: str,
	blurb: str,
	compatible: list[str],
	discs: list[int],
) -> None:
	"""Write pack-relative metadata for the built disc layers."""
	pack = {
		"id": pack_id,
		"name": display,
		"kind": "mod",
		"version": version,
		"blurb": blurb,
		"hint": HINT,
		"format": "ic-layer-v1",
		"compatibleBases": compatible,
		"discs": {str(d): f"./layers/disc{d}.layer.json" for d in discs},
		"discDigests": disc_digests(pack_dir, discs),
	}
	# The builder hides a mod whose baseVersion is not the base's current
	# build, because the layer's offsets only fit the build it was cut from.
	if base_version:
		pack["baseVersion"] = base_version
	pack_dir.mkdir(parents=True, exist_ok=True)
	(pack_dir / "VERSION").write_text(version + "\n", encoding="utf-8", newline="\n")
	(pack_dir / "pack.json").write_text(
		json.dumps(pack, indent=2) + "\n", encoding="utf-8", newline="\n"
	)


def update_manifest(
	*,
	pack_id: str,
	version: str,
	base_version: str,
	display: str,
	blurb: str,
	compatible: list[str],
	discs: list[int],
) -> None:
	"""Replace the stable-id manifest entry with manifest-relative paths."""
	entry = {
		"id": pack_id,
		"name": display,
		"kind": "mod",
		"version": version,
		"blurb": blurb,
		"hint": HINT,
		"format": "ic-layer-v1",
		"compatibleBases": compatible,
		"discs": {
			str(d): f"./{pack_id}/layers/disc{d}.layer.json" for d in discs
		},
		"discDigests": disc_digests(_ROOT / "builder" / pack_id, discs),
		"enabled": True,
	}
	if base_version:
		entry["baseVersion"] = base_version
	data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
	addons = data.setdefault("addons", [])
	addons[:] = [a for a in addons if str(a.get("id", "")) != pack_id]
	addons.append(entry)
	MANIFEST_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def build_one(
	*,
	against: str,
	disc: int,
	version: str,
	manifest_path: Path | None,
	csr_manifest: dict | None,
	keep_work: bool,
):
	"""Build and round-trip verify one fanfare layer in disposable work."""
	cfg = dict(AGAINST[against])
	base_id = cfg["base_id"]
	base_version = ""
	if against != "clean" and csr_manifest is not None:
		base_id = resolve_base_id(against, csr_manifest)
		cfg["base_id"] = base_id
		cfg["compatible"] = [base_id]
		entry = next(
			(b for b in csr_manifest.get("bases") or [] if str(b.get("id")) == base_id),
			None,
		)
		base_version = str((entry or {}).get("version") or "").strip()
		if not base_version:
			raise SystemExit(
				f"CSR manifest has no version for base {base_id!r}; the mod would "
				"be published without a baseVersion and the builder would hide it."
			)

	pack_id = cfg["prefix_stem"]
	display = "Fanfare Skip"
	blurb = (
		"After the last enemy dies, skip the victory ceremony path. "
		"Exp, AP, gil, and items still apply; loot/level-up "
		"screens still show."
	)

	pristine = PRISTINE_DIR / f"FINALFANTASY7_D{disc}.bin"
	if not pristine.is_file():
		raise SystemExit(f"Missing pristine: {pristine}")

	work_dir = WORK_ROOT / f"{against}-d{disc}"
	# Recreate generated work to ensure the layer depends only on the selected
	# pristine image, base layer, and tracked BATRES.X patch sites.
	if work_dir.exists():
		shutil.rmtree(work_dir)
	work_dir.mkdir(parents=True)

	layer = None
	if against != "clean":
		assert csr_manifest is not None
		assert manifest_path is not None
		path = resolve_layer_path(manifest_path, base_id, disc, csr_manifest)
		layer = load_layer(path)
		if layer.get("format") != "ic-layer-v1":
			raise SystemExit("base layer must be ic-layer-v1")

	base_bin = work_dir / "base.bin"
	make_base_image(pristine, layer, base_bin)
	patched_bin = patch_and_inject(base_bin, work_dir)
	repaired_bin = work_dir / "patched.repaired.bin"
	print("=== repair MODE2 Form 1 footers ===")
	# Repair against the selected parent, not retail pristine. A base may have
	# unrelated historical footer differences that do not belong in this mod.
	repair(base_bin, patched_bin, repaired_bin)

	print("=== diff -> fanfare-skip layer ===")
	out_dir = _ROOT / "builder" / pack_id / "layers"
	out_dir.mkdir(parents=True, exist_ok=True)
	out_path = out_dir / f"disc{disc}.layer.json"
	layer_id = f"{cfg['prefix_stem']}-disc{disc}-v{version}"
	description = f"Fanfare skip -- NTSC-U Disc {disc} (against {base_id})"
	built = build_layer(
		base_bin,
		repaired_bin,
		layer_id=layer_id,
		description=description,
	)
	out_path.write_text(json.dumps(built, indent=2) + "\n", encoding="utf-8", newline="\n")
	stats = built["stats"]
	print(
		f"  wrote {out_path.relative_to(_ROOT)}  "
		f"records={stats['records']} changedBytes={stats['changedBytes']}"
	)
	if stats["records"] == 0 or stats["changedBytes"] == 0:
		raise SystemExit("Empty layer -- patch/inject produced no disc changes")

	print("=== verify ===")
	check = bytearray(base_bin.read_bytes())
	apply_layer(check, built)
	# Exact reconstruction also covers the zero padding added to BATRES.X's
	# fixed ISO slot, which is part of the published disc-byte layer.
	if bytes(check) != repaired_bin.read_bytes():
		raise SystemExit("VERIFY FAIL -- layer apply does not match patched image")
	print("  OK")

	if not keep_work:
		shutil.rmtree(work_dir)
		print(f"  cleaned {work_dir}")

	return out_path, pack_id, display, blurb, cfg["compatible"], base_id, base_version


def main() -> int:
	ap = argparse.ArgumentParser(description="Build fanfare-skip builder packs")
	ap.add_argument(
		"--against",
		default="clean",
		help="clean | csr | csr-plus | highwind | all",
	)
	ap.add_argument("--discs", default="1,2,3")
	ap.add_argument("--version", default=None)
	ap.add_argument(
		"--csr-root",
		type=Path,
		help="Final-Fantasy-7-CSR checkout (or set FF7_CSR_ROOT)",
	)
	ap.add_argument("--keep-work", action="store_true")
	args = ap.parse_args()

	version = args.version or read_version()
	discs = parse_discs(args.discs)
	against_list = (
		["clean", "csr", "csr-plus", "highwind"]
		if args.against == "all"
		else [args.against]
	)
	for a in against_list:
		if a not in AGAINST:
			raise SystemExit(f"Unknown --against {a}")

	csr_manifest = None
	manifest_path = None
	if any(a != "clean" for a in against_list):
		manifest_path = csr_manifest_path(args.csr_root)
		csr_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

	built: dict[str, dict] = {}
	for against in against_list:
		for disc in discs:
			print(f"\n######## {against} disc {disc} ########")
			_out, pack_id, display, blurb, compatible, base_id, base_version = build_one(
				against=against,
				disc=disc,
				version=version,
				manifest_path=manifest_path,
				csr_manifest=csr_manifest,
				keep_work=args.keep_work,
			)
			rec = built.setdefault(
				pack_id,
				{
					"display": display,
					"blurb": blurb,
					"compatible": compatible,
					"discs": [],
					"version": version,
					"base_version": base_version,
				},
			)
			rec["discs"].append(disc)
			rec["base_version"] = base_version
			if against != "clean":
				rec["compatible"] = [base_id]

	for pack_id, rec in built.items():
		# Pack ids identify builder options and intentionally survive version
		# changes; publication replaces the manifest entry with the same id.
		pack_dir = _ROOT / "builder" / pack_id
		write_pack_json(
			pack_dir,
			pack_id=pack_id,
			version=rec["version"],
			base_version=rec["base_version"],
			display=rec["display"],
			blurb=rec["blurb"],
			compatible=rec["compatible"],
			discs=sorted(set(rec["discs"])),
		)
		update_manifest(
			pack_id=pack_id,
			version=rec["version"],
			base_version=rec["base_version"],
			display=rec["display"],
			blurb=rec["blurb"],
			compatible=rec["compatible"],
			discs=sorted(set(rec["discs"])),
		)
		print(f"Updated pack + manifest: {pack_id}")

	print("\nAll done.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
