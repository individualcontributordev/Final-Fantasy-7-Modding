#!/usr/bin/env python3
"""Verify a builder-output disc image (SRP: read-only checks, no patching).

Reports APPLIED.txt summary (if present next to the .bin) and whether the
shipped RCnt2 FORCE stub prefix appears in decompressed FIELD.BIN and/or
WORLD.BIN extracted from the image.

  python scripts/verify_built_disc.py path/to/built/FINALFANTASY7_D1.bin
  python scripts/verify_built_disc.py path/to/build-folder/   # picks first .bin
"""

from __future__ import annotations

import argparse
import gzip
import struct
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
	sys.path.insert(0, str(_SCRIPTS))

from psx_mode2_iso import extract_file  # noqa: E402

GZIPPS_HEADER_SIZE = 8
# lui at,0x1f80 ; lw v0,0x1120(at)  — start of shipped RCnt2 FORCE stub
RCNT2_STUB_PREFIX = bytes.fromhex("801f013c2011228c")
FIELD_STUB_OFF = 0xBB7C
# World stub offset in .dec (documented in world patches)
WORLD_STUB_OFF = 0x17DB4


def _decompress_gzipps(blob: bytes) -> bytes:
	if len(blob) <= GZIPPS_HEADER_SIZE:
		raise ValueError("file too small for GZIPPS")
	payload = blob[GZIPPS_HEADER_SIZE:]
	return gzip.decompress(payload)


def _check_engine(label: str, compressed: bytes, stub_off: int) -> dict:
	dec = _decompress_gzipps(compressed)
	at_off = dec[stub_off : stub_off + len(RCNT2_STUB_PREFIX)]
	found_at = at_off == RCNT2_STUB_PREFIX
	idx = dec.find(RCNT2_STUB_PREFIX)
	return {
		"label": label,
		"dec_size": len(dec),
		"stub_at_expected_off": found_at,
		"expected_off": stub_off,
		"prefix_first_index": idx,
		"head_at_expected": at_off.hex() if len(at_off) == len(RCNT2_STUB_PREFIX) else "",
	}


def _resolve_bin(path: Path) -> Path:
	path = path.expanduser().resolve()
	if path.is_file() and path.suffix.lower() == ".bin":
		return path
	if path.is_dir():
		bins = sorted(path.glob("*.bin")) + sorted(path.glob("*.BIN"))
		if not bins:
			raise SystemExit(f"No .bin in directory: {path}")
		if len(bins) > 1:
			print(f"Note: multiple .bin files; using {bins[0].name}", file=sys.stderr)
		return bins[0]
	raise SystemExit(f"Not a .bin or directory: {path}")


def _print_applied(applied: Path) -> None:
	print(f"=== APPLIED.txt ({applied}) ===")
	text = applied.read_text(encoding="utf-8", errors="replace")
	print(text.rstrip() or "(empty)")
	print()
	low = text.lower()
	for needle in (
		"field-encounter",
		"world-encounter",
		"csr-plus-scene",
		"highwind",
		"csr-v",
		"clean",
		"csr-plusplus",
	):
		if needle in low:
			print(f"  mentions {needle!r}: yes")
	print()


def main() -> int:
	ap = argparse.ArgumentParser(description="Verify builder-output disc (stub + APPLIED)")
	ap.add_argument("path", type=Path, help="Built .bin or folder containing it")
	ap.add_argument(
		"--skip-world",
		action="store_true",
		help="Only check FIELD.BIN (faster if world not needed)",
	)
	args = ap.parse_args()
	bin_path = _resolve_bin(args.path)
	print(f"Image: {bin_path} ({bin_path.stat().st_size} bytes)")

	applied = bin_path.with_name("APPLIED.txt")
	if not applied.is_file():
		# same stem folder root
		applied = bin_path.parent / "APPLIED.txt"
	if applied.is_file():
		_print_applied(applied)
	else:
		print("=== APPLIED.txt ===\n(not found next to image)\n")

	img = bin_path.read_bytes()
	print("=== Engine stubs (RCnt2 FORCE prefix) ===")
	try:
		field = extract_file(img, "FIELD/FIELD.BIN")
		fr = _check_engine("FIELD/FIELD.BIN", field, FIELD_STUB_OFF)
		print(
			f"{fr['label']}: dec={fr['dec_size']} "
			f"stub@{fr['expected_off']:#x}={'YES' if fr['stub_at_expected_off'] else 'NO'} "
			f"head={fr['head_at_expected'] or 'n/a'} "
			f"first_prefix_idx={fr['prefix_first_index']}"
		)
	except Exception as exc:
		print(f"FIELD/FIELD.BIN: ERROR {exc}", file=sys.stderr)

	if not args.skip_world:
		try:
			world = extract_file(img, "WORLD/WORLD.BIN")
			wr = _check_engine("WORLD/WORLD.BIN", world, WORLD_STUB_OFF)
			print(
				f"{wr['label']}: dec={wr['dec_size']} "
				f"stub@{wr['expected_off']:#x}={'YES' if wr['stub_at_expected_off'] else 'NO'} "
				f"head={wr['head_at_expected'] or 'n/a'} "
				f"first_prefix_idx={wr['prefix_first_index']}"
			)
		except Exception as exc:
			print(f"WORLD/WORLD.BIN: ERROR {exc}", file=sys.stderr)

	print()
	print(
		"Interpret: Light field pack should show FIELD stub@0xbb7c=YES. "
		"Vanilla Danger ramp ⇒ stub NO or wrong boot image."
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
