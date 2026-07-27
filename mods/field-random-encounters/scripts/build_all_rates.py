#!/usr/bin/env python3
"""Build Field encounter 25%/50%/75% layers for every current base (Disc 1 by default).

  python mods/field-random-encounters/scripts/build_all_rates.py
  python mods/field-random-encounters/scripts/build_all_rates.py --discs 1 --rates 25,50,75
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_MOD_SCRIPTS = Path(__file__).resolve().parent
_ROOT = _MOD_SCRIPTS.parent.parent.parent  # scripts → mod → mods → repo
BUILD = _MOD_SCRIPTS / "build_on_base.py"

AGAINSTS = ("clean", "csr", "csr-plus", "csr-plusplus")
DEFAULT_RATES = (25, 50, 75)


def main() -> int:
	ap = argparse.ArgumentParser(description="Build all Field encounter rate × base packs.")
	ap.add_argument("--discs", default="1", help="Disc list (default: 1)")
	ap.add_argument(
		"--rates",
		default="25,50,75",
		help="Comma list of rates (default: 25,50,75)",
	)
	ap.add_argument(
		"--against",
		default=None,
		help="Optional single base (default: all of clean/csr/csr-plus/csr-plusplus)",
	)
	ap.add_argument("--version", default=None, help="Override VERSION file")
	args = ap.parse_args()

	rates = [int(x.strip()) for x in args.rates.split(",") if x.strip()]
	againsts = [args.against] if args.against else list(AGAINSTS)

	failures: list[str] = []
	for rate in rates:
		for against in againsts:
			cmd = [
				sys.executable,
				str(BUILD),
				"--against",
				against,
				"--rate",
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
				failures.append(f"rate={rate} against={against} rc={rc}")

	if failures:
		print("\nFAILED:")
		for f in failures:
			print(" ", f)
		return 1
	print("\nAll packs built. Commit builder/ and push.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
