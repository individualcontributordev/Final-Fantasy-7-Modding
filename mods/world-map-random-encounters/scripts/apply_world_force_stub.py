#!/usr/bin/env python3
"""Apply RCnt2 FORCE stub over world Danger+= in WORLD.BIN.dec.

Window: VA 0x800B7DB4–0x800B7E1B (104 bytes). jal WorldRand @ 0x800B7E1C must stay.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_MOD = Path(__file__).resolve().parents[1]
_PATCH = _MOD / "patches"
_ROOT = _MOD.parent.parent
# density.py lives under field-random-encounters/scripts
_FIELD_SCRIPTS = _ROOT / "mods" / "field-random-encounters" / "scripts"
if _FIELD_SCRIPTS.is_dir():
	sys.path.insert(0, str(_FIELD_SCRIPTS))
sys.path.insert(0, str(_MOD / "scripts"))

from density import RATES, parse_one_density, prompt_densities, rate_label  # noqa: E402

# File offsets = VA - 0x800A0000
OFFSET = 0x17DB4
JAL_OFFSET = 0x17E1C
STUB_LEN = 104

RATE_MARKERS = {
	0: bytes.fromhex("00 00 00 00"),  # Off
	25: bytes.fromhex("82 18 03 00"),  # srl v1,v1,2
	50: bytes.fromhex("42 18 03 00"),  # srl v1,v1,1
	75: bytes.fromhex("40 08 03 00"),  # sll at,v1,1 (start of *3/4)
}


def _hex(name: str) -> bytes:
	return bytes.fromhex((_PATCH / name).read_text().replace("\n", " "))


def stub_for_rate(rate: int) -> bytes:
	if rate not in RATES:
		raise SystemExit(f"rate must be one of {RATES}")
	stub = _hex(f"stub-7db4-rate{rate}.hex")
	if len(stub) != STUB_LEN:
		raise SystemExit(f"stub must be {STUB_LEN} bytes, got {len(stub)}")
	return stub


JAL = _hex("jal-7e1c.hex")


def apply_stub(path: Path, rate: int = 50) -> bytes:
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
		metavar="PRESET",
		help="off / light / standard / dense (or 0 / 25 / 50 / 75). Omit to pick interactively.",
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
