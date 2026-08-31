#!/usr/bin/env python3
"""Pack metadata for world-map encounter ic-layer-v1 add-ons."""

from __future__ import annotations

import json
from pathlib import Path

_MOD_SCRIPTS = Path(__file__).resolve().parent
_MOD = _MOD_SCRIPTS.parent
_ROOT = _MOD.parent.parent

MANIFEST_PATH = _ROOT / "builder" / "manifest.json"
VERSION_FILE = _MOD / "VERSION"
EXCLUSIVE_GROUP = "world-encounter-rate"

AGAINST = {
	"clean": {
		"base_id": "clean",
		"prefix_stem": "world-encounter",
		"on_label": "",
	},
	"csr": {
		"base_id": "csr",
		"prefix_stem": "world-encounter-on-csr",
		"on_label": " (on CSR)",
	},
	"csr-plus": {
		"base_id": "csr-plus",
		"prefix_stem": "world-encounter-on-csr-plus",
		"on_label": " (on CSR+)",
	},
	"highwind": {
		"base_id": "highwind",
		"prefix_stem": "world-encounter-on-highwind",
		"on_label": " (on Highwind)",
	},
}

RATE_LABEL = {0: "Off", 25: "Light", 50: "Standard", 75: "Dense"}
RATE_BLURB = {
	0: "No random world-map battles.",
	25: "Fewer random world-map battles.",
	50: "Moderate random world-map battles.",
	75: "More random world-map battles.",
}
RATES = (0, 25, 50, 75)


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
		"display": f"World Random Encounters — {label} ({rate}%){on}",
		"group_label": "World Random Encounters",
		"option_label": f"{label} ({rate}%)",
		"blurb": RATE_BLURB[rate],
		"rate": rate,
		"against": against,
	}


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
) -> dict:
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
	return pack


def update_manifest(*, pack: dict) -> None:
	"""Derive the manifest addon entry from the pack.json dict that
	write_pack_json() just produced, so pack.json stays the single source of
	truth for id/blurb/compatibleBases/etc. and the two files can't drift.
	"""
	if not MANIFEST_PATH.is_file():
		raise SystemExit(f"Missing {MANIFEST_PATH}")
	data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
	pack_id = pack["id"]
	entry = dict(pack)
	entry["name"] = f"{pack['name']} v{pack['version']}"
	entry.pop("version", None)
	entry["discs"] = {
		disc: f"./{pack_id}/layers/disc{disc}.layer.json"
		for disc in pack["discs"]
	}
	entry["enabled"] = True

	addons = data.setdefault("addons", [])
	addons[:] = [a for a in addons if str(a.get("id", "")) != pack_id]
	addons.append(entry)
	MANIFEST_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
