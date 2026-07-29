#!/usr/bin/env python3
"""Build world encounter Light/Standard/Dense layers for every current base.

  python mods/world-map-random-encounters/scripts/build_all_rates.py --density all --discs 1
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_MOD_SCRIPTS = Path(__file__).resolve().parent
_ROOT = _MOD_SCRIPTS.parent.parent.parent
BUILD = _MOD_SCRIPTS / "build_on_base.py"
_FIELD_SCRIPTS = _ROOT / "mods" / "field-random-encounters" / "scripts"
sys.path.insert(0, str(_FIELD_SCRIPTS))

from density import parse_densities, prompt_densities, rate_label  # noqa: E402

AGAINSTS = ("clean", "csr", "csr-plus", "highwind")


def main() -> int:
	ap = argparse.ArgumentParser(description="Build world encounter density × base packs.")
	ap.add_argument("--discs", default="1", help="Disc list (default: 1)")
	ap.add_argument(
		"--density",
		"--rates",
		"--rate",
		dest="density",
		default=None,
		metavar="PRESET",
		help="light / standard / dense / all. Omit to pick interactively.",
	)
	ap.add_argument(
		"--against",
		default=None,
		help="Optional single base (default: all of clean/csr/csr-plus/highwind)",
	)
	ap.add_argument("--version", default=None, help="Override VERSION file")
	args = ap.parse_args()

	rates = (
		parse_densities(args.density)
		if args.density is not None
		else prompt_densities(allow_all=True, default="all")
	)
	againsts = [args.against] if args.against else list(AGAINSTS)

	print(
		"Building densities: "
		+ ", ".join(rate_label(r) for r in rates)
		+ f" × against={againsts}"
	)

	failures: list[str] = []
	for rate in rates:
		for against in againsts:
			cmd = [
				sys.executable,
				str(BUILD),
				"--against",
				against,
				"--density",
				str(rate),
				"--discs",
				args.discs,
			]
			if args.version:
				cmd.extend(["--version", args.version])
			print("\n" + "=" * 60)
			print(" ".join(cmd))
			print("=" * 60)
			rc = subprocess.call(cmd)
			if rc != 0:
				failures.append(f"{against} rate={rate} rc={rc}")

	if failures:
		print("\nFailures:")
		for f in failures:
			print(f"  {f}")
		return 1
	print("\nAll world encounter packs built.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
