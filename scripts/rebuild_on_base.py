#!/usr/bin/env python3
"""Recut field, world, and fanfare packs against one or more exclusive bases.

Run after a CSR base version bump, on a machine holding retail NTSC-U BINs.
Writes ``builder/`` and does not commit.

``all`` is csr + csr-plus + highwind; ``clean`` recuts the pristine packs.
Discs come from the CSR manifest. Recuts run one at a time and stream their
output; the first failure stops the run.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from libs.timing import Timer

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


def require_lf_json() -> None:
	"""Refuse to start if git will not round-trip published layer bytes.

	Digests are taken from the file on disk, but Pages serves the committed
	bytes. Windows silently checks JSON out as CRLF when ``core.autocrlf`` is
	on, which makes every digest describe bytes nobody downloads --- and you
	would only find out when the builder rejected the layer. ``.gitattributes``
	pins ``eol=lf``; ask git whether that rule is actually live here.
	"""
	try:
		attrs = subprocess.run(
			["git", "check-attr", "eol", "--", "builder/manifest.json"],
			cwd=ROOT,
			capture_output=True,
			text=True,
		).stdout
	except OSError as exc:
		raise SystemExit(f"cannot run git to check line-ending rules: {exc}")

	if "eol: lf" not in attrs:
		raise SystemExit(
			"builder JSON is not pinned to LF here "
			f"(git reports: {attrs.strip() or 'nothing'}).\n"
			"Add '*.json text eol=lf' to .gitattributes before publishing."
		)

	crlf = [p for p in (ROOT / "builder").rglob("*.json") if b"\r\n" in p.read_bytes()]
	if crlf:
		raise SystemExit(
			f"{len(crlf)} published JSON files have CRLF line endings, "
			f"starting with {crlf[0].relative_to(ROOT)}.\n"
			"Normalise the checkout first:\n"
			"  git add --renormalize .\n"
			"  git checkout -- builder"
		)


def require_zopfli() -> None:
	"""Fail before copying disc images: stdlib zlib alone overflows ISO slots.

	compress_gzipps.py treats zopfli as optional, but a FIELD/WORLD overlay
	that will not fit its fixed slot stops the run, so demand it up front
	instead of minutes in.
	"""
	try:
		import zopfli.gzip  # noqa: F401
	except ImportError:
		raise SystemExit("zopfli is not installed. Run: pip install zopfli")


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


def recut_commands(
	against: str, discs: list[int], csr: Path | None
) -> list[tuple[str, list[str]]]:
	"""The three recuts for one base, in the order they should run."""
	common = ["--against", against, "--discs", ",".join(str(d) for d in discs)]
	if against != "clean":
		common += ["--csr-root", str(csr)]
	return [
		(f"field on {against}", [sys.executable, str(FIELD), "--density", "all", *common]),
		(f"world on {against}", [sys.executable, str(WORLD), "--density", "all", *common]),
		(f"fanfare on {against}", [sys.executable, str(FANFARE), *common]),
	]


def run(label: str, cmd: list[str], timer: Timer) -> None:
	"""Stream one command, stopping the run if it fails.

	A failed recut leaves its pack pinned to the previous base version, so it
	does not fail visibly -- it silently disappears from the builder. Never
	continue past one.
	"""
	print(f"\n======== {label} ========", flush=True)
	print("$ " + " ".join(cmd), flush=True)
	with timer.stage(label):
		if subprocess.run(cmd, cwd=ROOT).returncode:
			raise SystemExit(f"\n{label} failed -- fix it, then rerun.")


def verify_one(against: str, discs: list[int], csr: Path | None, timer: Timer) -> None:
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
			run(f"verify {addon} disc {disc}", cmd, timer)


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
	timer = Timer()
	with timer.stage("lf_check"):
		require_lf_json()
	require_zopfli()

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

	recuts: list[tuple[str, list[str]]] = []
	for against in bases:
		discs = discs_for(against, manifest)
		print(f"Queue {against} discs {discs}")
		recuts.extend(recut_commands(against, discs, csr))

	print(f"\nRunning {len(recuts)} recuts, one at a time")
	for label, cmd in recuts:
		run(label, cmd, timer)

	print("\nReview git diff under builder/, then commit.")
	print("Do not commit workspace/ or cache/ BINs.")

	if args.verify:
		for against in bases:
			verify_one(against, discs_for(against, manifest), csr, timer)
	timer.total()
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
