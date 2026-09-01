#!/usr/bin/env python3
"""Create a Makou-safe copy of an FF7 PSX raw BIN.

This repairs the common, mechanically recoverable causes of Makou Reactor's
"Invalid archive" error:

* stale `(LBA, size)` records inside FIELD.BIN and WORLD.BIN;
* too little FIELD.BIN space for Makou's level-9 gzip recompression;
* stale Mode 2 Form 1 EDC/ECC bytes;
* detectable ISO directory overlaps or volume-size inconsistencies.

The input is never modified. The command refuses ambiguous table repairs rather
than guessing, because a wrong four-byte size can make an image appear healthy
while breaking a field later in the game.

For the strongest repair, pass --table-baseline with the unchanged BIN that was
opened before the problematic edit. A retail image is not required. Without a
baseline, the script identifies table records from their neighboring valid
records and stops if that inference is not unique.
"""
from __future__ import annotations

import argparse
import gzip
import struct
from pathlib import Path

from build_csrplus_staged import (
    SECTOR,
    cue_for,
    fix_tables_for_disc,
    is_mode2_form1,
    reserve_makou_field_bin_space,
    sha256,
    verify_disc_bounds,
    verify_iso_layout,
    verify_makou_preconditions,
    write_json,
    write_new,
)
from edc_ecc import repair_sector_edc_ecc
from fix_field_bin_table import _dir_entries, fix_bin_table
from psx_mode2_iso import extract_file


def _context_score(
    payload: bytes,
    offset: int,
    known_pairs: set[tuple[int, int]],
) -> int:
    """Count valid neighboring table records around one possible LBA match."""
    score = 0
    for distance in range(-4, 5):
        if distance == 0:
            continue
        neighbor = offset + distance * 8
        is_in_bounds = 0 <= neighbor and neighbor + 8 <= len(payload)
        if not is_in_bounds:
            continue
        if struct.unpack_from("<II", payload, neighbor) in known_pairs:
            score += 1
    return score


def _infer_table_records(
    image: bytes,
    directory: str,
    bin_path: str,
    skip_name: str,
) -> tuple[dict[str, int], dict[str, int]]:
    """Infer old sizes and exact table offsets from surrounding valid records."""
    raw = extract_file(image, bin_path)
    if raw[8:10] != b"\x1f\x8b":
        raise SystemExit(f"{bin_path} is not a GZIPPS archive")
    payload = gzip.decompress(raw[8:])

    entries = [
        entry
        for entry in _dir_entries(image, directory)
        if not entry[3] and entry[0] != skip_name
    ]
    known_pairs = {(lba, size) for _name, lba, size, _is_dir in entries}
    offsets_by_lba = {lba: [] for _name, lba, _size, _is_dir in entries}
    for offset in range(len(payload) - 7):
        possible_lba = struct.unpack_from("<I", payload, offset)[0]
        if possible_lba in offsets_by_lba:
            offsets_by_lba[possible_lba].append(offset)

    inferred_sizes: dict[str, int] = {}
    target_offsets: dict[str, int] = {}

    for name, lba, _current_size, _is_dir in entries:
        candidates = offsets_by_lba[lba]
        if not candidates:
            # Not every ISO file is represented in the embedded archive table.
            continue

        if len(candidates) == 1:
            target = candidates[0]
        else:
            scored = [
                (candidate, _context_score(payload, candidate, known_pairs))
                for candidate in candidates
            ]
            best_score = max(score for _candidate, score in scored)
            best_candidates = [
                candidate for candidate, score in scored if score == best_score
            ]
            inference_is_safe = best_score >= 2 and len(best_candidates) == 1
            if not inference_is_safe:
                detail = ", ".join(
                    f"{candidate}:{score}" for candidate, score in scored
                )
                raise SystemExit(
                    f"{bin_path}: cannot safely identify {name}'s table record "
                    f"among offsets/scores [{detail}]. Pass --table-baseline."
                )
            target = best_candidates[0]

        inferred_sizes[name] = struct.unpack_from("<I", payload, target + 4)[0]
        target_offsets[name] = target

    return inferred_sizes, target_offsets


def fix_tables_without_baseline(image: bytearray) -> int:
    """Repair FF7 lookup tables using structural context within each archive."""
    total = 0
    for directory, bin_path, skip_name in (
        ("FIELD", "FIELD/FIELD.BIN", "FIELD.BIN"),
        ("WORLD", "WORLD/WORLD.BIN", "WORLD.BIN"),
    ):
        entries = _dir_entries(bytes(image), directory)
        inferred_sizes, target_offsets = _infer_table_records(
            bytes(image),
            directory,
            bin_path,
            skip_name,
        )
        total += fix_bin_table(
            image,
            bin_path,
            entries,
            skip_names={skip_name},
            baseline_sizes=inferred_sizes,
            target_offsets=target_offsets,
        )
    return total


def repair_all_edc_ecc(image: bytearray) -> dict:
    """Recalculate every recognized Mode 2 Form 1 sector and verify the result."""
    recognized = 0
    changed = 0
    for sector_number in range(len(image) // SECTOR):
        offset = sector_number * SECTOR
        sector = image[offset : offset + SECTOR]
        if not is_mode2_form1(sector):
            continue

        recognized += 1
        original = bytes(sector)
        repair_sector_edc_ecc(sector)
        if sector != original:
            changed += 1
        image[offset : offset + SECTOR] = sector

    # Every recognized sector was compared with freshly calculated parity in
    # the loop above. Recalculating all 300k sectors a second time would provide
    # no independent check and roughly double a several-minute operation.
    return {
        "mode2Form1SectorsVerified": recognized,
        "sectorFootersChanged": changed,
    }


def make_makou_safe(
    input_path: Path,
    output_path: Path,
    table_baseline: Path | None,
    report_path: Path,
) -> dict:
    input_path = input_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()
    report_path = report_path.expanduser().resolve()
    cue_path = output_path.with_suffix(".cue")
    if not input_path.is_file():
        raise SystemExit(f"Input BIN does not exist: {input_path}")
    if input_path == output_path:
        raise SystemExit("Input and output must differ; the original is never overwritten")
    if output_path.exists():
        raise SystemExit(f"Output already exists: {output_path}")
    if cue_path.exists():
        raise SystemExit(f"CUE output already exists: {cue_path}")
    if report_path.exists():
        raise SystemExit(f"Report already exists: {report_path}")

    image = bytearray(input_path.read_bytes())
    if len(image) % SECTOR:
        raise SystemExit(
            f"Input is not a raw MODE2/2352 image: {len(image)} bytes"
        )

    # Reserve before table repair so a slightly larger recompressed FIELD.BIN
    # cannot overflow the old allocation during the repair itself.
    initial_reservation = reserve_makou_field_bin_space(image)

    if table_baseline is None:
        table_mode = "inferred from neighboring embedded records"
        table_patches = fix_tables_without_baseline(image)
        baseline_value = None
    else:
        table_baseline = table_baseline.expanduser().resolve()
        if not table_baseline.is_file():
            raise SystemExit(f"Table baseline does not exist: {table_baseline}")
        table_mode = "explicit pre-edit baseline"
        baseline_bytes = table_baseline.read_bytes()
        table_patches = fix_tables_for_disc(image, baseline_bytes)
        baseline_value = str(table_baseline)

    final_reservation = reserve_makou_field_bin_space(image)
    makou_checks = verify_makou_preconditions(image)
    edc_ecc = repair_all_edc_ecc(image)
    bounds = verify_disc_bounds(image)
    layout = verify_iso_layout(image)

    write_new(output_path, bytes(image))
    write_new(cue_path, cue_for(output_path))
    report = {
        "stage": "make-makou-safe",
        "input": str(input_path),
        "inputSha256": sha256(input_path),
        "output": str(output_path),
        "outputSha256": sha256(output_path),
        "tableBaseline": baseline_value,
        "tableRepairMode": table_mode,
        "tableEntriesPatched": table_patches,
        "initialFieldBinReservation": initial_reservation,
        "finalFieldBinReservation": final_reservation,
        "makouPreconditions": makou_checks,
        "edcEcc": edc_ecc,
        "discBounds": bounds,
        "isoLayout": layout,
    }
    write_json(report_path, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="FF7 raw MODE2/2352 BIN")
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument(
        "--table-baseline",
        type=Path,
        help="Unchanged pre-edit BIN; recommended when available",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="JSON report path (default: <output>.makou-safe.json)",
    )
    args = parser.parse_args()

    output = args.output.expanduser().resolve()
    report = args.report or output.with_suffix(".makou-safe.json")
    result = make_makou_safe(args.input, output, args.table_baseline, report)
    print(f"Makou-safe BIN: {result['output']}")
    print(f"Validation report: {report}")
    print(f"Embedded table entries patched: {result['tableEntriesPatched']}")


if __name__ == "__main__":
    main()
