#!/usr/bin/env python3
"""Recut every scripted mod against one or more exclusive bases.

Does not edit layers by hand and does not git-commit. Run this on a machine
that has retail NTSC-U BINs after a CSR base version bump (or to backfill
``baseVersion`` on encounter packs). Makou-authored mods are not rebuilt.

  python3 scripts/rebuild_on_base.py csr
  python3 scripts/rebuild_on_base.py all
  python3 scripts/rebuild_on_base.py all --jobs 4

``all`` is csr + csr-plus + highwind. Pass ``clean`` only when recutting the
pristine packs. Discs come from the CSR manifest (1,2,3 for clean).

Independent recuts (base × field/world/fanfare) run in parallel. Each job
copies disc images, so ``--jobs`` is capped by RAM more than CPU. Manifest
updates take a file lock so two packs cannot drop each other.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSR_FAMILY = ("csr", "csr-plus", "highwind")
RATES = (0, 25, 50, 75)
DEFAULT_JOBS = 3

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


def job_label(against: str, family: str) -> str:
	return f"{family} on {against}"


def recut_jobs(against: str, discs: list[int], csr: Path | None) -> list[tuple[str, list[str]]]:
	disc_arg = ",".join(str(d) for d in discs)
	common = ["--against", against, "--discs", disc_arg]
	if against != "clean":
		assert csr is not None
		common += ["--csr-root", str(csr)]
	return [
		(job_label(against, "field"), [sys.executable, str(FIELD), "--density", "all", *common]),
		(job_label(against, "world"), [sys.executable, str(WORLD), "--density", "all", *common]),
		(job_label(against, "fanfare"), [sys.executable, str(FANFARE), *common]),
	]


def run_job(label: str, cmd: list[str]) -> tuple[str, int, str]:
	quoted = " ".join(cmd)
	proc = subprocess.run(
		cmd,
		cwd=ROOT,
		text=True,
		capture_output=True,
	)
	body = proc.stdout or ""
	if proc.stderr:
		body += proc.stderr
	text = f"$ {quoted}\n{body}"
	if proc.returncode:
		text += f"\n[exit {proc.returncode}] {label}\n"
	return label, proc.returncode, text


def run_jobs(jobs: list[tuple[str, list[str]]], workers: int) -> None:
	if not jobs:
		return
	workers = max(1, min(workers, len(jobs)))
	print(f"Running {len(jobs)} recuts with --jobs {workers}", flush=True)
	failed: list[str] = []
	with ThreadPoolExecutor(max_workers=workers) as pool:
		futures = {pool.submit(run_job, label, cmd): label for label, cmd in jobs}
		for fut in as_completed(futures):
			label, code, text = fut.result()
			print(f"\n======== {label} ========", flush=True)
			print(text, end="" if text.endswith("\n") else "\n", flush=True)
			if code:
				failed.append(label)
	if failed:
		raise SystemExit("Recut failed: " + ", ".join(failed))


def run(cmd: list[str]) -> None:
	print("\n$ " + " ".join(cmd), flush=True)
	subprocess.run(cmd, cwd=ROOT, check=True)


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
		"--jobs",
		type=int,
		default=DEFAULT_JOBS,
		metavar="N",
		help=(
			f"Parallel recuts (default {DEFAULT_JOBS}). "
			"Each copies disc images; raise only if the machine has RAM to spare. "
			"1 = sequential."
		),
	)
	ap.add_argument(
		"--verify",
		action="store_true",
		help="Run verify_builder_config.py on every rebuilt pack (slow)",
	)
	args = ap.parse_args()
	if args.jobs < 1:
		raise SystemExit("--jobs must be >= 1")

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

	jobs: list[tuple[str, list[str]]] = []
	verify_later: list[tuple[str, list[int]]] = []
	for against in bases:
		discs = discs_for(against, manifest)
		print(f"Queue {against} discs {discs}")
		jobs.extend(recut_jobs(against, discs, csr))
		verify_later.append((against, discs))

	run_jobs(jobs, args.jobs)
	if args.verify:
		for against, discs in verify_later:
			verify_one(against, discs, csr)

	print("\nRebuilt packs. Review git diff under builder/, then commit.")
	print("Do not commit workspace/ or cache/ BINs.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
