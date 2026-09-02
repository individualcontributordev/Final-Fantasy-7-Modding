#!/usr/bin/env python3
"""Build and register world-encounter ``ic-layer-v1`` add-ons.

For each disc and fixed density, the command reconstructs the chosen clean or
CSR-family base, patches WORLD.BIN, zero-pads it into the existing ISO file
slot, and diffs from that exact parent. It writes stable-id packs under
``builder/`` and updates the local manifest. CSR layers are resolved only from
``--csr-root``/``FF7_CSR_ROOT``; disposable work directories are retained only
with ``--keep-work``."""

from __future__ import annotations

import argparse
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
for p in (_SHARED, _MOD_SCRIPTS):
	if str(p) not in sys.path:
		sys.path.insert(0, str(p))

from libs.layer import apply_layer, build_layer  # noqa: E402
from build_world_bin import build as build_world_stub  # noqa: E402
from density import parse_densities, prompt_densities, rate_label  # noqa: E402
from world_pack_meta import (  # noqa: E402
	AGAINST,
	VERSION_FILE,
	meta_for,
	update_manifest,
	write_pack_json,
)
from psx_mode2_iso import extract_file, find_file, replace_file_padded  # noqa: E402

PRISTINE_DIR = _ROOT / "workspace" / "pristine"
WORK_ROOT = _ROOT / "workspace" / "iso-extract" / "_on_base_world"
WORLD_PATH = "WORLD/WORLD.BIN"


def parse_discs(spec: str) -> list[int]:
	"""Parse a 1,2,3 disc list; each value must be a retail NTSC-U disc number."""
	discs: list[int] = []
	for part in spec.split(","):
		part = part.strip()
		if not part:
			continue
		disc = int(part)
		if disc not in (1, 2, 3):
			raise SystemExit(f"Disc must be 1, 2, or 3 — got {disc}")
		discs.append(disc)
	if not discs:
		raise SystemExit("Pass at least one disc, e.g. --discs 1")
	return discs


def read_default_version() -> str:
	"""Read the mod VERSION file; this is pack metadata, not part of the stable id."""
	if not VERSION_FILE.is_file():
		raise SystemExit(f"Missing {VERSION_FILE} — create it or pass --version")
	version = VERSION_FILE.read_text(encoding="utf-8").strip().splitlines()[0].strip()
	if not re.fullmatch(r"[0-9]+(\.[0-9]+)*", version):
		raise SystemExit(f"Bad version in {VERSION_FILE.name}: {version!r}")
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
	"""Choose the enabled concrete CSR manifest id for a base family."""
	if against == "clean":
		return "clean"
	bases = [b for b in (manifest.get("bases") or []) if b.get("enabled") is not False]
	ids = [str(b.get("id", "")) for b in bases]
	if against == "highwind":
		cands = [i for i in ids if i == "highwind" or i.startswith("highwind-v")]
	elif against == "csr-plus":
		cands = [i for i in ids if i == "csr-plus" or i.startswith("csr-plus-v")]
	elif against == "csr":
		cands = [i for i in ids if i == "csr" or re.fullmatch(r"csr-v[0-9.]+", i)]
	else:
		raise SystemExit(f"Unknown against: {against}")
	if not cands:
		raise SystemExit(f"No enabled base for --against {against}. Saw: {ids}")
	preferred = AGAINST[against]["base_id"]
	if preferred in cands:
		return preferred
	cands.sort()
	return cands[-1]


def resolve_layer_path(
	manifest_path: Path, base_id: str, disc: int, manifest: dict
) -> Path:
	"""Resolve one disc layer from the local CSR manifest."""
	entry = next((b for b in manifest.get("bases") or [] if b.get("id") == base_id), None)
	if not entry:
		raise SystemExit(f"Base id {base_id!r} not found in CSR manifest")
	if entry.get("enabled") is False:
		raise SystemExit(f"Base {base_id} is disabled")
	rel = (entry.get("discs") or {}).get(str(disc))
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
	"""Reconstruct the exact image used as this add-on layer's parent."""
	print(f"=== apply base → {out_bin.name} ===")
	image = bytearray(pristine.read_bytes())
	if layer is not None:
		apply_layer(image, layer)
		print(f"  applied {len(layer.get('records') or [])} records")
	else:
		print("  (clean — no base layer)")
	out_bin.parent.mkdir(parents=True, exist_ok=True)
	out_bin.write_bytes(image)
	print(f"  wrote {out_bin} ({len(image)} bytes)")


def stub_and_inject(base_bin: Path, work_dir: Path, rate: int) -> Path:
	"""Patch WORLD.BIN and inject it into its existing ISO file slot."""
	print(f"=== extract {WORLD_PATH} ===")
	base_bytes = bytearray(base_bin.read_bytes())
	meta = find_file(base_bytes, WORLD_PATH)
	world = extract_file(base_bytes, WORLD_PATH)
	world_path = work_dir / "WORLD.BIN"
	world_path.write_bytes(world)
	print(f"  LBA={meta.lba} size={meta.size} → {world_path}")

	print(f"=== stub WORLD.BIN (rate {rate}%) ===")
	world_new = build_world_stub(
		world_path, work_dir / "WORLD.BIN.new", keep_dec=False, rate=rate
	)
	new_bytes = world_new.read_bytes()
	print(f"  WORLD.BIN.new = {len(new_bytes)} bytes (slot {meta.size})")

	print("=== pad-inject WORLD.BIN.new ===")
	patched = work_dir / "patched.bin"
	shutil.copy2(base_bin, patched)
	img = bytearray(patched.read_bytes())
	replace_file_padded(img, WORLD_PATH, new_bytes)
	patched.write_bytes(img)
	print(f"  wrote {patched}")
	return patched


def build_one(
	*,
	against: str,
	disc: int,
	version: str,
	base_id: str,
	meta: dict,
	pristine_dir: Path,
	manifest_path: Path | None,
	csr_manifest: dict | None,
	base_layer_arg: str | None,
	keep_work: bool,
) -> Path:
	"""Build and round-trip verify one disc layer in disposable work."""
	pack_id = meta["pack_prefix"]
	pristine = pristine_dir / f"FINALFANTASY7_D{disc}.bin"
	if not pristine.is_file():
		raise SystemExit(f"Missing pristine: {pristine}")

	work_dir = WORK_ROOT / f"{against}-r{meta['rate']}-d{disc}"
	# Start from empty generated work so stale extracted overlays cannot become
	# invisible inputs to the byte diff.
	if work_dir.exists():
		shutil.rmtree(work_dir)
	work_dir.mkdir(parents=True)

	layer = None
	if against != "clean":
		if base_layer_arg:
			layer = load_layer(base_layer_arg)
		else:
			assert csr_manifest is not None
			assert manifest_path is not None
			path = resolve_layer_path(manifest_path, base_id, disc, csr_manifest)
			layer = load_layer(path)
		if layer.get("format") != "ic-layer-v1":
			raise SystemExit("base layer must be ic-layer-v1")

	base_bin = work_dir / "base.bin"
	make_base_image(pristine, layer, base_bin)
	patched_bin = stub_and_inject(base_bin, work_dir, meta["rate"])

	print("=== diff → world encounter layer ===")
	out_dir = _ROOT / "builder" / pack_id / "layers"
	out_dir.mkdir(parents=True, exist_ok=True)
	out_path = out_dir / f"disc{disc}.layer.json"
	layer_id = f"{meta['pack_prefix']}-disc{disc}-v{version}"
	description = (
		f"World encounters {meta['rate']}% RCnt2 FORCE stub — NTSC-U Disc {disc} "
		f"(against {base_id})"
	)
	built = build_layer(
		base_bin,
		patched_bin,
		layer_id=layer_id,
		description=description,
	)
	out_path.write_text(json.dumps(built, indent=2) + "\n", encoding="utf-8")
	stats = built["stats"]
	print(
		f"  wrote {out_path.relative_to(_ROOT)}  "
		f"records={stats['records']} changedBytes={stats['changedBytes']}"
	)
	if stats["records"] == 0 or stats["changedBytes"] == 0:
		raise SystemExit("Empty layer — stub/inject produced no disc changes")

	print("=== verify ===")
	check = bytearray(base_bin.read_bytes())
	apply_layer(check, built)
	# The publication boundary is the layer round trip, not merely a successful
	# overlay patch: ISO padding bytes must reconstruct exactly as well.
	if bytes(check) != patched_bin.read_bytes():
		raise SystemExit("VERIFY FAIL — layer apply does not match patched image")
	print("  OK")

	if not keep_work:
		shutil.rmtree(work_dir)
		print(f"  cleaned {work_dir}")

	return out_path


def main() -> int:
	ap = argparse.ArgumentParser(
		description="Build world encounter-on-base layers from local CSR layers + pristine."
	)
	ap.add_argument("--version", default=None, help=f"Version (default: {VERSION_FILE.name})")
	ap.add_argument("--discs", required=True, help="e.g. 1 or 1,2,3")
	ap.add_argument("--against", required=True, choices=sorted(AGAINST.keys()))
	ap.add_argument(
		"--density",
		"--rate",
		dest="density",
		default=None,
		metavar="DENSITY",
		help="light / standard / dense / all. Omit to pick interactively.",
	)
	ap.add_argument("--base-id", default=None, help="Override CSR base id")
	ap.add_argument("--pristine-dir", type=Path, default=PRISTINE_DIR)
	ap.add_argument(
		"--csr-root",
		type=Path,
		help="Final-Fantasy-7-CSR checkout (or set FF7_CSR_ROOT)",
	)
	ap.add_argument("--base-layer", default=None)
	ap.add_argument("--keep-work", action="store_true")
	args = ap.parse_args()

	version = (args.version or read_default_version()).strip()
	if not re.fullmatch(r"[0-9]+(\.[0-9]+)*", version):
		raise SystemExit(f"Weird version '{version}'")

	rates = (
		parse_densities(args.density)
		if args.density is not None
		else prompt_densities(allow_all=True, default="all")
	)
	discs = parse_discs(args.discs)
	if args.base_layer and len(discs) != 1:
		raise SystemExit("--base-layer only works with a single --discs value")

	against = args.against
	csr_manifest = None
	manifest_path = None
	if against == "clean":
		base_id = "clean"
	elif args.base_id:
		base_id = args.base_id.strip()
	else:
		manifest_path = csr_manifest_path(args.csr_root)
		csr_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
		base_id = resolve_base_id(against, csr_manifest)
	if against != "clean" and not args.base_layer and manifest_path is None:
		manifest_path = csr_manifest_path(args.csr_root)
		csr_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

	for rate in rates:
		meta = meta_for(against, rate)
		meta["base_id"] = base_id

		print(f"\n######## {rate_label(rate)} on {against} ########")
		print(f"Base id:  {base_id}")
		print(f"Version:  {version}")
		print(f"Discs:    {discs}")

		for disc in discs:
			print(f"\n######## Disc {disc} ########")
			build_one(
				against=against,
				disc=disc,
				version=version,
				base_id=base_id,
				meta=meta,
				pristine_dir=args.pristine_dir.expanduser().resolve(),
				manifest_path=manifest_path,
				csr_manifest=csr_manifest,
				base_layer_arg=args.base_layer,
				keep_work=args.keep_work,
			)

		# Version is metadata, not identity; keeping it out of the pack id
		# preserves sticky builder selections across releases.
		pack_id = meta["pack_prefix"]
		pack_dir = _ROOT / "builder" / pack_id
		existing: list[int] = []
		layers_dir = pack_dir / "layers"
		if layers_dir.is_dir():
			for p in layers_dir.glob("disc*.layer.json"):
				mid = p.name.removeprefix("disc").removesuffix(".layer.json")
				if mid.isdigit():
					existing.append(int(mid))
		existing = sorted(set(existing))
		if not existing:
			raise SystemExit(f"No disc*.layer.json under {layers_dir}")

		pack = write_pack_json(
			pack_dir,
			pack_id=pack_id,
			version=version,
			display=meta["display"],
			blurb=meta["blurb"],
			compatible_bases=[base_id],
			discs=existing,
			rate=meta["rate"],
			group_label=meta.get("group_label"),
			option_label=meta.get("option_label"),
		)
		update_manifest(pack=pack)
		print(f"\nUpdated {pack_dir / 'pack.json'}")
		print(f"Updated builder/manifest.json")

	print("\nDone. Commit JSON under builder/ only — not .bin/.cue.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
