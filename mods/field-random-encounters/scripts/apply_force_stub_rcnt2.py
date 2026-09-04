#!/usr/bin/env python3
"""Patch a decompressed FIELD.BIN with a tracked RCnt2 encounter stub.

The input is a mutable FIELD.BIN.dec and the encounter choice selects one of
the shipped 0/50/200 byte sequences. Output overwrites that file at the fixed
stub and JAL offsets; patch bytes come from this mod's tracked ``patches``
directory."""
from __future__ import annotations

import argparse
from pathlib import Path

from density import RATES, parse_one_density, prompt_densities, rate_label

# Decompressed FIELD.BIN offsets: 88-byte stub, then a 4-byte JAL that must
# remain the tracked call site. These are overlay offsets, not disc LBAs.
OFFSET = 0xBB7C
JAL_OFFSET = 0xBBD4

_MOD = Path(__file__).resolve().parents[1]
_PATCH_DIR = _MOD / "patches"

RATE_MARKERS = {
	0: bytes.fromhex("07 80 01 3c 3c 17 20 a4"),
	50: bytes.fromhex("42 18 03 00 00 00 00 00"),
	200: bytes.fromhex("40 18 03 00 02 0a 03 00"),
}

def _load_hex(name: str) -> bytes:
	"""Read one tracked patch file."""
	path = _PATCH_DIR / name
	if not path.is_file():
		raise SystemExit(f"missing patch file: {path}")
	text = path.read_text()
	return bytes.fromhex(text.replace("\n", " "))


def stub_for_rate(rate: int) -> bytes:
	"""Load the exact tracked instruction bytes for one shipped rate."""
	if rate not in RATES:
		raise SystemExit(f"rate must be one of {RATES}, got {rate}")
	return _load_hex(f"stub-bb7c-rate{rate}.hex")


JAL = _load_hex("jal-bbd4.hex")


def apply_stub(path: Path, rate: int = 50) -> bytes:
	"""Overwrite the fixed decompressed-overlay window and return the applied stub."""
	stub = stub_for_rate(rate)
	if len(stub) != 88:
		raise SystemExit(f"stub must be 88 bytes, got {len(stub)}")
	data = bytearray(path.read_bytes())
	if len(data) < JAL_OFFSET + 4:
		raise SystemExit(f"file too small: {len(data)}")
	data[OFFSET : OFFSET + len(stub)] = stub
	data[JAL_OFFSET : JAL_OFFSET + 4] = JAL
	path.write_bytes(data)
	return stub


def main() -> None:
	ap = argparse.ArgumentParser(description="Apply RCnt2 FORCE stub to FIELD.BIN.dec")
	ap.add_argument("dec", type=Path, help="FIELD.BIN.dec or .dec.patched")
	ap.add_argument(
		"--density",
		"--rate",
		dest="density",
		default=None,
		metavar="DENSITY",
		help="off / half / double (or 0 / 50 / 200). Omit to pick interactively.",
	)
	args = ap.parse_args()
	rate = (
		parse_one_density(args.density)
		if args.density is not None
		else prompt_densities(allow_all=False)[0]
	)
	stub = apply_stub(args.dec, rate)
	print(
		f"Patched {args.dec} @ 0x{OFFSET:X} ({len(stub)} bytes); "
		f"jal @ 0x{JAL_OFFSET:X}; {rate_label(rate)}"
	)
	print("Head:", stub[:8].hex(" "))
	print("Rate:", stub[24:32].hex(" "))


if __name__ == "__main__":
	main()
