#!/usr/bin/env python3
"""Apply Fanfare Skip patches to decompressed BATTLE.X."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

_MOD = Path(__file__).resolve().parent.parent
_SITES = _MOD / "patches" / "force-no-victory-music-sites.txt"


def load_sites() -> list[tuple[int, int, int]]:
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
	data = bytearray(dec_path.read_bytes())
	sites = load_sites()
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
