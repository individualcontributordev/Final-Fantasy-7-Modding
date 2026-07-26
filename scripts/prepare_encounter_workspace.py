#!/usr/bin/env python3
"""Copy pristine discs into iso-extract as disposable working images.

CDmage can auto-save on FIELD.BIN import. Keep retail masters only under
workspace/pristine/ and never open those for import.

  python scripts/prepare_encounter_workspace.py --discs 1
  python scripts/prepare_encounter_workspace.py --discs 1,2,3
  python scripts/prepare_encounter_workspace.py --discs 1 --force

Copies (bin + cue when present):
  workspace/pristine/FINALFANTASY7_DN.*
    → workspace/iso-extract/FINALFANTASY7_DN.*
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
PRISTINE = _ROOT / "workspace" / "pristine"
ISO = _ROOT / "workspace" / "iso-extract"
DISC_STEM = "FINALFANTASY7_D{disc}"


def parse_discs(spec: str) -> list[int]:
    discs: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        disc = int(part)
        if disc not in (1, 2, 3):
            raise SystemExit(f"Disc must be 1, 2, or 3 — got {disc}")
        discs.append(disc)
    if not discs:
        raise SystemExit("Pass at least one disc, e.g. --discs 1")
    return discs


def copy_one(src: Path, dest: Path, *, force: bool) -> None:
    if not src.is_file():
        raise SystemExit(f"Missing pristine: {src}")
    if dest.exists() and not force:
        raise SystemExit(
            f"Already exists: {dest}\n"
            "Delete it, or re-run with --force to replace the working copy.\n"
            "Do not use --force if that file is your only patched image."
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  {src.relative_to(_ROOT)} → {dest.relative_to(_ROOT)}")
    shutil.copy2(src, dest)
    if dest.stat().st_size != src.stat().st_size:
        raise SystemExit(f"Copy size mismatch for {dest.name}")


def prepare_disc(disc: int, *, force: bool) -> None:
    stem = DISC_STEM.format(disc=disc)
    print(f"\n=== Disc {disc}: refresh working copy ===")
    copy_one(PRISTINE / f"{stem}.bin", ISO / f"{stem}.bin", force=force)

    cue_src = PRISTINE / f"{stem}.cue"
    if cue_src.is_file():
        copy_one(cue_src, ISO / f"{stem}.cue", force=force)
    else:
        print(f"  (no {cue_src.name} — copy the .cue next to the pristine .bin)")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Copy pristine discs into iso-extract for CDmage work."
    )
    ap.add_argument(
        "--discs",
        required=True,
        help="Comma list, e.g. 1 or 1,2,3",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing working copies in iso-extract",
    )
    args = ap.parse_args()

    if not PRISTINE.is_dir():
        raise SystemExit(
            f"Missing {PRISTINE}\n"
            "Create it and place FINALFANTASY7_D1.bin … D3.bin (+ .cue) there."
        )

    discs = parse_discs(args.discs)
    print(f"Pristine vault: {PRISTINE}")
    print(f"Working dir:    {ISO}")
    print("Never open files under workspace/pristine/ in CDmage for import.")

    for disc in discs:
        prepare_disc(disc, force=args.force)

    print(
        "\nNext (per disc):\n"
        "  1. Open workspace/iso-extract/FINALFANTASY7_DN.cue in CDmage\n"
        "     (never open workspace/pristine/)\n"
        "  2. Extract FIELD/FIELD.BIN → iso-extract/FIELD.BIN\n"
        "  3. python scripts/build_field_encounter_patch.py workspace/iso-extract/FIELD.BIN\n"
        "  4. Import FIELD.BIN.new over FIELD/FIELD.BIN (pad if shorter; no truncate)\n"
        "     CDmage may auto-save — that updates the iso-extract working image only\n"
        "  5. python scripts/build_encounter_layers.py --version 0.1.0 --discs N"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
