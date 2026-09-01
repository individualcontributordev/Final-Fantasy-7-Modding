#!/usr/bin/env python3
"""Build an editable, publishable CSR+ Disc 1 without hiding intermediate steps.

The build is split into two commands:

  python3 mods/single-disc/scripts/build_csrplus_staged.py prepare
  # Edit 03-working/CSRPLUS_D1.bin in Makou Reactor and save a new file.
  python3 mods/single-disc/scripts/build_csrplus_staged.py finalize \
    --run-dir ../Final-Fantasy-7-CSR/build/csr-plus/<run> \
    --edited-image /path/to/makou-saved.bin

Every output is written below Final-Fantasy-7-CSR/build/, which is gitignored.
Nothing under either repository's published builder/ tree is changed.

The same work can be run one artifact boundary at a time with:
  csrplus_stage_1_sources.py
  csrplus_stage_2_collapse.py
  single_disc_stage_3_working.py
  stabilize_working_bin.py
  csrplus_stage_5_snova.py
  single_disc_stage_6_endings.py
  build_release_artifacts.py

Disc 2 and Disc 3 layers cannot be applied byte-for-byte to Disc 1: their ISO
files live at different absolute offsets. This pipeline reconstructs each disc,
then moves selected FIELD files by ISO path into the collapsed Disc 1 image.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(SCRIPT_DIR))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from disc_sources import csr_root as default_csr_root  # noqa: E402
from edc_ecc import repair_sector_edc_ecc  # noqa: E402
from fix_field_bin_table import _dir_entries, fix_bin_table, fix_field_and_world_bins  # noqa: E402
from fix_junair_air0_slot3 import fix_junair  # noqa: E402
from merge_rework_fields import SLOT_SPLICE_FIELDS, WHOLE_FILE_FIELDS, merge_slots  # noqa: E402
from merge_safe_fields import find_safe_whole_file_merges  # noqa: E402
from psx_mode2_iso import (  # noqa: E402
    SECTOR,
    USER,
    _patch_dirent_size_only,
    _u32_le,
    _user,
    _write_user,
    extract_file,
    find_file,
    replace_file_within_sectors,
)
from pipeline_cache import (  # noqa: E402
    archive_path,
    cached_artifacts,
    cached_output,
    load_report,
)
from verify_iso_integrity import sector_count, walk_tree  # noqa: E402

SCENE_SOURCE_REF = "ec1d4ca"
HISTORICAL_CSR_LAYER = "builder/csr-v0.14.1/layers/disc{disc}.layer.json"
CURRENT_CSR_LAYER = "builder/csr/layers/disc{disc}.layer.json"

# ec1d4ca is the last CSR commit where every independent scene layer existed
# together. Keeping these inputs separate makes the collapsed base rebuildable
# without using the already-collapsed csr-plus layer as its own source.
SCENES = (
    {
        "id": "aerith-house-v0.1.1",
        "disc": 1,
        "layer": "builder/csr-plus-scene-aerith-house-v0.1.1/layers/disc1.layer.json",
        "files": ("FIELD/EALS_1.DAT",),
    },
    {
        "id": "cota-v0.1.0",
        "disc": 2,
        "layer": "builder/csr-plus-scene-cota-fd-manip-v0.1.0/layers/disc2.layer.json",
        "files": ("FIELD/BLIN70_4.DAT", "FIELD/LOSLAKE1.DAT"),
    },
    {
        "id": "hojo-v0.1.0",
        "disc": 2,
        "layer": "builder/csr-plus-scene-hojo-fd-manip-v0.1.0/layers/disc2.layer.json",
        "files": ("FIELD/BLIN66_6.DAT", "FIELD/CANON_2.DAT", "FIELD/FSHIP_24.DAT"),
    },
    {
        "id": "endgame-v0.1.0",
        "disc": 3,
        "layer": "builder/csr-plus-scene-endgame-fd-manip-v0.1.0/layers/disc3.layer.json",
        "files": (
            "FIELD/LAS0_3.DAT",
            "FIELD/LAS4_0.DAT",
            "FIELD/LAS2_1.DAT",
            "FIELD/LAS4_1.DAT",
        ),
    },
)


def write_new(path: Path, data: bytes) -> None:
    if path.exists():
        raise SystemExit(f"Refusing to overwrite build artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, value: object) -> None:
    write_new(path, (json.dumps(value, indent=2) + "\n").encode())


def copy_new(source: Path, destination: Path) -> None:
    if destination.exists():
        raise SystemExit(f"Refusing to overwrite build artifact: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def git_json_at_ref(csr: Path, git_ref: str, repo_path: str) -> dict:
    """Read a retired layer without restoring it to the live builder catalog.

    Collapsed bases need the former multi-disc and scene-specific layers as
    source material. Reading a pinned commit makes the provenance reproducible
    while keeping those obsolete packs unavailable to players.
    """
    command = ["git", "-C", str(csr), "show", f"{git_ref}:{repo_path}"]
    result = subprocess.run(command, capture_output=True)
    if result.returncode:
        detail = result.stderr.decode(errors="replace").strip()
        raise SystemExit(f"Cannot read historical build input {repo_path}: {detail}")
    return json.loads(result.stdout)


def git_json(csr: Path, repo_path: str) -> dict:
    return git_json_at_ref(csr, SCENE_SOURCE_REF, repo_path)


def pristine(csr: Path, disc: int) -> Path:
    path = csr / "pristine" / f"FINALFANTASY7_D{disc}.bin"
    if not path.is_file():
        raise SystemExit(f"Missing pristine disc: {path}")
    return path


def configure_sources(csr: Path) -> None:
    os.environ["FF7_CSR_ROOT"] = str(csr)
    os.environ["FF7_PRISTINE_DIR"] = str(csr / "pristine")


def apply_layer_file(image: bytearray, path: Path) -> None:
    apply_layer(image, json.loads(path.read_text(encoding="utf-8")))


def materialize_inputs(csr: Path, run_dir: Path) -> dict[str, Path]:
    inputs = run_dir / "00-inputs"
    paths: dict[str, Path] = {}

    for disc in (1, 2, 3):
        current = csr / CURRENT_CSR_LAYER.format(disc=disc)
        if not current.is_file():
            raise SystemExit(f"Missing current CSR layer: {current}")
        destination = inputs / "current-csr" / f"disc{disc}.layer.json"
        copy_new(current, destination)
        paths[f"current-{disc}"] = destination

        historical = git_json(csr, HISTORICAL_CSR_LAYER.format(disc=disc))
        destination = inputs / "historical-csr-v0.14.1" / f"disc{disc}.layer.json"
        write_json(destination, historical)
        paths[f"historical-{disc}"] = destination

    for scene in SCENES:
        layer = git_json(csr, scene["layer"])
        destination = inputs / "scene-layers" / f"{scene['id']}.layer.json"
        write_json(destination, layer)
        paths[f"scene-{scene['id']}"] = destination

    source_manifest = {
        "sceneSourceCommit": SCENE_SOURCE_REF,
        "pristine": {
            str(disc): {
                "path": str(pristine(csr, disc)),
                "sha256": sha256(pristine(csr, disc)),
            }
            for disc in (1, 2, 3)
        },
        "currentCsrLayers": {
            str(disc): {
                "path": str(paths[f"current-{disc}"]),
                "sha256": sha256(paths[f"current-{disc}"]),
            }
            for disc in (1, 2, 3)
        },
        "scenes": list(SCENES),
    }
    write_json(inputs / "sources.json", source_manifest)
    return paths


def build_disc_set(
    csr: Path,
    run_dir: Path,
    inputs: dict[str, Path],
    layer_prefix: str,
    output_dir: str,
) -> None:
    for disc in (1, 2, 3):
        image = bytearray(pristine(csr, disc).read_bytes())
        apply_layer_file(image, inputs[f"{layer_prefix}-{disc}"])
        write_new(
            run_dir / output_dir / f"FINALFANTASY7_D{disc}.bin",
            bytes(image),
        )


def fix_tables_for_disc(image: bytearray, baseline: bytes) -> int:
    total = 0
    for directory, bin_path, skip_name in (
        ("FIELD", "FIELD/FIELD.BIN", "FIELD.BIN"),
        ("WORLD", "WORLD/WORLD.BIN", "WORLD.BIN"),
    ):
        entries = _dir_entries(bytes(image), directory)
        baseline_sizes = {
            name: size
            for name, _lba, size, is_dir in _dir_entries(baseline, directory)
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


def build_trimmed_discs(
    run_dir: Path,
    inputs: dict[str, Path],
) -> None:
    historical_dir = run_dir / "02-historical-csr"
    historical_trimmed_dir = run_dir / "03-historical-csr-plus-trims"
    current_dir = run_dir / "01-current-csr"
    current_trimmed_dir = run_dir / "04-current-csr-plus-trims"

    for disc in (1, 2, 3):
        historical = bytearray(
            (historical_dir / f"FINALFANTASY7_D{disc}.bin").read_bytes()
        )
        for scene in SCENES:
            if scene["disc"] == disc:
                apply_layer_file(historical, inputs[f"scene-{scene['id']}"])
        write_new(
            historical_trimmed_dir / f"FINALFANTASY7_D{disc}.bin",
            bytes(historical),
        )

        current_path = current_dir / f"FINALFANTASY7_D{disc}.bin"
        current_bytes = current_path.read_bytes()
        current = bytearray(current_bytes)
        for scene in SCENES:
            if scene["disc"] != disc:
                continue
            for file_path in scene["files"]:
                payload = extract_file(historical, file_path)
                replace_file_within_sectors(current, file_path, payload)
                if extract_file(current, file_path) != payload:
                    raise SystemExit(f"Trim injection did not round-trip: {file_path}")

        fix_tables_for_disc(current, current_bytes)
        trimmed_path = current_trimmed_dir / f"FINALFANTASY7_D{disc}.bin"
        write_new(trimmed_path, bytes(current))

        layer = build_layer(
            current_path,
            trimmed_path,
            layer_id=f"csr-plus-trims-disc{disc}",
            description=f"CSR+ scene trims on current CSR Disc {disc}",
        )
        layer_path = run_dir / "05-current-trim-layers" / f"disc{disc}.layer.json"
        write_json(layer_path, layer)
        check = bytearray(current_bytes)
        apply_layer(check, layer)
        if check != current:
            raise SystemExit(f"Trim layer round-trip failed for Disc {disc}")


def save_stage(output_dir: Path, name: str, image: bytearray) -> Path:
    path = output_dir / name
    write_new(path, bytes(image))
    return path


def apply_manual_blackbgb(image: bytearray, layer_json: Path) -> None:
    """Apply the committed BLACKBGB DSKCG-removal layer to FIELD/BLACKBGB.DAT."""
    layer = json.loads(layer_json.read_text(encoding="utf-8"))
    current = extract_file(image, "FIELD/BLACKBGB.DAT")
    data = bytearray(current)
    for rec in layer["records"]:
        offset = rec["offset"]
        chunk = bytes.fromhex(rec["hex"])
        data[offset : offset + len(chunk)] = chunk
    data = bytes(data)
    if data != current:
        replace_file_within_sectors(image, "FIELD/BLACKBGB.DAT", data)


def collapse_to_disc1(sources_dir: Path, output_dir: Path) -> Path:
    current_dir = sources_dir / "01-current-csr"
    trimmed_dir = sources_dir / "04-current-csr-plus-trims"
    c1 = current_dir.joinpath("FINALFANTASY7_D1.bin").read_bytes()
    c2 = current_dir.joinpath("FINALFANTASY7_D2.bin").read_bytes()
    c3 = current_dir.joinpath("FINALFANTASY7_D3.bin").read_bytes()
    image = bytearray(c1)
    save_stage(output_dir, "01-csr-disc1.bin", image)

    for field, disc in WHOLE_FILE_FIELDS.items():
        source = c1 if disc == 1 else c2
        replace_file_within_sectors(image, f"FIELD/{field}.DAT", extract_file(source, f"FIELD/{field}.DAT"))
    for field, slot_discs in SLOT_SPLICE_FIELDS.items():
        merge_slots(image, field, slot_discs, c1, c2)
    save_stage(output_dir, "02-rework-fields.bin", image)

    safe_merges = find_safe_whole_file_merges()
    sources = {2: c2, 3: c3}
    for field, disc in sorted(safe_merges.items()):
        file_path = f"FIELD/{field}.DAT"
        payload = extract_file(sources[disc], file_path)
        if payload != extract_file(image, file_path):
            replace_file_within_sectors(image, file_path, payload)
    save_stage(output_dir, "03-safe-d2-d3-fields.bin", image)

    del c1, c2, c3, sources
    fix_junair(image)
    blackbgb = ROOT / "mods/single-disc/patches/BLACKBGB.dskcg-removal.layer.json"
    apply_manual_blackbgb(image, blackbgb)
    save_stage(output_dir, "04-precision-patches.bin", image)

    for scene in SCENES:
        source = trimmed_dir / f"FINALFANTASY7_D{scene['disc']}.bin"
        source_image = source.read_bytes()
        for file_path in scene["files"]:
            payload = extract_file(source_image, file_path)
            replace_file_within_sectors(image, file_path, payload)
    save_stage(output_dir, "05-all-scene-trims.bin", image)

    patched = fix_field_and_world_bins(image)
    print(f"Embedded FIELD/WORLD table entries patched: {patched}")
    return save_stage(output_dir, "06-field-world-tables-fixed.bin", image)


def makou_compressed_size(image: bytes | bytearray) -> int:
    raw = extract_file(image, "FIELD/FIELD.BIN")
    decompressed = gzip.decompress(raw[8:])
    # Makou/ff7tk uses zlib's default strategy at level 9.
    return 8 + len(gzip.compress(decompressed, compresslevel=9, mtime=0))


def makou_resize_probe_size(image: bytes | bytearray) -> int:
    raw = extract_file(image, "FIELD/FIELD.BIN")
    decompressed = bytearray(gzip.decompress(raw[8:]))
    eals = next(
        (entry for entry in _dir_entries(bytes(image), "FIELD") if entry[0] == "EALS_1.DAT"),
        None,
    )
    if eals is None:
        raise SystemExit("FIELD/EALS_1.DAT not found for Makou resize probe")
    _name, lba, size, _is_dir = eals
    key = struct.pack("<II", lba, size)
    offset = decompressed.find(key)
    if offset < 0:
        raise SystemExit("EALS_1 lookup entry missing for Makou resize probe")
    struct.pack_into("<I", decompressed, offset + 4, size + 1)
    return 8 + len(gzip.compress(decompressed, compresslevel=9, mtime=0))


def reserve_makou_field_bin_space(image: bytearray) -> dict:
    meta = find_file(image, "FIELD/FIELD.BIN")
    field_entries = sorted(
        (lba, name)
        for name, lba, _size, is_dir in _dir_entries(bytes(image), "FIELD")
        if not is_dir and lba > meta.lba
    )
    next_lba = field_entries[0][0] if field_entries else len(image) // SECTOR
    available_sectors = next_lba - meta.lba
    required_sectors = (makou_compressed_size(image) + USER - 1) // USER
    current_sectors = (meta.size + USER - 1) // USER
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
    return {
        "lba": meta.lba,
        "nextFileLba": next_lba,
        "makouCompressedBytes": makou_compressed_size(image),
        "reservedBytes": reserved_size,
        "headroomBytes": reserved_size - makou_compressed_size(image),
    }


def is_mode2_form1(sector: bytes | bytearray) -> bool:
    valid_sync = sector[0] == 0 and sector[11] == 0
    valid_header = sector[15] == 2 and all(value == 0xFF for value in sector[1:11])
    is_form1 = not (sector[18] & 0x20)
    return valid_sync and valid_header and is_form1


def repair_changed_edc_ecc(image: bytearray, retail: bytes) -> int:
    repaired = 0
    for sector_number in range(len(image) // SECTOR):
        offset = sector_number * SECTOR
        sector = image[offset : offset + SECTOR]
        if sector_number * SECTOR < len(retail):
            retail_sector = retail[offset : offset + SECTOR]
            if sector == retail_sector:
                continue
        if not is_mode2_form1(sector):
            continue
        repair_sector_edc_ecc(sector)
        image[offset : offset + SECTOR] = sector
        repaired += 1
    return repaired


def verify_changed_edc_ecc(image: bytes | bytearray, retail: bytes) -> int:
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
    if len(image) % SECTOR:
        raise SystemExit(f"Image is not MODE2/2352 sector-aligned: {len(image)}")
    actual_sectors = len(image) // SECTOR
    declared_sectors = _u32_le(_user(image, 16), 80)
    if declared_sectors != actual_sectors:
        raise SystemExit(
            f"PVD volume size mismatch: declared {declared_sectors}, actual {actual_sectors}"
        )
    cd_80_minute_sectors = 80 * 60 * 75
    if actual_sectors >= cd_80_minute_sectors:
        raise SystemExit(
            f"Image exceeds 80-minute CD limit: {actual_sectors} sectors"
        )
    return {
        "sectors": actual_sectors,
        "pvdVolumeSectors": declared_sectors,
        "under80MinuteCdLimit": True,
    }


# The ending alias deliberately parks the truncated ENDING2E stream inside an
# existing MOVIE/ slot, so that slot's extent runs into the file behind it.
# That single overlap is the intended design; any other overlap still fails.
ENDING_ALIAS_OVERLAPS = frozenset({("MOVIE/NVLMK.MOV", "MOVIE/MONITOR.STR")})


def verify_iso_layout(
    image: bytes | bytearray,
    allowed_overlaps: frozenset[tuple[str, str]] = frozenset(),
) -> dict:
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
    bad_field_keys = []
    field_bin = gzip.decompress(extract_file(image, "FIELD/FIELD.BIN")[8:])
    for name, lba, size, is_dir in _dir_entries(bytes(image), "FIELD"):
        if is_dir or name.endswith(".X") or name == "FIELD.BIN":
            continue
        key = struct.pack("<II", lba, size)
        count = field_bin.count(key)
        after_start = field_bin[0x30000:].count(key)
        if count != 1 and not (count > 1 and after_start == 1):
            bad_field_keys.append(name)

    yamada = extract_file(image, "INIT/YAMADA.BIN")
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
        expected_lba, expected_size = struct.unpack_from("<II", yamada, index * 8)
        actual = find_file(image, file_path)
        if (actual.lba, actual.size) != (expected_lba, expected_size):
            bad_yamada.append(file_path)

    field_meta = find_file(image, "FIELD/FIELD.BIN")
    compressed_size = makou_compressed_size(image)
    resize_probe_size = makou_resize_probe_size(image)
    largest_probe = max(compressed_size, resize_probe_size)
    headroom = field_meta.size - largest_probe
    if bad_field_keys or bad_yamada or headroom < 2 * USER:
        raise SystemExit(
            "Makou precondition failure: "
            f"fieldKeys={bad_field_keys}, yamada={bad_yamada}, headroom={headroom}"
        )
    return {
        "fieldLookupKeys": "pass",
        "yamadaReferences": "pass",
        "makouLevel9CompressedBytes": compressed_size,
        "makouOneByteResizeProbeBytes": resize_probe_size,
        "fieldBinAllocatedBytes": field_meta.size,
        "fieldBinHeadroomAfterResizeProbeBytes": headroom,
    }


def cue_for(bin_path: Path) -> bytes:
    text = f'FILE "{bin_path.name}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'
    return text.encode()


def build_source_artifacts(csr: Path, output_dir: Path) -> dict:
    csr = csr.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    configure_sources(csr)
    if output_dir.exists():
        raise SystemExit(f"Output directory already exists: {output_dir}")
    output_dir.mkdir(parents=True)

    inputs = materialize_inputs(csr, output_dir)
    build_disc_set(csr, output_dir, inputs, "current", "01-current-csr")
    build_disc_set(csr, output_dir, inputs, "historical", "02-historical-csr")
    build_trimmed_discs(output_dir, inputs)

    # Collapse only reads these six reconstructed discs. Recording their
    # hashes makes the expensive source stage reusable without trusting that
    # files merely exist.
    cache_paths = [
        Path(directory) / f"FINALFANTASY7_D{disc}.bin"
        for directory in ("01-current-csr", "04-current-csr-plus-trims")
        for disc in (1, 2, 3)
    ]
    report = {
        "stage": "csrplus-sources",
        "outputDir": str(output_dir),
        "currentCsrDiscs": str(output_dir / "01-current-csr"),
        "historicalCsrDiscs": str(output_dir / "02-historical-csr"),
        "historicalTrimmedDiscs": str(output_dir / "03-historical-csr-plus-trims"),
        "currentTrimmedDiscs": str(output_dir / "04-current-csr-plus-trims"),
        "trimLayers": str(output_dir / "05-current-trim-layers"),
        "cacheArtifacts": {
            str(path): sha256(output_dir / path) for path in cache_paths
        },
    }
    write_json(output_dir / "stage-report.json", report)
    return report


def stabilize_working_image(
    *,
    input_image: Path,
    table_baseline: Path,
    edc_reference: Path,
    output_image: Path,
    report_path: Path,
) -> dict:
    for required in (input_image, table_baseline, edc_reference):
        if not required.is_file():
            raise SystemExit(f"Missing input: {required}")

    image = bytearray(input_image.read_bytes())
    baseline = table_baseline.read_bytes()
    table_patches = fix_tables_for_disc(image, baseline)
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


def inject_snova_image(
    *,
    input_image: Path,
    disc3: Path,
    output_image: Path,
    report_path: Path,
) -> dict:
    for required in (input_image, disc3):
        if not required.is_file():
            raise SystemExit(f"Missing input: {required}")
    copy_new(input_image, output_image)
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "inject_snova_d3_to_d1.py"),
            "--d1",
            str(output_image),
            "--d3",
            str(disc3),
            "--in-place",
        ],
        check=True,
        cwd=ROOT,
    )
    image = output_image.read_bytes()
    report = {
        "stage": "inject-snova",
        "input": str(input_image),
        "disc3": str(disc3),
        "output": str(output_image),
        "outputSha256": sha256(output_image),
        "discBounds": verify_disc_bounds(image),
        "isoLayout": verify_iso_layout(image),
    }
    write_json(report_path, report)
    return report


def inject_ending_alias_image(
    *,
    input_image: Path,
    disc3: Path,
    edc_reference: Path,
    output_image: Path,
    report_path: Path,
) -> dict:
    """Place the truncated Disc 3 ENDING2E stream at its absolute D3 LBA.

    This runs *before* the publish layer is diffed. The post-battle sequence
    seeks a hardcoded D3 LBA, so the ending only plays if those sectors exist
    on the collapsed Disc 1 image — which means the bytes have to be part of
    the published layer, exactly like the SNOVA files. Building the layer from
    a pre-alias image would hand builder users a disc that cannot play its own
    ending.
    """
    for required in (input_image, disc3, edc_reference):
        if not required.is_file():
            raise SystemExit(f"Missing input: {required}")
    copy_new(input_image, output_image)
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "alias_d3_ending_lbas_on_d1.py"),
            "--d1",
            str(output_image),
            "--d3",
            str(disc3),
            "--in-place",
        ],
        check=True,
        cwd=ROOT,
    )
    # The aliaser rewrites dirents and MOVIE_ID rows with plain byte writes,
    # so their sectors need fresh Form 1 footers before anything is published.
    image = bytearray(output_image.read_bytes())
    reference = edc_reference.read_bytes()
    repaired = repair_changed_edc_ecc(image, reference)
    output_image.write_bytes(image)
    report = {
        "stage": "inject-ending-alias",
        "input": str(input_image),
        "disc3": str(disc3),
        "output": str(output_image),
        "outputSha256": sha256(output_image),
        "edcEccSectorsRepaired": repaired,
        "edcEccSectorsVerified": verify_changed_edc_ecc(bytes(image), reference),
        "discBounds": verify_disc_bounds(bytes(image)),
        "isoLayout": verify_iso_layout(bytes(image), ENDING_ALIAS_OVERLAPS),
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
    kind: str,
    compatible_bases: list[str],
    disc: int = 1,
    blurb: str = "",
    allowed_overlaps: frozenset[tuple[str, str]] = frozenset(),
) -> dict:
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
    layout = verify_iso_layout(image, allowed_overlaps)

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
    if round_trip != image:
        raise SystemExit("Release layer round-trip failed")
    rebuilt_image = output_dir / "verification" / f"builder-rebuild-disc{disc}.bin"
    write_new(rebuilt_image, bytes(round_trip))
    write_new(rebuilt_image.with_suffix(".cue"), cue_for(rebuilt_image))
    rebuilt_edc_verified = verify_changed_edc_ecc(round_trip, reference)

    pack = {
        "id": pack_id,
        "name": name,
        "kind": kind,
        "version": version,
        "format": "ic-layer-v1",
        "discs": {str(disc): f"./layers/disc{disc}.layer.json"},
    }
    if blurb:
        pack["blurb"] = blurb
    if kind == "base":
        pack["exclusiveGroup"] = "cutscenes"
    else:
        if not compatible_bases:
            raise SystemExit("A mod release requires at least one --compatible-base")
        pack["compatibleBases"] = compatible_bases
    write_json(pack_dir / "pack.json", pack)
    write_new(pack_dir / "VERSION", (version + "\n").encode())

    report = {
        "stage": "build-release-artifacts",
        "input": str(input_image),
        "layerBase": str(layer_base),
        "edcReference": str(edc_reference),
        "releaseImage": str(release_image),
        "releaseImageSha256": sha256(release_image),
        "pack": str(pack_dir),
        "layer": str(layer_path),
        "layerRoundTrip": "pass",
        "builderRebuildImage": str(rebuilt_image),
        "builderRebuildSha256": sha256(rebuilt_image),
        "builderRebuildEdcEccSectorsVerified": rebuilt_edc_verified,
        "edcEccSectorsRepaired": repaired,
        "edcEccSectorsVerified": verified,
        "discBounds": bounds,
        "isoLayout": layout,
        "hardwareValidation": "pending DuckStation, MiSTer, burn verify, and console playtest",
    }
    write_json(output_dir / "stage-report.json", report)
    return report


def write_collapse_cache_report(
    *,
    stage: str,
    sources_dir: Path,
    output: Path,
    report_path: Path,
) -> dict:
    image = output.read_bytes()
    report = {
        "stage": stage,
        "sourcesDir": str(sources_dir),
        "output": str(output),
        "outputSha256": sha256(output),
        "discBounds": verify_disc_bounds(image),
        "isoLayout": verify_iso_layout(image),
    }
    write_json(report_path, report)
    return report


def cached_or_adopted_collapse(
    *,
    stage: str,
    sources_dir: Path,
    collapse_dir: Path,
    output: Path,
) -> tuple[bool, dict | None]:
    report_path = collapse_dir / "stage-report.json"
    valid, report, reason = cached_output(
        report_path=report_path,
        output_path=output,
        sha256_file=sha256,
    )
    if valid:
        print(f"[cache] 02-collapse: {reason}")
        return True, report
    if report_path.exists() or not output.is_file():
        print(f"[cache] 02-collapse: {reason}")
        return False, report

    # Older CSR+ runs did not write a collapse report. Validate the immutable
    # checkpoint structurally once, then record its hash for future resumes.
    report = write_collapse_cache_report(
        stage=stage,
        sources_dir=sources_dir,
        output=output,
        report_path=report_path,
    )
    print("[cache] 02-collapse: adopted legacy artifact after full structural validation")
    return True, report


def write_prepare_report(
    *,
    run_dir: Path,
    working_image: Path,
    sources_report: dict,
    collapse_report: dict,
    working_report: dict,
) -> None:
    report = {
        "runDir": str(run_dir),
        "workingImage": str(working_image),
        "workingSha256": working_report["outputSha256"],
        "sources": sources_report,
        "collapse": collapse_report,
        "working": working_report,
        "next": (
            "Edit 03-working/CSRPLUS_D1.bin in Makou Reactor, save as a new file, "
            "then run the finalize command printed below."
        ),
    }
    old_report = run_dir / "prepare-report.json"
    archive_path(old_report, run_dir)
    write_json(old_report, report)


def prepare(args: argparse.Namespace) -> None:
    csr = args.csr_root.expanduser().resolve()
    configure_sources(csr)
    run_name = args.run_name or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = csr / "build" / "csr-plus" / run_name
    # Top-level numbers are the operator stages, matching Highwind:
    # 01-sources, 02-collapse, 03-working, then finalize's 04/05/06.
    # Nested 00–05 folders live inside 01-sources, not as siblings of the
    # working BIN.
    sources_dir = run_dir / "01-sources"
    collapse_dir = run_dir / "02-collapse"
    working_dir = run_dir / "03-working"
    collapsed = collapse_dir / "06-field-world-tables-fixed.bin"
    working_image = working_dir / "CSRPLUS_D1.bin"

    if run_dir.exists() and not (args.resume or args.rebuild_from):
        raise SystemExit(
            f"Build run already exists: {run_dir}\n"
            "Use --resume to reuse verified stages, or --rebuild-from "
            "sources|collapse|working to force a stage and everything after it."
        )

    rebuild_from = args.rebuild_from
    if rebuild_from:
        stage_names = ("sources", "collapse", "working")
        first = stage_names.index(rebuild_from)
        stage_dirs = {
            "sources": sources_dir,
            "collapse": collapse_dir,
            "working": working_dir,
        }
        for stage_name in reversed(stage_names[first:]):
            archived = archive_path(stage_dirs[stage_name], run_dir)
            if archived:
                print(f"[recovery] preserved {stage_name} at {archived}")

    sources_valid, sources_report, sources_reason = cached_artifacts(
        report_path=sources_dir / "stage-report.json",
        stage_dir=sources_dir,
        sha256_file=sha256,
    )
    collapse_valid, collapse_report = cached_or_adopted_collapse(
        stage="csrplus-collapse",
        sources_dir=sources_dir,
        collapse_dir=collapse_dir,
        output=collapsed,
    )
    working_valid, working_report, working_reason = cached_output(
        report_path=working_dir / "stage-report.json",
        output_path=working_image,
        sha256_file=sha256,
    )

    if working_valid and not rebuild_from:
        print(f"[cache] 03-working: {working_reason}")
        print(f"\nMakou-safe CSR+ image: {working_image}")
        return

    if not collapse_valid:
        if not sources_valid:
            if sources_dir.exists():
                raise SystemExit(
                    f"Cannot safely reuse 01-sources: {sources_reason}\n"
                    "Run again with --rebuild-from sources. Existing artifacts "
                    "will be preserved under recovery/."
                )
            sources_report = build_source_artifacts(csr, sources_dir)
        else:
            print(f"[cache] 01-sources: {sources_reason}")
        archive_path(collapse_dir, run_dir)
        archive_path(working_dir, run_dir)
        collapsed = collapse_to_disc1(sources_dir, collapse_dir)
        collapse_report = write_collapse_cache_report(
            stage="csrplus-collapse",
            sources_dir=sources_dir,
            output=collapsed,
            report_path=collapse_dir / "stage-report.json",
        )
    else:
        print("[cache] 02-collapse: reusable")
        if sources_report is None:
            sources_report = load_report(sources_dir / "stage-report.json") or {}

    if working_dir.exists():
        archived = archive_path(working_dir, run_dir)
        print(f"[recovery] preserved changed 03-working at {archived}")

    working_image = run_dir / "03-working" / "CSRPLUS_D1.bin"
    working_report = stabilize_working_image(
        input_image=collapsed,
        table_baseline=collapsed,
        edc_reference=pristine(csr, 1),
        output_image=working_image,
        report_path=run_dir / "03-working" / "stage-report.json",
    )
    write_prepare_report(
        run_dir=run_dir,
        working_image=working_image,
        sources_report=sources_report or {},
        collapse_report=collapse_report or {},
        working_report=working_report,
    )
    print(f"\nMakou-safe CSR+ image: {working_image}")
    print("Save Makou's result as a new file; do not overwrite this checkpoint.")
    print(
        f"{sys.executable} {Path(__file__).relative_to(ROOT)} finalize "
        f"--run-dir {run_dir} --edited-image /path/to/makou-saved.bin"
    )


def finalize(args: argparse.Namespace) -> None:
    run_dir = args.run_dir.expanduser().resolve()
    edited = args.edited_image.expanduser().resolve()
    if not run_dir.is_dir():
        raise SystemExit(f"Missing run directory: {run_dir}")
    if not edited.is_file():
        raise SystemExit(f"Missing edited image: {edited}")
    csr = args.csr_root.expanduser().resolve()
    configure_sources(csr)
    output_dir = run_dir / "04-finalize"
    if output_dir.exists():
        raise SystemExit(f"Finalize artifacts already exist: {output_dir}")

    working_baseline = run_dir / "03-working" / "CSRPLUS_D1.bin"
    baseline_valid, _baseline_report, baseline_reason = cached_output(
        report_path=run_dir / "03-working" / "stage-report.json",
        output_path=working_baseline,
        sha256_file=sha256,
    )
    if not baseline_valid:
        raise SystemExit(
            f"03-working is not the unchanged Makou baseline: {baseline_reason}\n"
            "Run prepare again with the same --run-name and --resume. The edited "
            "directory will be preserved under recovery/ before the baseline is rebuilt."
        )
    stabilized = output_dir / "01-makou-stabilized.bin"
    stabilize_report = stabilize_working_image(
        input_image=edited,
        table_baseline=working_baseline,
        edc_reference=pristine(csr, 1),
        output_image=stabilized,
        report_path=output_dir / "01-stage-report.json",
    )

    snova = output_dir / "02-snova-injected.bin"
    snova_report = inject_snova_image(
        input_image=stabilized,
        disc3=pristine(csr, 3),
        output_image=snova,
        report_path=output_dir / "02-stage-report.json",
    )

    publish_input = snova
    ending_report = None
    if args.ending_alias:
        endings = output_dir / "03-endings.bin"
        ending_report = inject_ending_alias_image(
            input_image=snova,
            disc3=pristine(csr, 3),
            edc_reference=pristine(csr, 1),
            output_image=endings,
            report_path=output_dir / "03-stage-report.json",
        )
        publish_input = endings

    publish_dir = run_dir / "05-release-candidate"
    release_report = build_release_artifacts(
        input_image=publish_input,
        layer_base=pristine(csr, 1),
        edc_reference=pristine(csr, 1),
        output_dir=publish_dir,
        pack_id="csr-plus",
        name="CSR+ (single-disc)",
        version=args.version,
        kind="base",
        compatible_bases=[],
        disc=1,
        blurb="CutScenes Removed plus scene trims, collapsed onto Disc 1.",
        allowed_overlaps=ENDING_ALIAS_OVERLAPS if args.ending_alias else frozenset(),
    )
    publish_source = Path(release_report["releaseImage"])
    layer_path = Path(release_report["layer"])
    retail = pristine(csr, 1).read_bytes()

    # The console image is a straight copy of the publish source, so the disc
    # you burn is byte-identical to what the builder site reconstructs.
    console_dir = run_dir / "06-console-check"
    console_bin = console_dir / "FINALFANTASY7_D1_CSRPLUS.bin"
    copy_new(publish_source, console_bin)
    write_new(console_bin.with_suffix(".cue"), cue_for(console_bin))
    console_image = console_bin.read_bytes()
    console_edc_verified = verify_changed_edc_ecc(console_image, retail)
    console_bounds = verify_disc_bounds(console_image)
    console_iso_layout = verify_iso_layout(
        console_image, ENDING_ALIAS_OVERLAPS if args.ending_alias else frozenset()
    )

    report = {
        "editedInput": str(edited),
        "stabilize": stabilize_report,
        "snova": snova_report,
        "endingAlias": ending_report,
        "endingAliasInPublishedLayer": bool(args.ending_alias),
        "release": release_report,
        "publishLayer": str(layer_path),
        "publishLayerRoundTrip": release_report["layerRoundTrip"],
        "consoleImage": str(console_bin),
        "consoleImageSha256": sha256(console_bin),
        "consoleEdcEccSectorsVerified": console_edc_verified,
        "consoleDiscBounds": console_bounds,
        "consoleIsoLayout": console_iso_layout,
        "automatedValidation": "pass",
        "hardwareValidation": "pending DuckStation, MiSTer, ImgBurn verify, and console playtest",
    }
    write_json(run_dir / "finalize-report.json", report)
    print(f"\nPublish candidate: {layer_path}")
    print(f"Console test image: {console_bin}")
    print("Automated checks passed; physical burn and console playtest remain required.")


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--csr-root",
        type=Path,
        default=default_csr_root(),
        help="Final-Fantasy-7-CSR repository",
    )
    commands = ap.add_subparsers(dest="command", required=True)

    prepare_command = commands.add_parser("prepare", help="Build all sources and a Makou-editable Disc 1")
    prepare_command.add_argument("--run-name", help="Build folder name (default: UTC timestamp)")
    prepare_mode = prepare_command.add_mutually_exclusive_group()
    prepare_mode.add_argument(
        "--resume",
        action="store_true",
        help="Reuse hash-verified stages and rebuild only the first changed output",
    )
    prepare_mode.add_argument(
        "--rebuild-from",
        choices=("sources", "collapse", "working"),
        help="Preserve then rebuild this stage and every later prepare stage",
    )
    prepare_command.set_defaults(action=prepare)

    finalize_command = commands.add_parser("finalize", help="Validate a Makou save and create publish artifacts")
    finalize_command.add_argument("--run-dir", type=Path, required=True)
    finalize_command.add_argument("--edited-image", type=Path, required=True)
    finalize_command.add_argument("--version", default="0.1.1")
    # On by default: the ending is part of the single-disc build, so it belongs
    # in the published layer or builder users get a disc without an ending.
    finalize_command.add_argument(
        "--no-ending-alias",
        dest="ending_alias",
        action="store_false",
        help="Skip the ENDING2E Disc 3 alias (publishes a disc with no ending movie)",
    )
    finalize_command.set_defaults(action=finalize)
    return ap


def main() -> None:
    args = parser().parse_args()
    args.action(args)


if __name__ == "__main__":
    main()
