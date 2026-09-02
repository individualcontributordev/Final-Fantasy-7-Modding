"""Create field-encounter pack metadata and update the local manifest.

Inputs are a base family, shipped rate, version, compatible base id, and built
disc numbers. Outputs are ``pack.json`` and a matching enabled add-on entry in
``builder/manifest.json``. Pack ids derive only from base family plus fixed
rate, so rebuilding a version replaces the same published option rather than
creating a new identity. This module does not build or validate layer bytes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from density import RATES

MOD = Path(__file__).resolve().parents[1]
ROOT = MOD.parent.parent
MANIFEST_PATH = ROOT / "builder" / "manifest.json"
VERSION_FILE = MOD / "VERSION"
EXCLUSIVE_GROUP = "field-encounter-rate"

AGAINST = {
	"clean": {"base_id": "clean", "prefix": "field-encounter", "suffix": ""},
	"csr": {"base_id": "csr", "prefix": "field-encounter-on-csr", "suffix": " (on CSR)"},
	"csr-plus": {
		"base_id": "csr-plus",
		"prefix": "field-encounter-on-csr-plus",
		"suffix": " (on CSR+)",
	},
	"highwind": {
		"base_id": "highwind",
		"prefix": "field-encounter-on-highwind",
		"suffix": " (on Highwind)",
	},
}
RATE_LABEL = {0: "Off", 25: "Light", 50: "Standard", 75: "Dense"}
RATE_BLURB = {
	0: "No random field battles.",
	25: "Fewer random field battles.",
	50: "Moderate random field battles.",
	75: "More random field battles.",
}


def disc_digests(pack_dir: Path, discs: list[int]) -> dict[str, str]:
	"""sha256 of each published layer. The builder caches on these bytes."""
	digests = {}
	for disc in discs:
		path = pack_dir / "layers" / f"disc{disc}.layer.json"
		digests[str(disc)] = hashlib.sha256(path.read_bytes()).hexdigest()
	return digests


def meta_for(against: str, rate: int) -> dict:
	"""Derive stable publication metadata from a base family and shipped rate."""
	if against not in AGAINST:
		raise SystemExit(f"Unknown base: {against}")
	if rate not in RATES:
		raise SystemExit(f"Rate must be one of {RATES}")
	base = AGAINST[against]
	label = RATE_LABEL[rate]
	return {
		"base_id": base["base_id"],
		"pack_prefix": f"{base['prefix']}-{rate}",
		"display": f"Field Random Encounters — {label} ({rate}%){base['suffix']}",
		"group_label": "Field Random Encounters",
		"option_label": f"{label} ({rate}%)",
		"blurb": RATE_BLURB[rate],
		"rate": rate,
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
	rate: int,
	group_label: str,
	option_label: str,
	base_version: str = "",
) -> dict:
	"""Write pack-relative metadata for the disc layers already present."""
	pack = {
		"id": pack_id,
		"name": display,
		"kind": "mod",
		"version": version,
		"blurb": blurb,
		"format": "ic-layer-v1",
		"exclusiveGroup": EXCLUSIVE_GROUP,
		"compatibleBases": compatible_bases,
		"discs": {str(disc): f"./layers/disc{disc}.layer.json" for disc in discs},
		"rate": rate,
		"groupLabel": group_label,
		"optionLabel": option_label,
		"discDigests": disc_digests(pack_dir, discs),
	}
	# Omit on clean: pristine never versions. Required on CSR-family bases or
	# the hosted builder hides the pack.
	if base_version:
		pack["baseVersion"] = base_version
	pack_dir.mkdir(parents=True, exist_ok=True)
	(pack_dir / "pack.json").write_text(
		json.dumps(pack, indent=2) + "\n",
		encoding="utf-8",
	)
	return pack


def update_manifest(*, pack: dict) -> None:
	"""Replace the matching manifest entry while preserving all other add-ons."""
	manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
	pack_id = pack["id"]
	entry = dict(pack)
	# pack.json paths are relative to the pack directory; the top-level
	# manifest is one directory higher and must publish pack-prefixed paths.
	entry["discs"] = {
		disc: f"./{pack_id}/layers/disc{disc}.layer.json"
		for disc in pack["discs"]
	}
	entry["enabled"] = True

	addons = manifest.setdefault("addons", [])
	addons[:] = [addon for addon in addons if addon.get("id") != pack_id]
	addons.append(entry)
	MANIFEST_PATH.write_text(
		json.dumps(manifest, indent=2) + "\n",
		encoding="utf-8",
	)
