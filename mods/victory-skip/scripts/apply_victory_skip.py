#!/usr/bin/env python3
"""Force no-victory-music bit on BATTLE.X.dec battle-mode checks."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

_MOD = Path(__file__).resolve().parent.parent
_SITES = _MOD / "patches" / "force-no-victory-music-sites.txt"


def load_sites() -> list[tuple[int, int, int]]:
	"""Return (nop_offset, old_word, new_word)."""
	sites: list[tuple[int, int, int]] = []
	for line in _SITES.read_text(encoding="utf-8").splitlines():
		line = line.split("#", 1)[0].strip()
		if not line:
			continue
		parts = line.split()
		if len(parts) < 3:
			raise SystemExit(f"bad site line: {line!r}")
		off = int(parts[0], 16)
		old = int(parts[1], 16)
		new = int(parts[2], 16)
		sites.append((off, old, new))
	if not sites:
		raise SystemExit(f"no sites in {_SITES}")
	return sites


def discover_sites(dec: bytes) -> list[tuple[int, int, int]]:
	"""Re-scan decompressed BATTLE.X (used to regenerate the sites file)."""
	sites: list[tuple[int, int, int]] = []
	for i in range(0, len(dec) - 16, 4):
		w = struct.unpack_from("<I", dec, i)[0]
		if (w >> 26) != 0x25:
			continue
		imm = w & 0xFFFF
		if imm not in (0x2D7E, 0x2D7C):
			continue
		rt = (w >> 16) & 0x1F
		nop = struct.unpack_from("<I", dec, i + 4)[0]
		andi = struct.unpack_from("<I", dec, i + 8)[0]
		if nop != 0:
			continue
		if (andi >> 26) != 0x0C:
			continue
		mask = andi & 0xFFFF
		if mask == 0x20:
			ori = (0x0D << 26) | (rt << 21) | (rt << 16) | 0x0120
			sites.append((i + 4, 0, ori))
		elif mask == 0x100:
			ori = (0x0D << 26) | (rt << 21) | (rt << 16) | 0x0100
			sites.append((i + 4, 0, ori))
	# 9da0 victory-anim gate (fixed offset on NTSC-U)
	if len(dec) > 0x5480 and struct.unpack_from("<I", dec, 0x547C)[0] == 0:
		ori = (0x0D << 26) | (0 << 21) | (2 << 16) | 0x0020
		sites.append((0x547C, 0, ori))
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
				f"unexpected word at 0x{off:X}: got {got:08X}, "
				f"expected {old:08X} (or already {new:08X})"
			)
		struct.pack_into("<I", data, off, new)
	if write:
		dec_path.write_bytes(data)
	return len(sites)


def verify(dec_path: Path) -> None:
	data = dec_path.read_bytes()
	sites = load_sites()
	for off, _old, new in sites:
		got = struct.unpack_from("<I", data, off)[0]
		if got != new:
			raise SystemExit(
				f"verify fail @ 0x{off:X}: got {got:08X}, expected {new:08X}"
			)
	print(f"Verified {len(sites)} victory-skip sites in {dec_path}")


def main() -> None:
	if len(sys.argv) < 2:
		print(
			f"Usage: {sys.argv[0]} <BATTLE.X.dec> [--verify-only]",
			file=sys.stderr,
		)
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
