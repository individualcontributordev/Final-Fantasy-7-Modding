#!/usr/bin/env python3
"""Apply the playtested fanfare-skip changes to decompressed BATRES.X.

Patch sites are loaded as offset, expected bytes, and replacement bytes. Every
site must contain either the retail bytes or the replacement before writing.
This prevents an incompatible overlay from being patched at unchecked offsets.
"""

from __future__ import annotations

import sys
from pathlib import Path

_MOD = Path(__file__).resolve().parent.parent
_SITES = _MOD / "patches" / "batres-fanfare-skip-sites.txt"


def load_sites() -> list[tuple[int, bytes, bytes]]:
	"""Load checked byte replacements from the tracked BATRES.X patch table."""
	sites: list[tuple[int, bytes, bytes]] = []
	for line in _SITES.read_text(encoding="utf-8").splitlines():
		line = line.split("#", 1)[0].strip()
		if not line:
			continue
		parts = line.split()
		if len(parts) != 3:
			raise SystemExit(f"bad site line: {line!r}")
		original = bytes.fromhex(parts[1])
		replacement = bytes.fromhex(parts[2])
		if len(original) != len(replacement):
			raise SystemExit(f"site changes payload size: {line!r}")
		sites.append((int(parts[0], 16), original, replacement))
	if not sites:
		raise SystemExit(f"no sites in {_SITES}")
	return sites


def apply_patch(dec_path: Path, *, write: bool = True) -> int:
	"""Apply idempotent replacements only where source or patched bytes match."""
	data = bytearray(dec_path.read_bytes())
	sites = load_sites()
	for offset, original, replacement in sites:
		end = offset + len(original)
		got = bytes(data[offset:end])
		if got == replacement:
			continue
		if got != original:
			raise SystemExit(
				f"unexpected bytes at 0x{offset:X}: got {got.hex()}, "
				f"expected {original.hex()}"
			)
		data[offset:end] = replacement
	if write:
		dec_path.write_bytes(data)
	return len(sites)


def verify(dec_path: Path) -> None:
	"""Require every tracked site to contain its replacement bytes."""
	data = dec_path.read_bytes()
	for offset, _original, replacement in load_sites():
		got = data[offset : offset + len(replacement)]
		if got != replacement:
			raise SystemExit(
				f"verify fail @ 0x{offset:X}: got {got.hex()}, "
				f"expected {replacement.hex()}"
			)
	print(f"Verified {len(load_sites())} fanfare-skip sites in {dec_path}")


def main() -> None:
	if len(sys.argv) < 2:
		print(f"Usage: {sys.argv[0]} <BATRES.X.dec> [--verify-only]", file=sys.stderr)
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
