#!/usr/bin/env python3
"""Patch a decompressed WORLD.BIN with a tracked RCnt2 encounter stub.

The mutable input and encounter choice select one of three fixed patch files.
The command replaces the verified 104-byte instruction window and restores the
tracked JAL word immediately after it."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_MOD = Path(__file__).resolve().parents[1]
_PATCH = _MOD / "patches"
sys.path.insert(0, str(_MOD / "scripts"))

from density import RATES, parse_one_density, prompt_densities, rate_label  # noqa: E402

# The tracked patch's load base maps the documented virtual-address window to
# these decompressed WORLD.BIN offsets; offsets are not raw-disc addresses.
OFFSET = 0x17DB4
JAL_OFFSET = 0x17E1C
STUB_LEN = 104

RATE_MARKERS = {
	0: bytes.fromhex("11 80 01 3c 84 62 20 ac"),
	50: bytes.fromhex("42 18 03 00 00 00 00 00"),
	200: bytes.fromhex("40 18 03 00 02 0a 03 00"),
}


def _hex(name: str) -> bytes:
	"""Load a tracked WORLD.BIN patch file as raw instruction bytes."""
	return bytes.fromhex((_PATCH / name).read_text().replace("\n", " "))


def stub_for_rate(rate: int) -> bytes:
	"""Load and length-check the tracked instruction window for one shipped rate."""
	if rate not in RATES:
		raise SystemExit(f"rate must be one of {RATES}")
	stub = _hex(f"stub-7db4-rate{rate}.hex")
	if len(stub) != STUB_LEN:
		raise SystemExit(f"stub must be {STUB_LEN} bytes, got {len(stub)}")
	return stub


JAL = _hex("jal-7e1c.hex")


def apply_stub(path: Path, rate: int = 50) -> bytes:
	"""Overwrite the fixed decompressed-overlay window and restore the tracked JAL."""
	stub = stub_for_rate(rate)
	data = bytearray(path.read_bytes())
	if len(data) < JAL_OFFSET + 4:
		raise SystemExit(f"file too small: {len(data)}")
	data[OFFSET : OFFSET + STUB_LEN] = stub
	data[JAL_OFFSET : JAL_OFFSET + 4] = JAL
	path.write_bytes(data)
	return stub


def main() -> None:
	ap = argparse.ArgumentParser(description="Apply world-map RCnt2 FORCE stub to WORLD.BIN.dec")
	ap.add_argument("dec", type=Path, help="WORLD.BIN.dec or .dec.patched")
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
	stub = apply_stub(args.dec.expanduser().resolve(), rate)
	print(
		f"Patched {args.dec} @ 0x{OFFSET:X} ({len(stub)} bytes); "
		f"jal @ 0x{JAL_OFFSET:X}; {rate_label(rate)}"
	)
	print("Head:", stub[:8].hex(" "))
	print("Marker:", RATE_MARKERS[rate].hex(" "))


if __name__ == "__main__":
	main()
