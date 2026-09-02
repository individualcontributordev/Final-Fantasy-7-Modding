#!/usr/bin/env python3
"""Build the playtested fanfare-skip BATRES.X GZIPPS overlay."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_MOD_SCRIPTS = Path(__file__).resolve().parent
_ROOT = _MOD_SCRIPTS.parent.parent.parent
_SHARED = _ROOT / "scripts"
for path in (_SHARED, _MOD_SCRIPTS):
	if str(path) not in sys.path:
		sys.path.insert(0, str(path))

from apply_fanfare_skip import apply_patch, verify  # noqa: E402
from compress_gzipps import compress_gzipps  # noqa: E402
from decompress_gzipps import decompress_gzipps  # noqa: E402


def build(src_batres_x: Path, output: Path | None, keep_dec: bool) -> Path:
	"""Patch and recompress BATRES.X, returning the new overlay path."""
	src_batres_x = src_batres_x.expanduser().resolve()
	if not src_batres_x.is_file():
		raise SystemExit(f"not found: {src_batres_x}")

	patched_dec = src_batres_x.with_name(src_batres_x.name + ".dec.patched")
	if output is None:
		output = src_batres_x.with_name("BATRES.X.new")
	else:
		output = output.expanduser().resolve()

	print("=== 1/4 decompress BATRES.X ===")
	original_dec = decompress_gzipps(src_batres_x, None)
	patched_dec.write_bytes(original_dec.read_bytes())

	print("=== 2/4 apply playtested fanfare skip ===")
	apply_patch(patched_dec)

	print("=== 3/4 verify all BATRES.X sites ===")
	verify(patched_dec)

	print("=== 4/4 recompress BATRES.X ===")
	result = compress_gzipps(patched_dec, src_batres_x, output)

	if not keep_dec:
		for intermediate in (original_dec, patched_dec):
			if intermediate.is_file():
				intermediate.unlink()

	return result


def main() -> None:
	parser = argparse.ArgumentParser(description="Patch BATRES.X for fanfare skip")
	parser.add_argument("batres_x", type=Path, help="Extracted BATTLE/BATRES.X")
	parser.add_argument("-o", "--output", type=Path, default=None)
	parser.add_argument("--keep-dec", action="store_true")
	args = parser.parse_args()
	build(args.batres_x, args.output, args.keep_dec)


if __name__ == "__main__":
	main()
