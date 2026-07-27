#!/usr/bin/env python3
"""Build a patched FIELD.BIN.new with the encounter FORCE stub.

Chains: decompress → apply stub → verify → compress.

Example (Makou-extracted FIELD.BIN):
  python scripts/build_field_encounter_patch.py workspace/iso-extract/FIELD.BIN.makou --rate 50

Then CDmage-import the printed FIELD.BIN.new over FIELD/FIELD.BIN (pad Yes if shorter).

See docs/06-packaging-combined-ppf.md for the full Makou + PPF workflow.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
	sys.path.insert(0, str(_SCRIPTS))

from apply_force_stub_rcnt2 import (  # noqa: E402
	JAL,
	JAL_OFFSET,
	OFFSET,
	RATE_MARKERS,
	RATES,
	apply_stub,
)
from compress_field_bin import compress_field_bin  # noqa: E402
from decompress_field_bin import decompress_field_bin  # noqa: E402

EXPECT_HEAD = bytes.fromhex("80 1f 01 3c 20 11 22 8c")


def apply_stub_to_dec(dec_path: Path, rate: int = 50) -> None:
	apply_stub(dec_path, rate)


def verify_stub(dec_path: Path, rate: int = 50) -> None:
	data = dec_path.read_bytes()
	head = data[OFFSET : OFFSET + 8]
	jal = data[JAL_OFFSET : JAL_OFFSET + 4]
	if head != EXPECT_HEAD:
		raise SystemExit(
			f"verify failed @ 0x{OFFSET:X}: got {head.hex(' ')}, "
			f"expected {EXPECT_HEAD.hex(' ')}"
		)
	if jal != JAL:
		raise SystemExit(
			f"verify failed jal @ 0x{JAL_OFFSET:X}: got {jal.hex(' ')}, "
			f"expected {JAL.hex(' ')}"
		)
	mid = data[OFFSET + 24 : OFFSET + 32]
	expect_rate = RATE_MARKERS[rate]
	print(f"Verified stub @ 0x{OFFSET:X}: {head.hex(' ')} …")
	print(f"Verified jal  @ 0x{JAL_OFFSET:X}: {jal.hex(' ')}")
	print(f"Rate {rate}%   @ +24: {mid.hex(' ')}")
	if mid != expect_rate:
		raise SystemExit(
			f"verify failed rate @ +24: got {mid.hex(' ')}, expected {expect_rate.hex(' ')}"
		)


def build(
	src_field_bin: Path,
	out_new: Path | None,
	keep_dec: bool,
	rate: int = 50,
) -> Path:
	if rate not in RATES:
		raise SystemExit(f"rate must be one of {RATES}, got {rate}")

	src_field_bin = src_field_bin.expanduser().resolve()
	if not src_field_bin.is_file():
		raise SystemExit(f"not found: {src_field_bin}")

	dec_path = src_field_bin.with_name(src_field_bin.name + ".dec.patched")
	if out_new is None:
		out_new = src_field_bin.with_name("FIELD.BIN.new")
	else:
		out_new = out_new.expanduser().resolve()

	print("=== 1/4 decompress ===")
	raw_dec = decompress_field_bin(src_field_bin, None)
	dec_path.write_bytes(raw_dec.read_bytes())

	print(f"\n=== 2/4 apply FORCE stub (rate {rate}%) ===")
	apply_stub_to_dec(dec_path, rate)
	print(f"Wrote stub into {dec_path}")

	print("\n=== 3/4 verify ===")
	verify_stub(dec_path, rate)

	print("\n=== 4/4 compress → FIELD.BIN.new ===")
	result = compress_field_bin(dec_path, src_field_bin, out_new)

	if not keep_dec:
		stock_dec = Path(str(src_field_bin) + ".dec")
		for p in (stock_dec,):
			if p.is_file() and p.resolve() != dec_path.resolve():
				p.unlink()
				print(f"Removed intermediate {p}")

	print("\n=== done ===")
	print(f"Import this over FIELD/FIELD.BIN in CDmage:")
	print(f"  {result}")
	print("If 'pad with zeros?' → Yes. If 'truncate?' → Cancel.")
	return result


def main() -> None:
	ap = argparse.ArgumentParser(
		description="Decompress FIELD.BIN, apply encounter FORCE stub, recompress."
	)
	ap.add_argument(
		"field_bin",
		type=Path,
		help="Extracted FIELD.BIN (prefer Makou ISO's FIELD/FIELD.BIN)",
	)
	ap.add_argument(
		"-o",
		"--output",
		type=Path,
		default=None,
		help="Output path (default: FIELD.BIN.new next to input)",
	)
	ap.add_argument(
		"--rate",
		type=int,
		choices=RATES,
		default=50,
		help="Encounter density as %% of raw lure/256 (default 50)",
	)
	ap.add_argument(
		"--keep-dec",
		action="store_true",
		help="Keep intermediate .dec / .dec.patched files",
	)
	args = ap.parse_args()
	build(args.field_bin, args.output, args.keep_dec, rate=args.rate)


if __name__ == "__main__":
	main()
