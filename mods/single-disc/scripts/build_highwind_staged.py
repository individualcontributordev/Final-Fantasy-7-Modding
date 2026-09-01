#!/usr/bin/env python3
"""Build, edit, and package the collapsed Highwind base.

Highwind rebuilds the same Disc 1 collapse as CSR+ (CSR discs + scene trims),
then copies Highwind's extra early Disc 1 fields. It does not read the
published csr-plus pack.

Preferred Makou point is 03-working (collapsed, pre-SNOVA). Finalize
restabilizes, injects SNOVA, and writes a candidate layer.

Normal workflow:

  python3 mods/single-disc/scripts/build_highwind_staged.py prepare \
    --run-name my-highwind-edit

  # Open 03-working/HIGHWIND_D1.bin in Makou Reactor. Save to a new filename.

  python3 mods/single-disc/scripts/build_highwind_staged.py finalize \
    --run-dir ../Final-Fantasy-7-CSR/build/highwind/my-highwind-edit \
    --edited-image /path/to/makou-saved.bin \
    --version 0.2.1

This wrapper calls the same public functions as the individual stage scripts.
Use highwind_stage_1_sources.py, highwind_stage_2_collapse.py,
prepare_working_bin.py, stabilize_working_bin.py, csrplus_stage_5_snova.py,
and build_release_artifacts.py when you want to inspect every handoff.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from build_csrplus_staged import (
    ENDING_ALIAS_OVERLAPS,
    build_release_artifacts,
    configure_sources,
    copy_new,
    cue_for,
    default_csr_root,
    inject_ending_alias_image,
    inject_snova_image,
    pristine,
    sha256,
    stabilize_working_image,
    verify_changed_edc_ecc,
    verify_disc_bounds,
    verify_iso_layout,
    write_json,
    write_new,
)
from highwind_pipeline import (
    build_highwind_source_artifacts,
    collapse_highwind_disc1,
)


def prepare(args: argparse.Namespace) -> None:
    csr = args.csr_root.expanduser().resolve()
    configure_sources(csr)
    run_name = args.run_name or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = csr / "build" / "highwind" / run_name

    sources = build_highwind_source_artifacts(csr, run_dir / "01-sources")
    collapsed, collapse_report = collapse_highwind_disc1(
        run_dir / "01-sources",
        run_dir / "02-collapse",
    )
    working_image = run_dir / "03-working" / "HIGHWIND_D1.bin"
    working = stabilize_working_image(
        input_image=collapsed,
        table_baseline=collapsed,
        edc_reference=pristine(csr, 1),
        output_image=working_image,
        report_path=run_dir / "03-working" / "stage-report.json",
    )

    report = {
        "runDir": str(run_dir),
        "sources": sources,
        "collapse": collapse_report,
        "working": working,
        "next": (
            "Edit 03-working/HIGHWIND_D1.bin in Makou, save to a new file, "
            "then run this script's finalize command."
        ),
    }
    write_json(run_dir / "prepare-report.json", report)
    print(f"\nMakou-safe Highwind image: {working_image}")
    print("Keep this checkpoint unchanged and save Makou's result to a new file.")


def finalize(args: argparse.Namespace) -> None:
    csr = args.csr_root.expanduser().resolve()
    configure_sources(csr)
    run_dir = args.run_dir.expanduser().resolve()
    edited = args.edited_image.expanduser().resolve()
    if not run_dir.is_dir():
        raise SystemExit(f"Missing run directory: {run_dir}")
    if not edited.is_file():
        raise SystemExit(f"Missing Makou-saved image: {edited}")
    finalize_dir = run_dir / "04-finalize"
    if finalize_dir.exists():
        raise SystemExit(f"Finalize output already exists: {finalize_dir}")

    working_baseline = run_dir / "03-working" / "HIGHWIND_D1.bin"
    stabilized = finalize_dir / "01-stabilized.bin"
    stabilize_report = stabilize_working_image(
        input_image=edited,
        table_baseline=working_baseline,
        edc_reference=pristine(csr, 1),
        output_image=stabilized,
        report_path=finalize_dir / "01-stage-report.json",
    )

    # SNOVA appends a new directory and changes BATTLE.X. Keeping it after
    # Makou prevents the editor from repacking this custom end-of-disc layout.
    snova = finalize_dir / "02-snova.bin"
    snova_report = inject_snova_image(
        input_image=stabilized,
        disc3=pristine(csr, 3),
        output_image=snova,
        report_path=finalize_dir / "02-stage-report.json",
    )

    # Must precede the layer diff: the ending's Disc 3 sectors have to be in
    # the published layer, or builder-built discs cannot play their own ending.
    publish_input = snova
    ending_report = None
    if args.ending_alias:
        endings = finalize_dir / "03-endings.bin"
        ending_report = inject_ending_alias_image(
            input_image=snova,
            disc3=pristine(csr, 3),
            edc_reference=pristine(csr, 1),
            output_image=endings,
            report_path=finalize_dir / "03-stage-report.json",
        )
        publish_input = endings

    release_report = build_release_artifacts(
        input_image=publish_input,
        layer_base=pristine(csr, 1),
        edc_reference=pristine(csr, 1),
        output_dir=run_dir / "05-release-candidate",
        pack_id="highwind",
        name="Highwind",
        version=args.version,
        kind="base",
        compatible_bases=[],
        disc=1,
        blurb=(
            "Heavily shortened story, collapsed onto Disc 1. "
            "Many dialogue choices and scenes are cut."
        ),
        allowed_overlaps=ENDING_ALIAS_OVERLAPS if args.ending_alias else frozenset(),
    )

    # Straight copy of the publish source, so the burned disc and the
    # builder-site reconstruction are byte-identical.
    release_image = Path(release_report["releaseImage"])
    console_dir = run_dir / "06-console-check"
    console_image = console_dir / "FINALFANTASY7_D1_HIGHWIND.bin"
    copy_new(release_image, console_image)
    retail = pristine(csr, 1).read_bytes()
    write_new(console_image.with_suffix(".cue"), cue_for(console_image))

    console_bytes = console_image.read_bytes()
    report = {
        "editedInput": str(edited),
        "stabilize": stabilize_report,
        "snova": snova_report,
        "endingAlias": ending_report,
        "endingAliasInPublishedLayer": bool(args.ending_alias),
        "release": release_report,
        "consoleImage": str(console_image),
        "consoleImageSha256": sha256(console_image),
        "consoleEdcEccSectorsVerified": verify_changed_edc_ecc(console_bytes, retail),
        "consoleDiscBounds": verify_disc_bounds(console_bytes),
        "consoleIsoLayout": verify_iso_layout(
            console_bytes, ENDING_ALIAS_OVERLAPS if args.ending_alias else frozenset()
        ),
        "hardwareValidation": "pending DuckStation, MiSTer, burn verify, and console playtest",
    }
    write_json(run_dir / "finalize-report.json", report)
    print(f"\nCandidate pack: {release_report['pack']}")
    print(f"Builder reconstruction: {release_report['builderRebuildImage']}")
    print(f"Console test image: {console_image}")


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--csr-root", type=Path, default=default_csr_root())
    commands = parser.add_subparsers(dest="command", required=True)

    prepare_command = commands.add_parser(
        "prepare",
        help="Create a Makou-safe Highwind working BIN",
    )
    prepare_command.add_argument("--run-name")
    prepare_command.set_defaults(action=prepare)

    finalize_command = commands.add_parser(
        "finalize",
        help="Process a Makou save into release artifacts",
    )
    finalize_command.add_argument("--run-dir", type=Path, required=True)
    finalize_command.add_argument("--edited-image", type=Path, required=True)
    finalize_command.add_argument("--version", required=True)
    # On by default so the published layer always carries the ending sectors.
    finalize_command.add_argument(
        "--no-ending-alias",
        dest="ending_alias",
        action="store_false",
        help="Skip the ENDING2E Disc 3 alias (publishes a disc with no ending movie)",
    )
    finalize_command.set_defaults(action=finalize)
    return parser


def main() -> None:
    args = parser().parse_args()
    args.action(args)


if __name__ == "__main__":
    main()
