#!/usr/bin/env python3
"""Decompress FF7 PS1 GZIPPS overlays for Ghidra.

Handles FIELD.BIN, WORLD.BIN, BATTLE/BATTLE.X, BATRES.X, BATINI.X, etc.
See docs/ghidra-battle-overlays.md for extract + image-base load addresses.
"""

from __future__ import annotations

import gzip
import struct
import sys
from pathlib import Path

GZIPPS_HEADER_SIZE = 8
FIELD_RNG_HEAD = bytes.fromhex("B1CAEE6C5A712E55")


def decompress_gzipps(src: Path, dst: Path | None = None) -> Path:
	data = src.read_bytes()
	if len(data) <= GZIPPS_HEADER_SIZE:
		raise ValueError(f"{src}: file too small for GZIPPS header")

	dec_size = struct.unpack("<I", data[0:4])[0]
	gzip_header = data[4:8]

	print(f"Source:           {src}")
	print(f"Compressed size:  {len(data)} bytes")
	print(f"Expected dec size:{dec_size} bytes")
	print(f"GZIPPS sub-header:{gzip_header.hex()}")

	payload = data[GZIPPS_HEADER_SIZE:]
	decompressed = gzip.decompress(payload)

	if len(decompressed) != dec_size:
		print(
			f"Warning: decompressed size {len(decompressed)} != header {dec_size}",
			file=sys.stderr,
		)

	if dst is None:
		dst = src.with_suffix(src.suffix + ".dec")

	dst.write_bytes(decompressed)
	print(f"Wrote:            {dst} ({len(decompressed)} bytes)")

	idx = decompressed.find(FIELD_RNG_HEAD)
	if idx >= 0:
		print(f"Field RNG table found at file offset 0x{idx:X}")

	return dst


# Back-compat name used by older scripts / muscle memory.
decompress_field_bin = decompress_gzipps


def main() -> None:
	if len(sys.argv) < 2:
		print(f"Usage: {sys.argv[0]} <GZIPPS.bin> [output.dec]", file=sys.stderr)
		sys.exit(1)

	src = Path(sys.argv[1]).expanduser().resolve()
	dst = Path(sys.argv[2]).expanduser().resolve() if len(sys.argv) > 2 else None

	if not src.is_file():
		print(f"Error: not found: {src}", file=sys.stderr)
		sys.exit(1)

	decompress_gzipps(src, dst)


if __name__ == "__main__":
	main()
