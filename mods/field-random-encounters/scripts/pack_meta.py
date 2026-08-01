#!/usr/bin/env python3
"""Helpers + optional CLI for Field encounter ic-layer-v1 packs.

  python mods/field-random-encounters/scripts/build_all_rates.py
  python mods/field-random-encounters/scripts/build_on_base.py --against csr-plus --discs 1
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_MOD_SCRIPTS = Path(__file__).resolve().parent
_MOD = _MOD_SCRIPTS.parent
_ROOT = _MOD.parent.parent  # mods/<name> → repo root
_SHARED = _ROOT / "scripts"
# Prefer this mod's scripts over deprecated repo-root shims with the same names.
for p in (_SHARED, _MOD_SCRIPTS):
	if str(p) not in sys.path:
		sys.path.insert(0, str(p))


from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from density import RATES, parse_one_density, prompt_densities, rate_label  # noqa: E402

PRISTINE_DIR = _ROOT / "workspace" / "pristine"
ISO = _ROOT / "workspace" / "iso-extract"
MANIFEST_PATH = _ROOT / "builder" / "manifest.json"
VERSION_FILE = _MOD / "VERSION"
EXCLUSIVE_GROUP = "field-encounter-rate"

AGAINST = {
	"clean": {
		"base_id": "clean",
		"prefix_stem": "field-encounter",
		"on_label": "",
	},
	"csr": {
		"base_id": "csr-v0.14.1",
		"prefix_stem": "field-encounter-on-csr",
		"on_label": " (on CSR)",
	},
	"csr-plus": {
		"base_id": "csr-plus-v0.1.1",
		"prefix_stem": "field-encounter-on-csr-plus",
		"on_label": " (on CSR+)",
	},
	"highwind": {
		"base_id": "highwind-v0.1.1",
		"prefix_stem": "field-encounter-on-highwind",
		"on_label": " (on Highwind)",
	},
}

RATE_LABEL = {
	0: "Off",
	25: "Light",
	50: "Standard",
	75: "Dense",
}

RATE_BLURB = {
	0: "No random field battles.",
	25: "Fewer random field battles.",
	50: "Moderate random field battles.",
	75: "More random field battles.",
}


def meta_for(against: str, rate: int) -> dict:
	if against not in AGAINST:
		raise SystemExit(f"Unknown against: {against}")
	if rate not in RATES:
		raise SystemExit(f"rate must be one of {RATES}, got {rate}")
	base = AGAINST[against]
	on = base["on_label"]
	pack_prefix = f"{base['prefix_stem']}-{rate}"
	label = RATE_LABEL[rate]
	return {
		"base_id": base["base_id"],
		"pack_prefix": pack_prefix,
		"display": f"Field Random Encounters — {label} ({rate}%){on}",
		"group_label": "Field Random Encounters",
		"option_label": f"{label} ({rate}%)",
		"blurb": RATE_BLURB[rate],
		"rate": rate,
		"against": against,
	}


def parse_discs(spec: str | None, base_bin_fn, working_bin_fn) -> list[int]:
	if spec:
		discs = []
		for part in spec.split(","):
			part = part.strip()
			if not part:
				continue
			disc = int(part)
			if disc not in (1, 2, 3):
				raise SystemExit(f"Disc must be 1, 2, or 3 — got {disc}")
			discs.append(disc)
		return discs
	found = [
		d
		for d in (1, 2, 3)
		if base_bin_fn(d).is_file() and working_bin_fn(d).is_file()
	]
	if not found:
		raise SystemExit(
			"No disc pairs found (base + iso-extract working image).\n"
			"Prefer: python mods/field-random-encounters/scripts/build_on_base.py …"
		)
	return found


def verify(base: Path, layer_path: Path, patched: Path) -> None:
	image = bytearray(base.read_bytes())
	layer = json.loads(layer_path.read_text(encoding="utf-8"))
	apply_layer(image, layer)
	expect = patched.read_bytes()
	if bytes(image) != expect:
		lim = min(len(image), len(expect))
		for i in range(lim):
			if image[i] != expect[i]:
				raise SystemExit(f"VERIFY FAIL at offset {i} (0x{i:X}) for {layer_path.name}")
		raise SystemExit(
			f"VERIFY FAIL size {len(image)} vs {len(expect)} for {layer_path.name}"
		)


def write_pack_json(
	pack_dir: Path,
	*,
	pack_id: str,
	version: str,
	display: str,
	blurb: str,
	compatible_bases: list[str],
	discs: list[int],
	rate: int | None = None,
	group_label: str | None = None,
	option_label: str | None = None,
) -> None:
	pack = {
		"id": pack_id,
		"name": display,
		"kind": "mod",
		"version": version,
		"blurb": blurb,
		"format": "ic-layer-v1",
		"exclusiveGroup": EXCLUSIVE_GROUP,
		"compatibleBases": compatible_bases,
		"discs": {str(d): f"./layers/disc{d}.layer.json" for d in discs},
	}
	if rate is not None:
		pack["rate"] = rate
	if group_label:
		pack["groupLabel"] = group_label
	if option_label:
		pack["optionLabel"] = option_label
	pack_dir.mkdir(parents=True, exist_ok=True)
	(pack_dir / "pack.json").write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")


def update_manifest(
	*,
	pack_id: str,
	pack_prefix: str,
	version: str,
	display: str,
	blurb: str,
	compatible_bases: list[str],
	discs: list[int],
	rate: int | None = None,
	group_label: str | None = None,
	option_label: str | None = None,
) -> None:
	if not MANIFEST_PATH.is_file():
		raise SystemExit(f"Missing {MANIFEST_PATH}")
	data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
	entry = {
		"id": pack_id,
		"name": f"{display} v{version}",
		"kind": "mod",
		"blurb": blurb,
		"format": "ic-layer-v1",
		"exclusiveGroup": EXCLUSIVE_GROUP,
		"compatibleBases": compatible_bases,
		"discs": {
			str(d): f"./{pack_id}/layers/disc{d}.layer.json" for d in discs
		},
		"enabled": True,
	}
	if rate is not None:
		entry["rate"] = rate
	if group_label:
		entry["groupLabel"] = group_label
	if option_label:
		entry["optionLabel"] = option_label

	addons = data.setdefault("addons", [])
	# Drop legacy encounter-* ids when writing the new field-encounter pack
	legacy_id = pack_id.removeprefix("field-")
	addons[:] = [
		a
		for a in addons
		if str(a.get("id", "")) not in (pack_id, legacy_id)
	]
	addons.append(entry)

	MANIFEST_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def resolve_base_bin(disc: int, against: str, base_dir: Path | None) -> Path:
	if against == "clean":
		return PRISTINE_DIR / f"FINALFANTASY7_D{disc}.bin"

	if base_dir is None:
		raise SystemExit(
			f"--against {against} requires --base-dir "
			"(CSR repo folder with FINALFANTASY7_DN.bin)."
		)
	base_dir = base_dir.expanduser().resolve()
	plain = base_dir / f"FINALFANTASY7_D{disc}.bin"
	legacy = base_dir / f"FINALFANTASY7_D{disc} (patched).bin"
	if plain.is_file():
		return plain
	if legacy.is_file():
		return legacy
	raise SystemExit(f"Missing base image for disc {disc} under {base_dir}")


def working_bin(disc: int) -> Path:
	return ISO / f"FINALFANTASY7_D{disc}.bin"


def build_one_disc(
	*,
	version: str,
	disc: int,
	against: str,
	meta: dict,
	base_dir: Path | None,
	skip_verify: bool,
) -> Path:
	base = resolve_base_bin(disc, against, base_dir)
	patched = working_bin(disc)
	if not base.is_file():
		raise SystemExit(f"Missing stack-base image: {base}")
	if not patched.is_file():
		raise SystemExit(
			f"Missing working image: {patched}\n"
			"Prefer build_on_base.py, or stub + import into iso-extract."
		)
	if base.resolve() == patched.resolve():
		raise SystemExit("Base and working paths are the same file — check layout.")

	pack_id = f"{meta['pack_prefix']}-v{version}"
	out_dir = _ROOT / "builder" / pack_id / "layers"
	out_dir.mkdir(parents=True, exist_ok=True)
	out_path = out_dir / f"disc{disc}.layer.json"

	layer_id = f"{meta['pack_prefix']}-disc{disc}-v{version}"
	description = (
		f"Field encounters {meta['rate']}% RCnt2 FORCE stub — NTSC-U Disc {disc} "
		f"(against {meta['base_id']})"
	)
	print(f"\n=== Disc {disc}: diff ===")
	print(f"  base:    {base}")
	print(f"  working: {patched}")
	layer = build_layer(
		base,
		patched,
		layer_id=layer_id,
		description=description,
	)
	out_path.write_text(json.dumps(layer, indent=2) + "\n", encoding="utf-8")
	stats = layer["stats"]
	print(
		f"  wrote {out_path.relative_to(_ROOT)}  "
		f"records={stats['records']} changedBytes={stats['changedBytes']}"
	)
	if stats["records"] == 0 or stats["changedBytes"] == 0:
		raise SystemExit(
			f"Disc {disc}: base and working images are identical.\n"
			"Stub never landed, or you re-prepared over the working copy."
		)

	if not skip_verify:
		print(f"=== Disc {disc}: verify ===")
		verify(base, out_path, patched)
		print("  OK — layer apply matches working image")

	return out_path


def main() -> int:
	ap = argparse.ArgumentParser(
		description="Build Field encounter layers for the browser builder (manual path)."
	)
	ap.add_argument("--version", required=True, help="Version string, e.g. 0.1.2")
	ap.add_argument(
		"--discs",
		default=None,
		help="Comma list (default: all pairs that exist). Example: 1,2,3",
	)
	ap.add_argument(
		"--against",
		default="clean",
		choices=sorted(AGAINST.keys()),
		help="Which builder base this Field encounter layer stacks on",
	)
	ap.add_argument(
		"--density",
		"--rate",
		dest="density",
		default=None,
		metavar="PRESET",
		help="light / standard / dense (or 25 / 50 / 75). Omit to pick interactively.",
	)
	ap.add_argument(
		"--base-dir",
		default=None,
		help="CSR workspace folder with FINALFANTASY7_DN.bin (required unless --against clean)",
	)
	ap.add_argument(
		"--skip-verify",
		action="store_true",
		help="Skip apply_layer checks (not recommended)",
	)
	args = ap.parse_args()

	version = args.version.strip()
	if not re.fullmatch(r"[0-9]+(\.[0-9]+)*", version):
		raise SystemExit(f"Weird version '{version}' — expected like 0.1.0")

	against = args.against
	rate = (
		parse_one_density(args.density)
		if args.density is not None
		else prompt_densities(allow_all=False)[0]
	)
	meta = meta_for(against, rate)
	base_dir = Path(args.base_dir) if args.base_dir else None
	if against != "clean" and base_dir is None:
		raise SystemExit(f"--against {against} requires --base-dir")

	discs = parse_discs(
		args.discs,
		lambda d: resolve_base_bin(d, against, base_dir),
		working_bin,
	)
	pack_id = f"{meta['pack_prefix']}-v{version}"
	pack_dir = _ROOT / "builder" / pack_id
	compatible = [meta["base_id"]]

	print(f"Addon:     {meta['display']}")
	print(f"Version:   {version}")
	print(f"Density:   {rate_label(meta['rate'])}")
	print(f"Against:   {against} → compatibleBases={compatible}")
	print(f"Working:   {ISO}")
	print(f"Discs:     {discs}")
	print(f"Output:    builder/{pack_id}/")

	for disc in discs:
		build_one_disc(
			version=version,
			disc=disc,
			against=against,
			meta=meta,
			base_dir=base_dir,
			skip_verify=args.skip_verify,
		)

	write_pack_json(
		pack_dir,
		pack_id=pack_id,
		version=version,
		display=meta["display"],
		blurb=meta["blurb"],
		compatible_bases=compatible,
		discs=discs,
		rate=meta["rate"],
		group_label=meta.get("group_label"),
		option_label=meta.get("option_label"),
	)
	update_manifest(
		pack_id=pack_id,
		pack_prefix=meta["pack_prefix"],
		version=version,
		display=meta["display"],
		blurb=meta["blurb"],
		compatible_bases=compatible,
		discs=discs,
		rate=meta["rate"],
		group_label=meta.get("group_label"),
		option_label=meta.get("option_label"),
	)
	print(f"\nUpdated {pack_dir / 'pack.json'}")
	print(f"Updated {MANIFEST_PATH.relative_to(_ROOT)} (enabled=true, discs={discs})")
	print("\nDone. Commit JSON under builder/ only — not .bin/.cue.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
