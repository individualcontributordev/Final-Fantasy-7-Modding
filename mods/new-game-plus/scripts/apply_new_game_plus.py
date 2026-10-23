#!/usr/bin/env python3
"""Apply the NEW GAME+ changes to a CSR+ disc 1 MODE2/2352 image in place.

Sites are path, offset-in-file, expected bytes, replacement bytes. Every site
must hold either the base bytes or the replacement before anything is written.
Sector EDC/ECC is not recomputed; run scripts/repair_mode2_edc.py afterwards.
"""

from __future__ import annotations

import sys
from pathlib import Path

_MOD = Path(__file__).resolve().parent.parent
_SITES = _MOD / "patches" / "new-game-plus-sites.txt"
sys.path.insert(0, str(_MOD.parent.parent / "scripts"))

from psx_mode2_iso import SECTOR, USER, USER_OFF, find_file  # noqa: E402


def load_sites() -> list[tuple[str, int, bytes, bytes]]:
	"""Load checked byte replacements from the tracked site table."""
	sites = []
	for line in _SITES.read_text(encoding="utf-8").splitlines():
		line = line.split("#", 1)[0].strip()
		if not line:
			continue
		path, off, exp, new = line.split()
		if len(exp) != len(new):
			raise SystemExit(f"site changes payload size: {line!r}")
		sites.append((path, int(off, 16), bytes.fromhex(exp), bytes.fromhex(new)))
	if not sites:
		raise SystemExit(f"no sites in {_SITES}")
	return sites


def _span(img, lba: int, off: int, n: int) -> list[int]:
	"""Raw image offsets of n file bytes starting at off (sector user windows)."""
	return [(lba + (off + k) // USER) * SECTOR + USER_OFF + (off + k) % USER for k in range(n)]


def apply_patch(img: bytearray, revert: bool = False) -> int:
	"""Patch img in place (or undo it); refuse the whole disc if any site is unrecognised."""
	todo = []
	for path, off, exp, new in load_sites():
		if revert:
			exp, new = new, exp
		pos = _span(img, find_file(img, path).lba, off, len(exp))
		got = bytes(img[p] for p in pos)
		if got == new:
			continue
		if got != exp:
			raise SystemExit(
				f"unexpected bytes in {path} @ 0x{off:X}: got {got.hex()}, expected {exp.hex()}"
			)
		todo.append((pos, new))
	for pos, new in todo:
		for p, b in zip(pos, new):
			img[p] = b
	return len(todo)


def main() -> None:
	args = [a for a in sys.argv[1:] if a != "--revert"]
	if len(args) != 1:
		raise SystemExit("usage: apply_new_game_plus.py [--revert] <csr-plus-disc1.bin>")
	revert = len(args) != len(sys.argv) - 1
	path = Path(args[0])
	img = bytearray(path.read_bytes())
	n = apply_patch(img, revert)
	path.write_bytes(img)
	print(f"{'Reverted' if revert else 'Patched'} {n} NEW GAME+ site(s) in {path}; now run repair_mode2_edc.py")


if __name__ == "__main__":
	main()
