#!/usr/bin/env python3
"""Build a fanfare-skip BATTLE.X GZIPPS overlay.

The input is an extracted BATTLE/BATTLE.X and output defaults to BATTLE.X.new.
The command decompresses, applies and verifies all tracked instruction sites,
then recompresses using the original overlay as its format and size reference.
It never edits FAN2.SND or injects an ISO; an oversized output must be rejected
by the caller rather than truncated."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_MOD_SCRIPTS = Path(__file__).resolve().parent
_ROOT = _MOD_SCRIPTS.parent.parent.parent
_SHARED = _ROOT / "scripts"
for p in (_SHARED, _MOD_SCRIPTS):
	if str(p) not in sys.path:
		sys.path.insert(0, str(p))

from apply_fanfare_skip import apply_patch, verify  # noqa: E402
from compress_gzipps import compress_gzipps  # noqa: E402
from decompress_gzipps import decompress_gzipps  # noqa: E402


def build(src_battle_x: Path, out_new: Path | None, keep_dec: bool) -> Path:
	"""Patch and recompress BATTLE.X, returning the new overlay path."""
	src_battle_x = src_battle_x.expanduser().resolve()
	if not src_battle_x.is_file():
		raise SystemExit(f"not found: {src_battle_x}")

	dec_path = src_battle_x.with_name(src_battle_x.name + ".dec.patched")
	if out_new is None:
		out_new = src_battle_x.with_name("BATTLE.X.new")
	else:
		out_new = out_new.expanduser().resolve()

	print("=== 1/4 decompress ===")
	raw_dec = decompress_gzipps(src_battle_x, None)
	dec_path.write_bytes(raw_dec.read_bytes())

	print("=== 2/4 apply fanfare-skip ===")
	apply_patch(dec_path)
	print(f"Wrote patches into {dec_path}")

	print("=== 3/4 verify ===")
	verify(dec_path)

	print("=== 4/4 compress -> BATTLE.X.new ===")
	result = compress_gzipps(dec_path, src_battle_x, out_new)

	if not keep_dec:
		stock_dec = Path(str(src_battle_x) + ".dec")
		if stock_dec.is_file() and stock_dec.resolve() != dec_path.resolve():
			stock_dec.unlink()
			print(f"Removed intermediate {stock_dec}")

	print("=== done ===")
	print(f"  {result}")
	return result


def main() -> None:
	ap = argparse.ArgumentParser(description="Patch BATTLE.X for fanfare skip")
	ap.add_argument("battle_x", type=Path, help="Extracted BATTLE/BATTLE.X")
	ap.add_argument("-o", "--output", type=Path, default=None)
	ap.add_argument("--keep-dec", action="store_true")
	args = ap.parse_args()
	build(args.battle_x, args.output, args.keep_dec)


if __name__ == "__main__":
	main()
