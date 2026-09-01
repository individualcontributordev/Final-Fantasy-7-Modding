"""Synchronize embedded FIELD.BIN/WORLD.BIN lookup sizes with ISO9660.

Inputs are a mutable raw image, an overlay path, current directory entries, and
baseline evidence used to disambiguate repeated LBAs. The selected four-byte
sizes are patched in the decompressed GZIPPS payload, recompressed, and replaced
only if it fits the existing sector allocation. Ambiguous records and growth
beyond capacity stop the operation rather than guessing or relocating files."""
from __future__ import annotations

import gzip
import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from compress_gzipps import compress_gzipps  # noqa: E402
from psx_mode2_iso import (  # noqa: E402
	USER,
	_list_dir,
	_u32_le,
	_user,
	extract_file,
	find_file,
	replace_file_within_sectors,
)


def directory_entries(img: bytes, dir_path: str) -> list[tuple[str, int, int, bool]]:
	"""Resolve a directory and return its immediate ISO9660 children."""
	pvd = _user(img, 16)
	root = pvd[156:190]
	lba, size = _u32_le(root, 2), _u32_le(root, 10)
	for part in dir_path.split("/"):
		entries = _list_dir(img, lba, size)
		match = next(entry for entry in entries if entry[0] == part)
		lba, size = match[1], match[2]
	return _list_dir(img, lba, size)


def fix_bin_table(
	img: bytearray,
	bin_path: str,
	entries: list[tuple[str, int, int, bool]],
	skip_names: set[str],
	baseline_sizes: dict[str, int],
	target_offsets: dict[str, int] | None = None,
) -> int:
	"""Repair unambiguous embedded sizes and replace the recompressed overlay."""
	raw = extract_file(bytes(img), bin_path)
	if raw[8:10] != b"\x1f\x8b":
		raise SystemExit(f"{bin_path} is not GZIPPS")
	payload = bytearray(gzip.decompress(raw[8:]))

	patched = 0
	for name, lba, size, is_dir in entries:
		if is_dir or name in skip_names:
			continue

		inferred_offset = (target_offsets or {}).get(name)
		if inferred_offset is not None:
			recorded_lba, recorded_size = struct.unpack_from("<II", payload, inferred_offset)
			if recorded_lba != lba:
				raise SystemExit(
					f"{bin_path}: offset {inferred_offset} has LBA {recorded_lba}, "
					f"expected {lba}"
				)
			if recorded_size == size:
				continue
			target = inferred_offset
		else:
			lba_key = struct.pack("<I", lba)
			candidates = [
				offset
				for offset in range(len(payload) - 4)
				if payload[offset : offset + 4] == lba_key
			]
			if not candidates:
				continue
			already_correct = [
				offset
				for offset in candidates
				if struct.unpack_from("<I", payload, offset + 4)[0] == size
			]
			if already_correct:
				continue
			if len(candidates) == 1:
				target = candidates[0]
			else:
				# LBA values can occur in executable/data bytes by coincidence.
				# The unchanged size beside the LBA is the evidence that selects
				# an archive-table record without assuming a hard-coded offset.
				baseline_size = baseline_sizes.get(name)
				baseline_matches = [
					offset
					for offset in candidates
					if baseline_size is not None
					and struct.unpack_from("<I", payload, offset + 4)[0]
					== baseline_size
				]
				if len(baseline_matches) != 1:
					raise SystemExit(
						f"{bin_path}: ambiguous lookup record for {name} at LBA {lba}"
					)
				target = baseline_matches[0]

		old_size = struct.unpack_from("<I", payload, target + 4)[0]
		struct.pack_into("<I", payload, target + 4, size)
		print(f"  {bin_path}: {name} size {old_size} -> {size}")
		patched += 1

	if not patched:
		return 0

	meta = find_file(img, bin_path)
	with tempfile.TemporaryDirectory() as temp_dir:
		temp = Path(temp_dir)
		decompressed = temp / "bin.dec"
		original = temp / "bin.orig"
		output = temp / "bin.new"
		decompressed.write_bytes(payload)
		original.write_bytes(raw)
		compress_gzipps(decompressed, original, output)
		recompressed = output.read_bytes()

	# Table repair cannot relocate this archive: its ISO extent and the next
	# file's LBA are fixed, so only the existing sector allocation is writable.
	capacity = ((meta.size + USER - 1) // USER) * USER
	if len(recompressed) > capacity:
		raise SystemExit(
			f"{bin_path}: recompressed {len(recompressed)} > capacity {capacity}"
		)
	replace_file_within_sectors(img, bin_path, recompressed)
	return patched
