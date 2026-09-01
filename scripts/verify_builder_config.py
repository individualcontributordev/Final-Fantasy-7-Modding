#!/usr/bin/env python3
"""Reconstruct one local builder selection from a pristine FF7 disc.

Inputs select a disc, base id, optional add-on ids, and optional output BIN.
Local manifests resolve every ``ic-layer-v1`` in builder order; non-clean bases
come only from an explicit ``--csr-root`` or ``FF7_CSR_ROOT``. Compatibility is
checked before add-ons apply. The command performs no network or git access and
does not mutate manifests or source layers."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from apply_layer import apply_layer

ROOT = Path(__file__).resolve().parents[1]


def load_manifest(path: Path) -> tuple[Path, dict]:
	"""Load a local manifest and return its directory for resolving relative layers."""
	path = path.expanduser().resolve()
	if not path.is_file():
		raise SystemExit(f"Missing manifest: {path}")
	return path.parent, json.loads(path.read_text(encoding="utf-8"))


def index_packs(builder_dir: Path, manifest: dict) -> dict[str, tuple[Path, dict]]:
	"""Index base and add-on entries by their published ids."""
	packs: dict[str, tuple[Path, dict]] = {}
	for group in ("bases", "addons"):
		for pack in manifest.get(group) or []:
			pack_id = pack.get("id")
			if pack_id:
				packs[str(pack_id)] = (builder_dir, pack)
	return packs


def layer_path(builder_dir: Path, pack: dict, disc: int) -> Path:
	"""Resolve one pack's disc layer relative to its own manifest directory."""
	relative = (pack.get("discs") or {}).get(str(disc))
	if not relative:
		raise SystemExit(f"{pack.get('id')}: no layer for disc {disc}")
	path = (builder_dir / str(relative).lstrip("./")).resolve()
	if not path.is_file():
		raise SystemExit(f"Missing layer: {path}")
	return path


def apply_pack(image: bytearray, builder_dir: Path, pack: dict, disc: int) -> int:
	"""Apply one validated local pack and return its record count."""
	path = layer_path(builder_dir, pack, disc)
	layer = json.loads(path.read_text(encoding="utf-8"))
	if layer.get("format") != "ic-layer-v1":
		raise SystemExit(f"{path}: expected ic-layer-v1")
	apply_layer(image, layer)
	print(f"  {pack['id']}: {path}")
	return len(layer.get("records") or [])


def csr_root(cli_root: Path | None) -> Path | None:
	"""Resolve the explicit CLI path before the ``FF7_CSR_ROOT`` fallback."""
	if cli_root:
		return cli_root.expanduser().resolve()
	value = os.environ.get("FF7_CSR_ROOT")
	return Path(value).expanduser().resolve() if value else None


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--pristine", type=Path, required=True)
	parser.add_argument("--disc", type=int, choices=(1, 2, 3), required=True)
	parser.add_argument("--base", required=True)
	parser.add_argument("--addon", action="append", default=[])
	parser.add_argument(
		"--csr-root",
		type=Path,
		help="Final-Fantasy-7-CSR checkout (or set FF7_CSR_ROOT)",
	)
	parser.add_argument("-o", "--output", type=Path)
	args = parser.parse_args()

	pristine = args.pristine.expanduser().resolve()
	if not pristine.is_file():
		raise SystemExit(f"Missing pristine image: {pristine}")

	mod_builder, mod_manifest = load_manifest(ROOT / "builder" / "manifest.json")
	packs = index_packs(mod_builder, mod_manifest)

	base_id = args.base.strip()
	if base_id not in {"clean", "unmodified"}:
		csr = csr_root(args.csr_root)
		if csr is None:
			raise SystemExit("Pass --csr-root or set FF7_CSR_ROOT")
		csr_builder, csr_manifest = load_manifest(csr / "builder" / "manifest.json")
		packs.update(index_packs(csr_builder, csr_manifest))

	image = bytearray(pristine.read_bytes())
	record_count = 0
	if base_id not in {"clean", "unmodified"}:
		if base_id not in packs:
			raise SystemExit(f"Unknown base: {base_id}")
		builder_dir, pack = packs[base_id]
		record_count += apply_pack(image, builder_dir, pack, args.disc)

	for addon_id in args.addon:
		if addon_id not in packs:
			raise SystemExit(f"Unknown add-on: {addon_id}")
		builder_dir, pack = packs[addon_id]
		required_base = "clean" if base_id in {"clean", "unmodified"} else base_id
		compatible = pack.get("compatibleBases") or []
		if compatible and required_base not in compatible:
			raise SystemExit(
				f"{addon_id}: compatibleBases={compatible}, base={required_base}"
			)
		record_count += apply_pack(image, builder_dir, pack, args.disc)

	if args.output:
		output = args.output.expanduser().resolve()
		output.parent.mkdir(parents=True, exist_ok=True)
		output.write_bytes(image)
		print(f"Wrote {output}")

	print(f"PASS: {record_count} layer records")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
