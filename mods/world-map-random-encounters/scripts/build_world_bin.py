#!/usr/bin/env python3
"""Build a patched WORLD.BIN GZIPPS overlay for one encounter density.

The input is an extracted WORLD.BIN and output defaults to WORLD.BIN.new. The
pipeline decompresses, applies a tracked world encounter stub, verifies the
stub and preserved JAL bytes, and recompresses against the source overlay.
It does not inject into an ISO, and callers must reject rather than truncate an
output that exceeds its allocated file slot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_MOD_SCRIPTS = Path(__file__).resolve().parent
_MOD = _MOD_SCRIPTS.parent
_ROOT = _MOD.parent.parent
_SHARED = _ROOT / "scripts"
for p in (_SHARED, _MOD_SCRIPTS):
	if str(p) not in sys.path:
		sys.path.insert(0, str(p))

from apply_world_force_stub import (  # noqa: E402
	JAL,
	JAL_OFFSET,
	OFFSET,
	RATE_MARKERS,
	RATES,
	apply_stub,
	stub_for_rate,
)
from compress_gzipps import compress_gzipps  # noqa: E402
from decompress_gzipps import decompress_gzipps  # noqa: E402
from density import parse_one_density, prompt_densities, rate_label  # noqa: E402

EXPECT_HEAD = bytes.fromhex("80 1f 01 3c 20 11 22 8c")


def verify_stub(dec_path: Path, rate: int = 50) -> None:
	"""Require the selected stub and following JAL to match tracked patch bytes."""
	data = dec_path.read_bytes()
	expect = stub_for_rate(rate)
	got = data[OFFSET : OFFSET + len(expect)]
	jal = data[JAL_OFFSET : JAL_OFFSET + 4]
	if got != expect:
		raise SystemExit(
			f"verify failed stub @ 0x{OFFSET:X}: got {got[:16].hex(' ')}…, "
			f"expected {expect[:16].hex(' ')}…"
		)
	if jal != JAL:
		raise SystemExit(
			f"verify failed jal @ 0x{JAL_OFFSET:X}: got {jal.hex(' ')}, "
			f"expected {JAL.hex(' ')}"
		)
	print(f"Verified stub @ 0x{OFFSET:X} ({len(expect)} bytes, rate {rate}%)")
	print(f"Verified jal  @ 0x{JAL_OFFSET:X}: {jal.hex(' ')}")


def build(
	src_bin: Path,
	out_new: Path | None,
	keep_dec: bool,
	rate: int = 50,
) -> Path:
	"""Run the WORLD.BIN overlay pipeline and return the recompressed output path."""
	if rate not in RATES:
		raise SystemExit(f"rate must be one of {RATES}, got {rate}")

	src_bin = src_bin.expanduser().resolve()
	if not src_bin.is_file():
		raise SystemExit(f"not found: {src_bin}")

	dec_path = src_bin.with_name(src_bin.name + ".dec.patched")
	if out_new is None:
		out_new = src_bin.with_name("WORLD.BIN.new")
	else:
		out_new = out_new.expanduser().resolve()

	print("=== 1/4 decompress ===")
	raw_dec = decompress_gzipps(src_bin, None)
	dec_path.write_bytes(raw_dec.read_bytes())

	print(f"\n=== 2/4 apply FORCE stub (rate {rate}%) ===")
	apply_stub(dec_path, rate)
	print(f"Wrote stub into {dec_path}")

	print("\n=== 3/4 verify ===")
	verify_stub(dec_path, rate)

	print("\n=== 4/4 compress → WORLD.BIN.new ===")
	result = compress_gzipps(dec_path, src_bin, out_new)

	if not keep_dec:
		stock_dec = Path(str(src_bin) + ".dec")
		if stock_dec.is_file() and stock_dec.resolve() != dec_path.resolve():
			stock_dec.unlink()
			print(f"Removed intermediate {stock_dec}")

	print("\n=== done ===")
	print(f"Import this over WORLD.BIN in CDmage:\n  {result}")
	print("If 'pad with zeros?' → Yes. If 'truncate?' → Cancel.")
	return result


def main() -> None:
	ap = argparse.ArgumentParser(
		description="Decompress WORLD.BIN, apply encounter FORCE stub, recompress."
	)
	ap.add_argument("world_bin", type=Path, help="Extracted WORLD.BIN (GZIPPS)")
	ap.add_argument("-o", "--output", type=Path, default=None, help="Output WORLD.BIN.new")
	ap.add_argument("--keep-dec", action="store_true")
	ap.add_argument(
		"--density",
		"--rate",
		dest="density",
		default=None,
		metavar="DENSITY",
		help="light / standard / dense (or 25 / 50 / 75). Omit to pick interactively.",
	)
	args = ap.parse_args()
	rate = (
		parse_one_density(args.density)
		if args.density is not None
		else prompt_densities(allow_all=False)[0]
	)
	print(f"Density: {rate_label(rate)}")
	build(args.world_bin, args.output, args.keep_dec, rate)


if __name__ == "__main__":
	main()
