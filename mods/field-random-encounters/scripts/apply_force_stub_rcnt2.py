#!/usr/bin/env python3
"""Apply RCnt2 FORCE stub at FIELD.BIN.dec offset 0xBB7C.

Canonical bytes live in mods/field-random-encounters/patches/.

Ship via disc builder layers: see repo root README.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from density import RATES, parse_one_density, prompt_densities, rate_label

OFFSET = 0xBB7C
JAL_OFFSET = 0xBBD4

_MOD = Path(__file__).resolve().parents[1]
_PATCH_DIR = _MOD / "patches"

RATE_MARKERS = {
	0: bytes.fromhex("00 00 00 00 00 00 00 00"),  # Off: no threshold ops; danger cleared
	25: bytes.fromhex("82 18 03 00 00 00 00 00"),
	50: bytes.fromhex("42 18 03 00 00 00 00 00"),
	75: bytes.fromhex("82 08 03 00 23 18 61 00"),
}

_FALLBACK = {
	25: (
		"80 1f 01 3c 20 11 22 8c 00 00 00 00 06 80 01 3c"
		"19 2f 23 90 ff 00 42 30 82 18 03 00 00 00 00 00"
		"2b 10 43 00 23 10 02 00 07 80 01 3c 3c 17 22 a4"
		+ (" 00 00 00 00" * 10)
	),
	50: (
		"80 1f 01 3c 20 11 22 8c 00 00 00 00 06 80 01 3c"
		"19 2f 23 90 ff 00 42 30 42 18 03 00 00 00 00 00"
		"2b 10 43 00 23 10 02 00 07 80 01 3c 3c 17 22 a4"
		+ (" 00 00 00 00" * 10)
	),
	75: (
		"80 1f 01 3c 20 11 22 8c 00 00 00 00 06 80 01 3c"
		"19 2f 23 90 ff 00 42 30 82 08 03 00 23 18 61 00"
		"2b 10 43 00 23 10 02 00 07 80 01 3c 3c 17 22 a4"
		+ (" 00 00 00 00" * 10)
	),
}


def _load_hex(name: str, fallback: str = "") -> bytes:
	path = _PATCH_DIR / name
	if path.is_file():
		text = path.read_text()
	elif fallback:
		text = fallback
	else:
		raise SystemExit(f"missing patch file: {path}")
	return bytes.fromhex(text.replace("\n", " "))


def stub_for_rate(rate: int) -> bytes:
	if rate not in RATES:
		raise SystemExit(f"rate must be one of {RATES}, got {rate}")
	return _load_hex(f"stub-bb7c-rate{rate}.hex", _FALLBACK.get(rate, ""))


JAL = _load_hex("jal-bbd4.hex", "72 ae 02 0c")
STUB = stub_for_rate(50)


def apply_stub(path: Path, rate: int = 50) -> bytes:
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
		metavar="PRESET",
		help="off / light / standard / dense (or 0 / 25 / 50 / 75). Omit to pick interactively.",
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
