#!/usr/bin/env python3
"""Recut every scripted mod against one or more exclusive bases.

Does not edit layers by hand and does not git-commit. Run this on a machine
that has retail NTSC-U BINs after a CSR base version bump (or to backfill
``baseVersion`` on encounter packs). Makou-authored mods are not rebuilt.

  python3 scripts/rebuild_on_base.py csr
  python3 scripts/rebuild_on_base.py all

``all`` is csr + csr-plus + highwind. Pass ``clean`` only when recutting the
pristine packs. Discs come from the CSR manifest (1,2,3 for clean).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSR_FAMILY = ("csr", "csr-plus", "highwind")
RATES = (0, 25, 50, 75)

FIELD = ROOT / "mods" / "field-random-encounters" / "scripts" / "build_on_base.py"
WORLD = ROOT / "mods" / "world-map-random-encounters" / "scripts" / "build_on_base.py"
FANFARE = ROOT / "mods" / "fanfare-skip" / "scripts" / "build_on_base.py"

PACK_PREFIX = {
	"field": {
		"clean": "field-encounter",
		"csr": "field-encounter-on-csr",
		"csr-plus": "field-encounter-on-csr-plus",
		"highwind": "field-encounter-on-highwind",
	},
	"world": {
		"clean": "world-encounter",
		"csr": "world-encounter-on-csr",
		"csr-plus": "world-encounter-on-csr-plus",
		"highwind": "world-encounter-on-highwind",
	},
	"fanfare": {
		"clean": "fanfare-skip",
		"csr": "fanfare-skip-on-csr",
		"csr-plus": "fanfare-skip-on-csr-plus",
		"highwind": "fanfare-skip-on-highwind",
	},
}


def csr_root(cli: Path | None) -> Path:
	if cli is not None:
		return cli.expanduser().resolve()
	env = os.environ.get("FF7_CSR_ROOT")
	if env:
		return Path(env).expanduser().resolve()
	sibling = ROOT.parent / "Final-Fantasy-7-CSR"
	if (sibling / "builder" / "manifest.json").is_file():
		return sibling
	raise SystemExit("Pass --csr-root or set FF7_CSR_ROOT")


def load_csr_manifest(root: Path) -> dict:
	path = root / "builder" / "manifest.json"
	if not path.is_file():
		raise SystemExit(f"Missing CSR manifest: {path}")
	return json.loads(path.read_text(encoding="utf-8"))


def discs_for(against: str, manifest: dict | None) -> list[int]:
	if against == "clean":
		return [1, 2, 3]
	assert manifest is not None
	entry = next(
		(b for b in manifest.get("bases") or [] if str(b.get("id")) == against),
		None,
	)
	if not entry:
		raise SystemExit(f"Base {against!r} not in CSR manifest")
	keys = sorted(int(k) for k in (entry.get("discs") or {}) if str(k).isdigit())
	if not keys:
		raise SystemExit(f"{against} lists no discs")
	return keys


def pack_ids(against: str) -> list[str]:
	field = [f"{PACK_PREFIX['field'][against]}-{rate}" for rate in RATES]
	world = [f"{PACK_PREFIX['world'][against]}-{rate}" for rate in RATES]
	return field + world + [PACK_PREFIX["fanfare"][against]]


def run(cmd: list[str]) -> None:
	print("\n$ " + " ".join(cmd), flush=True)
	subprocess.run(cmd, cwd=ROOT, check=True)


def rebuild_one(against: str, discs: list[int], csr: Path | None) -> None:
	disc_arg = ",".join(str(d) for d in discs)
	common = ["--against", against, "--discs", disc_arg]
	if against != "clean":
		assert csr is not None
		common += ["--csr-root", str(csr)]
	run([sys.executable, str(FIELD), "--density", "all", *common])
	run([sys.executable, str(WORLD), "--density", "all", *common])
	run([sys.executable, str(FANFARE), *common])


def verify_one(against: str, discs: list[int], csr: Path | None) -> None:
	for addon in pack_ids(against):
		for disc in discs:
			cmd = [
				sys.executable,
				str(ROOT / "scripts" / "verify_builder_config.py"),
				"--disc",
				str(disc),
				"--base",
				against,
				"--addon",
				addon,
				"--no-cache",
			]
			if csr is not None:
				cmd += ["--csr-root", str(csr)]
			run(cmd)


def main() -> int:
	ap = argparse.ArgumentParser(
		description="Recut field, world, and fanfare packs against current bases."
	)
	ap.add_argument(
		"bases",
		nargs="+",
		help="csr, csr-plus, highwind, clean, and/or all (CSR-family only)",
	)
	ap.add_argument("--csr-root", type=Path, default=None)
	ap.add_argument(
		"--verify",
		action="store_true",
		help="Run verify_builder_config.py on every rebuilt pack (slow)",
	)
	args = ap.parse_args()

	wanted: list[str] = []
	for token in args.bases:
		if token == "all":
			wanted.extend(CSR_FAMILY)
		elif token in CSR_FAMILY or token == "clean":
			wanted.append(token)
		else:
			raise SystemExit(f"Unknown base {token!r}")
	# Preserve order, drop duplicates (all + csr).
	bases = list(dict.fromkeys(wanted))

	csr = None
	manifest = None
	if any(b != "clean" for b in bases):
		csr = csr_root(args.csr_root)
		manifest = load_csr_manifest(csr)
		print(f"CSR root: {csr}")
		for b in bases:
			if b == "clean":
				continue
			version = next(
				(
					str(e.get("version"))
					for e in manifest.get("bases") or []
					if str(e.get("id")) == b
				),
				"?",
			)
			print(f"  {b} version {version}")

	for against in bases:
		discs = discs_for(against, manifest)
		print(f"\n======== {against} discs {discs} ========")
		rebuild_one(against, discs, csr)
		if args.verify:
			verify_one(against, discs, csr)

	print("\nRebuilt packs. Review git diff under builder/, then commit.")
	print("Do not commit workspace/ or cache/ BINs.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
