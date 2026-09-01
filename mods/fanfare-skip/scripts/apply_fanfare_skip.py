#!/usr/bin/env python3
"""Apply the tracked fanfare-skip instruction replacements to BATTLE.X.dec.

Patch sites are loaded from ``force-no-victory-music-sites.txt`` as offset,
expected word, and replacement word triples. Each little-endian word must be
original or already patched before writing, and verification requires every
replacement. This command changes only BATTLE.X code; it does not modify audio
files, compress the overlay, inject a disc, or establish gameplay semantics
beyond the tracked patch."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

_MOD = Path(__file__).resolve().parent.parent
_SITES = _MOD / "patches" / "force-no-victory-music-sites.txt"


def load_sites() -> list[tuple[int, int, int]]:
	"""Load checked little-endian word replacements from the tracked patch table."""
	sites: list[tuple[int, int, int]] = []
	for line in _SITES.read_text(encoding="utf-8").splitlines():
		line = line.split("#", 1)[0].strip()
		if not line:
			continue
		parts = line.split()
		if len(parts) < 3:
			raise SystemExit(f"bad site line: {line!r}")
		sites.append((int(parts[0], 16), int(parts[1], 16), int(parts[2], 16)))
	if not sites:
		raise SystemExit(f"no sites in {_SITES}")
	return sites


def apply_patch(dec_path: Path, *, write: bool = True) -> int:
	"""Apply idempotent replacements only where source or patched words match."""
	data = bytearray(dec_path.read_bytes())
	sites = load_sites()
	# Checking the old instruction word ties each write to the tracked BATTLE.X
	# build. An unknown word may indicate a different executable and is safer to
	# reject than to patch at the same numeric offset.
	for off, old, new in sites:
		got = struct.unpack_from("<I", data, off)[0]
		if got == new:
			continue
		if got != old:
			raise SystemExit(
				f"unexpected word at 0x{off:X}: got {got:08X}, expected {old:08X}"
			)
		struct.pack_into("<I", data, off, new)
	if write:
		dec_path.write_bytes(data)
	return len(sites)


def verify(dec_path: Path) -> None:
	"""Require every tracked site to contain its replacement word."""
	data = dec_path.read_bytes()
	for off, _old, new in load_sites():
		got = struct.unpack_from("<I", data, off)[0]
		if got != new:
			raise SystemExit(
				f"verify fail @ 0x{off:X}: got {got:08X}, expected {new:08X}"
			)
	print(f"Verified {len(load_sites())} fanfare-skip sites in {dec_path}")


def main() -> None:
	if len(sys.argv) < 2:
		print(f"Usage: {sys.argv[0]} <BATTLE.X.dec> [--verify-only]", file=sys.stderr)
		sys.exit(1)
	path = Path(sys.argv[1]).expanduser().resolve()
	if not path.is_file():
		raise SystemExit(f"not found: {path}")
	if "--verify-only" in sys.argv:
		verify(path)
		return
	n = apply_patch(path)
	verify(path)
	print(f"Applied {n} patches -> {path}")


if __name__ == "__main__":
	main()
