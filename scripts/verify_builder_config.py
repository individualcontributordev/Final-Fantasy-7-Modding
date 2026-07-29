#!/usr/bin/env python3
"""Verify a builder config (base + add-ons) using CSR + this repo manifests.

Thin wrapper: stacks layers like the site builder. Implementation lives with
apply_layer in Final-Fantasy-7-CSR; this entrypoint defaults both manifests.

  python scripts/verify_builder_config.py \\
    --pristine workspace/pristine/FINALFANTASY7_D1.bin \\
    --disc 1 --base clean \\
    --addon field-encounter-25-v0.1.2 \\
    --addon world-encounter-25-v0.1.0

  python scripts/verify_builder_config.py \\
    --pristine workspace/pristine/FINALFANTASY7_D1.bin \\
    --disc 1 --base highwind-v0.1.1 \\
    --addon field-encounter-on-highwind-25-v0.1.2

Override CSR checkout with --csr-root if not a sibling of this repo.
"""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

_MODDING = Path(__file__).resolve().parent.parent
_DEFAULT_CSR = _MODDING.parent / "Final-Fantasy-7-CSR"


def main() -> int:
	ap = argparse.ArgumentParser(
		description="Verify builder base+addon stack (CSR + Modding manifests)"
	)
	ap.add_argument("--pristine", type=Path, required=True)
	ap.add_argument("--disc", type=int, required=True, choices=(1, 2, 3))
	ap.add_argument("--base", required=True)
	ap.add_argument("--addon", action="append", default=[], dest="addons")
	ap.add_argument(
		"--csr-root",
		type=Path,
		default=_DEFAULT_CSR,
		help=f"Final-Fantasy-7-CSR root (default: {_DEFAULT_CSR})",
	)
	ap.add_argument("-o", "--output", type=Path, default=None)
	args = ap.parse_args()

	csr_root = args.csr_root.expanduser().resolve()
	csr_script = csr_root / "scripts" / "verify_builder_config.py"
	if not csr_script.is_file():
		raise SystemExit(f"CSR verify script not found: {csr_script}")

	csr_manifest = csr_root / "builder" / "manifest.json"
	mod_manifest = _MODDING / "builder" / "manifest.json"
	if not csr_manifest.is_file():
		raise SystemExit(f"Missing {csr_manifest}")
	if not mod_manifest.is_file():
		raise SystemExit(f"Missing {mod_manifest}")

	# Import CSR apply_layer by putting CSR scripts first, then exec CSR main with argv.
	sys.path.insert(0, str(csr_root / "scripts"))
	argv = [
		str(csr_script),
		"--pristine",
		str(args.pristine.expanduser().resolve()),
		"--disc",
		str(args.disc),
		"--base",
		args.base,
		"--manifest",
		str(csr_manifest),
		"--extra-manifest",
		str(mod_manifest),
	]
	for a in args.addons:
		argv.extend(["--addon", a])
	if args.output:
		argv.extend(["-o", str(args.output)])

	sys.argv = argv
	# Run as __main__
	g = runpy.run_path(str(csr_script), run_name="__not_main__")
	return int(g["main"]())


if __name__ == "__main__":
	raise SystemExit(main())
