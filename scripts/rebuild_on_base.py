#!/usr/bin/env python3
"""Recut field, world, fanfare, New Game+, Party Recolor and Masamune packs against one or more exclusive bases.

Run on a machine holding retail NTSC-U BINs. Writes ``builder/`` and does not
commit.

``all`` is every exclusive parent, Unmodified (catalog id ``clean``) included.
Discs for CSR-family bases come from the CSR manifest.
Recuts run in parallel (``-j N``); each job's output is printed when it
finishes, and the first failure stops the run. Fixups run after the mods they
merge. ``--only MOD ...`` recuts just those mods (and the fixups that merge
them) against the chosen bases. Recuts skip ``builder/manifest.json`` (``FF7_DEFER_MANIFEST``); it is
synced once from the pack.json files at the end.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from libs.local_paths import expand_base_names
from libs.timing import Timer

ROOT = Path(__file__).resolve().parent.parent
RATES = (0, 50, 100, 200)
LOG_DIR = ROOT / "workspace" / "rebuild-logs"  # full output of every recut


MODS = ("field", "world", "fanfare", "new-game-plus", "save-encounter-state", "party-recolor", "masamune")


def script(mod: str, name: str = "build_on_base.py") -> str:
	return str(ROOT / "mods" / mod / "scripts" / name)


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


def recut_commands(
	against: str, discs: list[int], csr: Path | None
) -> list[tuple[str, list[str]]]:
	"""The recuts for one base, in the order they should run."""
	common = ["--against", against, "--discs", ",".join(str(d) for d in discs)]
	if against != "clean":
		common += ["--csr-root", str(csr)]
	cmds = [
		(f"field on {against}", [sys.executable, script("field-random-encounters"), "--density", "0", *common]),
		(f"world on {against}", [sys.executable, script("world-map-random-encounters"), "--density", "0", *common]),
		(f"fanfare on {against}", [sys.executable, script("fanfare-skip"), *common]),
	]
	if against in ("csr-plus", "csr", "highwind", "clean"):  # New Game+: every base
		args = ["--against", against] + (["--csr-root", str(csr)] if against != "clean" else [])
		cmds.append((f"new-game-plus on {against}", [sys.executable, script("new-game-plus"), *args]))
		cmds.append((f"save-encounter-state on {against}", [sys.executable, script("save-encounter-state"), *args]))
		# both mods patch SCUS sectors 28/138; this pack repairs their footers when both are picked
		cmds.append((f"save-encounter-state+new-game-plus fixup on {against}", [sys.executable, script("save-encounter-state", "build_ngp_fixup.py"), *args]))
		cmds.append((f"party-recolor on {against}", [sys.executable, script("party-recolor"), *args]))
		cmds.append((f"masamune on {against}", [sys.executable, script("masamune"), *args]))
		# both mods rewrite the Cloud models + KERNEL; this pack applies last when both are picked
		cmds.append((f"masamune+party-recolor fixup on {against}", [sys.executable, script("masamune", "build_recolor_fixup.py"), *args]))
	return cmds


def run_one(label: str, cmd: list[str]) -> tuple[str, int, str, float]:
	"""Run one recut with output captured so parallel jobs don't interleave."""
	print(f"  start  {label}", flush=True)
	t0 = time.perf_counter()
	# Recuts only write their own pack dir; manifest.json is synced once afterwards.
	env = {**os.environ, "FF7_DEFER_MANIFEST": "1", "PYTHONUNBUFFERED": "1"}
	p = subprocess.run(
		cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
		text=True, errors="replace",
	)
	LOG_DIR.mkdir(parents=True, exist_ok=True)
	log = LOG_DIR / (label.replace(" ", "_").replace("+", "_") + ".log")
	log.write_text(f"$ {' '.join(cmd)}\n{p.stdout}", encoding="utf-8")
	return label, p.returncode, p.stdout, time.perf_counter() - t0


def run_stage(jobs: list[tuple[str, list[str]]], workers: int) -> None:
	"""Run independent recuts in parallel, stopping the run on the first failure.

	A failed recut leaves its pack pinned to the previous base version, so it
	does not fail visibly -- it silently disappears from the builder. Never
	continue past one: pending jobs are cancelled, running ones finish.
	"""
	if not jobs:
		return
	failed = None
	with ThreadPoolExecutor(max_workers=workers) as pool:
		futures = [pool.submit(run_one, label, cmd) for label, cmd in jobs]
		for fut in as_completed(futures):
			label, rc, out, secs = fut.result()
			if rc:
				print(f"\n======== {label} FAILED ({secs:.0f}s) ========\n{out}", flush=True)
			else:
				print(f"  done   {label} ({secs:.0f}s)", flush=True)
			if rc and failed is None:
				failed = label
				for f in futures:
					f.cancel()
	if failed:
		raise SystemExit(f"\n{failed} failed -- fix it, then rerun.")


def sync_manifest(since: float) -> None:
	"""Rewrite manifest entries for packs recut this run from their pack.json.

	pack.json is the single source of truth; the manifest entry is the same
	dict with pack-prefixed layer paths and enabled=true. Entries keep their
	position; new ones are appended.
	"""
	builder = ROOT / "builder"
	path = builder / "manifest.json"
	data = json.loads(path.read_text(encoding="utf-8"))
	addons = data.setdefault("addons", [])
	n = 0
	for pj in sorted(builder.glob("*/pack.json")):
		if pj.stat().st_mtime < since:
			continue
		pack = json.loads(pj.read_text(encoding="utf-8"))
		pid = pack["id"]
		entry = dict(pack)
		entry["discs"] = {d: f"./{pid}/layers/disc{d}.layer.json" for d in pack["discs"]}
		entry["enabled"] = True
		for i, a in enumerate(addons):
			if str(a.get("id", "")) == pid:
				addons[i] = entry
				break
		else:
			addons.append(entry)
		n += 1
	path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
	print(f"Synced {n} manifest entries.")


def remove_retired_encounter_packs() -> None:
	"""Delete published encounter choices no longer listed in ``RATES``."""
	builder = ROOT / "builder"
	removed_ids: set[str] = set()
	for pack_dir in builder.iterdir():
		if not pack_dir.is_dir():
			continue
		pack_id = pack_dir.name
		is_encounter_pack = (
			pack_id.startswith("field-encounter")
			or pack_id.startswith("world-encounter")
		)
		rate_text = pack_id.rsplit("-", 1)[-1]
		if not is_encounter_pack or not rate_text.isdigit():
			continue
		if int(rate_text) in RATES:
			continue
		shutil.rmtree(pack_dir)
		removed_ids.add(pack_id)

	if not removed_ids:
		return

	manifest_path = builder / "manifest.json"
	manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
	addons = manifest.get("addons") or []
	manifest["addons"] = [
		addon for addon in addons if str(addon.get("id", "")) not in removed_ids
	]
	manifest_path.write_text(
		json.dumps(manifest, indent=2) + "\n",
		encoding="utf-8",
		newline="\n",
	)
	print(f"Removed {len(removed_ids)} retired encounter packs.")


def main() -> int:
	ap = argparse.ArgumentParser(
		description="Recut field, world, fanfare and New Game+ packs against current bases."
	)
	ap.add_argument(
		"bases",
		nargs="+",
		help="all, unmodified (clean), csr, csr-plus, and/or highwind",
	)
	ap.add_argument("--csr-root", type=Path, default=None)
	ap.add_argument(
		"--only", metavar="MOD", nargs="+", choices=MODS,
		help="recut just these mods (plus any fixup that merges one of them); default: all",
	)
	ap.add_argument(
		"-j", "--jobs", type=int, default=min(4, os.cpu_count() or 1),
		help="parallel recuts (each holds ~700 MB disc images; 1 = serial)",
	)
	args = ap.parse_args()
	start = time.time()
	timer = Timer()
	with timer.stage("lf_check"):
		require_lf_json()
	require_zopfli()

	bases = expand_base_names(args.bases)

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

	if args.only:
		recuts = [r for r in recuts if set(r[0].split(" ")[0].split("+")) & set(args.only)]
	# Fixups read the layers of the mods they merge, so they run after everything else.
	fixups = [r for r in recuts if "fixup" in r[0]]
	mods = [r for r in recuts if "fixup" not in r[0]]
	print(f"\nRunning {len(recuts)} recuts, {args.jobs} at a time")
	with timer.stage("recuts"):
		run_stage(mods, args.jobs)
	with timer.stage("fixups"):
		run_stage(fixups, args.jobs)

	sync_manifest(start - 2)
	remove_retired_encounter_packs()
	print("\nReview git diff under builder/, then commit.")
	print("Do not commit workspace/ or cache/ BINs.")
	print("Then: python scripts/ff7mod.py verify all   # or unmodified, csr, ...")
	timer.total()
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
