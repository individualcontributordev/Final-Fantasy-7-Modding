#!/usr/bin/env python3
"""Build Field encounter Light/Standard/Dense layers for every current base.

  python mods/field-random-encounters/scripts/build_all_rates.py
  python mods/field-random-encounters/scripts/build_all_rates.py --density all --discs 1
  python mods/field-random-encounters/scripts/build_all_rates.py --density light --against csr-plus
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_MOD_SCRIPTS = Path(__file__).resolve().parent
_ROOT = _MOD_SCRIPTS.parent.parent.parent  # scripts → mod → mods → repo
BUILD = _MOD_SCRIPTS / "build_on_base.py"

from density import parse_densities, prompt_densities, rate_label  # noqa: E402

AGAINSTS = ("clean", "csr", "csr-plus", "csr-plusplus")


def main() -> int:
	ap = argparse.ArgumentParser(
		description="Build Field encounter density × base packs."
	)
	ap.add_argument("--discs", default="1", help="Disc list (default: 1)")
	ap.add_argument(
		"--density",
		"--rates",
		"--rate",
		dest="density",
		default=None,
		metavar="PRESET",
		help=(
			"light / standard / dense / all (or 25 / 50 / 75, comma-list). "
			"Omit to pick interactively."
		),
	)
	ap.add_argument(
		"--against",
		default=None,
		help="Optional single base (default: all of clean/csr/csr-plus/csr-plusplus)",
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
			rc = subprocess.call(cmd, cwd=_ROOT)
			if rc != 0:
				failures.append(f"{rate_label(rate)} against={against} rc={rc}")

	if failures:
		print("\nFAILED:")
		for f in failures:
			print(" ", f)
		return 1
	print("\nAll packs built. Commit builder/ and push.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
