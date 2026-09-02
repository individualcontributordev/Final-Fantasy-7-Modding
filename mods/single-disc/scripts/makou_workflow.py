"""Provide Makou preparation, stabilization, validation, and release helpers.

These functions synchronize embedded archive tables, reserve FIELD.BIN
recompression headroom, repair changed Mode 2 Form 1 EDC/ECC, validate ISO
bounds/layout, and emit ``ic-layer-v1`` release artifacts. Inputs and outputs
are explicit local paths; artifacts are never overwritten. A release is
accepted only when applying its layer to the declared builder parent exactly
reconstructs the stabilized image."""
from __future__ import annotations

import gzip
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from libs.layer import apply_layer, build_layer  # noqa: E402
from edc_ecc import repair_sector_edc_ecc  # noqa: E402
from archive_tables import directory_entries, fix_bin_table  # noqa: E402
from psx_mode2_iso import (  # noqa: E402
	SECTOR,
	USER,
	_patch_dirent_size_only,
	_u32_le,
	_user,
	_write_user,
	extract_file,
	find_file,
)
from verify_iso_integrity import sector_count, walk_tree  # noqa: E402


def write_new(path: Path, data: bytes) -> None:
	"""Create an output file; refuse if it already exists so prior artifacts stay intact."""
	if path.exists():
		raise SystemExit(f"Refusing to overwrite build artifact: {path}")
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_bytes(data)


def write_json(path: Path, value: object) -> None:
	write_new(path, (json.dumps(value, indent=2) + "\n").encode())


def sha256(path: Path) -> str:
	"""Hash a local file for stage reports without loading it all at once."""
	digest = hashlib.sha256()
	with path.open("rb") as stream:
		while chunk := stream.read(1024 * 1024):
			digest.update(chunk)
	return digest.hexdigest()


def fix_tables_for_disc(image: bytearray, baseline: bytes) -> int:
	"""Repair FIELD and WORLD embedded sizes using an unchanged baseline."""
	total = 0
	for directory, bin_path, skip_name in (
		("FIELD", "FIELD/FIELD.BIN", "FIELD.BIN"),
		("WORLD", "WORLD/WORLD.BIN", "WORLD.BIN"),
	):
		entries = directory_entries(bytes(image), directory)
		baseline_sizes = {
			name: size
			for name, _lba, size, is_dir in directory_entries(baseline, directory)
			if not is_dir
		}
		total += fix_bin_table(
			image,
			bin_path,
			entries,
			skip_names={skip_name},
			baseline_sizes=baseline_sizes,
		)
	return total


def makou_compressed_size(image: bytes | bytearray) -> int:
	"""Estimate FIELD.BIN size after Makou's level-9 gzip of the current payload."""
	raw = extract_file(image, "FIELD/FIELD.BIN")
	decompressed = gzip.decompress(raw[8:])
	return 8 + len(gzip.compress(decompressed, compresslevel=9, mtime=0))


def makou_resize_probe_size(image: bytes | bytearray) -> int:
	"""Estimate FIELD.BIN size after a one-byte lookup-table bump, as Makou may do on save."""
	raw = extract_file(image, "FIELD/FIELD.BIN")
	decompressed = bytearray(gzip.decompress(raw[8:]))
	eals = next(
		(
			entry
			for entry in directory_entries(bytes(image), "FIELD")
			if entry[0] == "EALS_1.DAT"
		),
		None,
	)
	if eals is None:
		raise SystemExit("FIELD/EALS_1.DAT not found for Makou resize probe")
	_name, lba, size, _is_dir = eals
	offset = decompressed.find(struct.pack("<II", lba, size))
	if offset < 0:
		raise SystemExit("EALS_1 lookup entry missing for Makou resize probe")
	struct.pack_into("<I", decompressed, offset + 4, size + 1)
	return 8 + len(gzip.compress(decompressed, compresslevel=9, mtime=0))


def reserve_makou_field_bin_space(image: bytearray) -> dict:
	"""Expand FIELD.BIN's recorded slot into verified free sectors."""
	meta = find_file(image, "FIELD/FIELD.BIN")
	field_entries = sorted(
		(lba, name)
		for name, lba, _size, is_dir in directory_entries(bytes(image), "FIELD")
		if not is_dir and lba > meta.lba
	)
	next_lba = field_entries[0][0] if field_entries else len(image) // SECTOR
	available_sectors = next_lba - meta.lba
	required_sectors = (makou_compressed_size(image) + USER - 1) // USER
	current_sectors = (meta.size + USER - 1) // USER
	# Makou recompresses FIELD.BIN and may grow it after even a small field edit.
	# Two extra logical sectors keep that save within the verified gap before
	# the next file; no following extent is moved.
	reserved_sectors = max(current_sectors, required_sectors + 2)
	if reserved_sectors > available_sectors:
		raise SystemExit(
			"FIELD.BIN has no safe room for Makou recompression: "
			f"need {reserved_sectors} sectors, have {available_sectors}"
		)

	original = extract_file(image, "FIELD/FIELD.BIN")
	reserved_size = reserved_sectors * USER
	payload = original + b"\x00" * (reserved_size - len(original))
	for index in range(reserved_sectors):
		start = index * USER
		_write_user(image, meta.lba + index, payload[start : start + USER])
	_patch_dirent_size_only(image, "FIELD/FIELD.BIN", reserved_size)
	compressed_size = makou_compressed_size(image)
	return {
		"lba": meta.lba,
		"nextFileLba": next_lba,
		"makouCompressedBytes": compressed_size,
		"reservedBytes": reserved_size,
		"headroomBytes": reserved_size - compressed_size,
	}


def is_mode2_form1(sector: bytes | bytearray) -> bool:
	"""True for a 2352-byte CD-XA Mode 2 Form 1 sector (subheader bit 5 clear)."""
	valid_sync = sector[0] == 0 and sector[11] == 0
	valid_header = sector[15] == 2 and all(value == 0xFF for value in sector[1:11])
	return valid_sync and valid_header and not (sector[18] & 0x20)


def repair_changed_edc_ecc(image: bytearray, retail: bytes) -> int:
	"""Repair changed Form 1 sectors while leaving retail-identical sectors alone."""
	repaired = 0
	for sector_number in range(len(image) // SECTOR):
		offset = sector_number * SECTOR
		sector = image[offset : offset + SECTOR]
		if offset < len(retail) and sector == retail[offset : offset + SECTOR]:
			continue
		if not is_mode2_form1(sector):
			continue
		# ISO writes alter only the 2048-byte user window. Raw MODE2/2352 media
		# also carries EDC and P/Q parity, which must describe the new user data.
		repair_sector_edc_ecc(sector)
		image[offset : offset + SECTOR] = sector
		repaired += 1
	return repaired


def verify_changed_edc_ecc(image: bytes | bytearray, retail: bytes) -> int:
	"""Require every changed Form 1 sector footer to match a fresh calculation."""
	verified = 0
	for sector_number in range(len(image) // SECTOR):
		offset = sector_number * SECTOR
		sector = image[offset : offset + SECTOR]
		if offset < len(retail) and sector == retail[offset : offset + SECTOR]:
			continue
		if not is_mode2_form1(sector):
			continue
		expected = bytearray(sector)
		repair_sector_edc_ecc(expected)
		if expected != sector:
			raise SystemExit(f"Invalid EDC/ECC at LBA {sector_number}")
		verified += 1
	return verified


def verify_disc_bounds(image: bytes | bytearray) -> dict:
	"""Require sector alignment, a matching PVD size, and an under-80-minute image."""
	if len(image) % SECTOR:
		raise SystemExit(f"Image is not MODE2/2352 sector-aligned: {len(image)}")
	actual_sectors = len(image) // SECTOR
	declared_sectors = _u32_le(_user(image, 16), 80)
	if declared_sectors != actual_sectors:
		raise SystemExit(
			f"PVD volume size mismatch: declared {declared_sectors}, actual {actual_sectors}"
		)
	if actual_sectors >= 80 * 60 * 75:
		raise SystemExit(f"Image exceeds 80-minute CD limit: {actual_sectors} sectors")
	return {
		"sectors": actual_sectors,
		"pvdVolumeSectors": declared_sectors,
		"under80MinuteCdLimit": True,
	}


def verify_iso_layout(
	image: bytes | bytearray,
	allowed_overlaps: frozenset[tuple[str, str]] = frozenset(),
) -> dict:
	"""Reject duplicate LBAs and unapproved overlaps in the recursive ISO tree."""
	pvd = _user(image, 16)
	root = pvd[156:190]
	entries: list[tuple[str, int, int, bool]] = [
		("[root]", _u32_le(root, 2), _u32_le(root, 10), True)
	]
	walk_tree(bytes(image), _u32_le(root, 2), _u32_le(root, 10), "", entries)

	lbas: dict[int, list[str]] = {}
	for name, lba, _size, _is_dir in entries:
		lbas.setdefault(lba, []).append(name)
	duplicates = {lba: names for lba, names in lbas.items() if len(names) > 1}

	overlaps = []
	expected_overlaps = []
	ordered = sorted(entries, key=lambda entry: entry[1])
	for previous, current in zip(ordered, ordered[1:]):
		previous_name, previous_lba, previous_size, _ = previous
		current_name, current_lba, _current_size, _ = current
		previous_end = previous_lba + sector_count(previous_size, previous_name)
		if previous_end <= current_lba:
			continue
		overlap = (previous_name, current_name, previous_end - current_lba)
		if (previous_name, current_name) in allowed_overlaps:
			expected_overlaps.append(overlap)
		else:
			overlaps.append(overlap)

	if duplicates or overlaps:
		raise SystemExit(
			f"ISO layout failure: duplicateLbas={duplicates}, overlaps={overlaps}"
		)
	return {
		"entries": len(entries),
		"duplicateLbas": 0,
		"overlaps": 0,
		"expectedOverlaps": expected_overlaps,
	}


def verify_makou_preconditions(image: bytes | bytearray) -> dict:
	"""Check embedded lookup keys, YAMADA references, and FIELD.BIN headroom."""
	field_bin = gzip.decompress(extract_file(image, "FIELD/FIELD.BIN")[8:])
	bad_field_keys = []
	for name, lba, size, is_dir in directory_entries(bytes(image), "FIELD"):
		if is_dir or name.endswith(".X") or name == "FIELD.BIN":
			continue
		key = struct.pack("<II", lba, size)
		count = field_bin.count(key)
		after_start = field_bin[0x30000:].count(key)
		if count != 1 and not (count > 1 and after_start == 1):
			bad_field_keys.append(name)

	yamada = extract_file(image, "INIT/YAMADA.BIN")
	# INIT/YAMADA.BIN stores little-endian (LBA, size) pairs at 8-byte slots.
	# Index 0 is unused here; slot i must match the ISO directory for that file.
	yamada_files = (
		"INIT/WINDOW.BIN",
		"INIT/KERNEL.BIN",
		"BATTLE/BROM.X",
		"BATTLE/TITLE.BIN",
		"BATTLE/BATTLE.X",
		"BATTLE/BATINI.X",
		"BATTLE/SCENE.BIN",
		"BATTLE/BATRES.X",
		"BATTLE/CO.BIN",
	)
	bad_yamada = []
	for index, file_path in enumerate(yamada_files, 1):
		expected = struct.unpack_from("<II", yamada, index * 8)
		actual = find_file(image, file_path)
		if (actual.lba, actual.size) != expected:
			bad_yamada.append(file_path)

	field_meta = find_file(image, "FIELD/FIELD.BIN")
	largest_probe = max(makou_compressed_size(image), makou_resize_probe_size(image))
	headroom = field_meta.size - largest_probe
	if bad_field_keys or bad_yamada or headroom < 2 * USER:
		raise SystemExit(
			"Makou precondition failure: "
			f"fieldKeys={bad_field_keys}, yamada={bad_yamada}, headroom={headroom}"
		)
	return {
		"fieldLookupKeys": "pass",
		"yamadaReferences": "pass",
		"fieldBinAllocatedBytes": field_meta.size,
		"fieldBinHeadroomAfterResizeProbeBytes": headroom,
	}


def cue_for(bin_path: Path) -> bytes:
	"""Write a one-track MODE2/2352 CUE that names the sibling BIN."""
	return (
		f'FILE "{bin_path.name}" BINARY\n'
		"  TRACK 01 MODE2/2352\n"
		"    INDEX 01 00:00:00\n"
	).encode()


def stabilize_working_image(
	*,
	input_image: Path,
	table_baseline: Path,
	edc_reference: Path,
	output_image: Path,
	report_path: Path,
) -> dict:
	"""Normalize and validate an image, then write BIN/CUE and a report."""
	for required in (input_image, table_baseline, edc_reference):
		if not required.is_file():
			raise SystemExit(f"Missing input: {required}")

	image = bytearray(input_image.read_bytes())
	table_patches = fix_tables_for_disc(image, table_baseline.read_bytes())
	reservation = reserve_makou_field_bin_space(image)
	makou = verify_makou_preconditions(image)
	reference = edc_reference.read_bytes()
	repaired = repair_changed_edc_ecc(image, reference)
	verified = verify_changed_edc_ecc(image, reference)
	bounds = verify_disc_bounds(image)
	layout = verify_iso_layout(image)

	write_new(output_image, bytes(image))
	write_new(output_image.with_suffix(".cue"), cue_for(output_image))
	report = {
		"stage": "stabilize-working-bin",
		"input": str(input_image),
		"inputSha256": sha256(input_image),
		"tableBaseline": str(table_baseline),
		"tableBaselineSha256": sha256(table_baseline),
		"edcReference": str(edc_reference),
		"output": str(output_image),
		"outputSha256": sha256(output_image),
		"tableEntriesPatched": table_patches,
		"fieldBinReservation": reservation,
		"makouPreconditions": makou,
		"edcEccSectorsRepaired": repaired,
		"edcEccSectorsVerified": verified,
		"discBounds": bounds,
		"isoLayout": layout,
	}
	write_json(report_path, report)
	return report


def build_release_artifacts(
	*,
	input_image: Path,
	layer_base: Path,
	edc_reference: Path,
	output_dir: Path,
	pack_id: str,
	name: str,
	version: str,
	compatible_bases: list[str],
	disc: int = 1,
	blurb: str = "",
) -> dict:
	"""Create a pack and require its layer to reconstruct the release image exactly."""
	for required in (input_image, layer_base, edc_reference):
		if not required.is_file():
			raise SystemExit(f"Missing input: {required}")
	if output_dir.exists():
		raise SystemExit(f"Output directory already exists: {output_dir}")

	image = bytearray(input_image.read_bytes())
	reference = edc_reference.read_bytes()
	repaired = repair_changed_edc_ecc(image, reference)
	verified = verify_changed_edc_ecc(image, reference)
	bounds = verify_disc_bounds(image)
	layout = verify_iso_layout(image)

	release_image = output_dir / "image" / f"{pack_id}-disc{disc}.bin"
	write_new(release_image, bytes(image))
	write_new(release_image.with_suffix(".cue"), cue_for(release_image))
	layer = build_layer(
		layer_base,
		release_image,
		layer_id=f"{pack_id}-{version}-disc{disc}",
		description=f"{name} {version}",
	)
	pack_dir = output_dir / "pack" / pack_id
	layer_path = pack_dir / "layers" / f"disc{disc}.layer.json"
	write_json(layer_path, layer)

	round_trip = bytearray(layer_base.read_bytes())
	apply_layer(round_trip, layer)
	# ic-layer-v1 has no source-byte assertions, so generation success alone
	# cannot detect a wrong parent. Exact round-trip reconstruction makes the
	# declared layer base an enforced release invariant.
	if round_trip != image:
		raise SystemExit("Release layer round-trip failed")
	rebuilt_image = output_dir / "verification" / f"builder-rebuild-disc{disc}.bin"
	write_new(rebuilt_image, bytes(round_trip))
	write_new(rebuilt_image.with_suffix(".cue"), cue_for(rebuilt_image))

	if not compatible_bases:
		raise SystemExit("A mod release requires at least one --compatible-base")
	pack = {
		"id": pack_id,
		"name": name,
		"kind": "mod",
		"version": version,
		"format": "ic-layer-v1",
		"compatibleBases": compatible_bases,
		"discs": {str(disc): f"./layers/disc{disc}.layer.json"},
	}
	if blurb:
		pack["blurb"] = blurb
	write_json(pack_dir / "pack.json", pack)
	write_new(pack_dir / "VERSION", (version + "\n").encode())

	report = {
		"stage": "build-release-artifacts",
		"input": str(input_image),
		"layerBase": str(layer_base),
		"releaseImage": str(release_image),
		"releaseImageSha256": sha256(release_image),
		"pack": str(pack_dir),
		"layer": str(layer_path),
		"layerRoundTrip": "pass",
		"builderRebuildImage": str(rebuilt_image),
		"builderRebuildSha256": sha256(rebuilt_image),
		"edcEccSectorsRepaired": repaired,
		"edcEccSectorsVerified": verified,
		"discBounds": bounds,
		"isoLayout": layout,
	}
	write_json(output_dir / "stage-report.json", report)
	return report
