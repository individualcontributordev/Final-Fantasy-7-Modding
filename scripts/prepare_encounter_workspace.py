#!/usr/bin/env python3
"""Copy a disc image into iso-extract as a disposable CDmage working copy.

Retail (Unmodified Encounter):

  python scripts/prepare_encounter_workspace.py --discs 1
  python scripts/prepare_encounter_workspace.py --discs 1 --force

CSR / CSR+ / CSR++ stack (copy THAT base’s patched image — never the retail vault):

  python scripts/prepare_encounter_workspace.py --discs 1 --force \\
    --from-dir /c/path/to/Final-Fantasy-7-CSR/workspace/csr-plus

Expects under --from-dir:
  FINALFANTASY7_DN.bin   (+ .cue if present)
  (legacy: FINALFANTASY7_DN (patched).bin still accepted)

Writes:
  workspace/iso-extract/FINALFANTASY7_DN.bin (+ .cue)
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
PATCHED_NAME = "FINALFANTASY7_D{disc} (patched)"


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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(_ROOT))
    except ValueError:
        return str(path)


def copy_one(src: Path, dest: Path, *, force: bool) -> None:
    if not src.is_file():
        raise SystemExit(f"Missing source: {src}")
    if dest.exists() and not force:
        raise SystemExit(
            f"Already exists: {dest}\n"
            "Delete it, or re-run with --force to replace the working copy.\n"
            "Do not use --force if that file is your only patched image."
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  {rel(src)} → {rel(dest)}")
    shutil.copy2(src, dest)
    if dest.stat().st_size != src.stat().st_size:
        raise SystemExit(f"Copy size mismatch for {dest.name}")


def source_bin_and_cue(disc: int, from_dir: Path | None) -> tuple[Path, Path | None]:
    if from_dir is None:
        stem = DISC_STEM.format(disc=disc)
        bin_src = PRISTINE / f"{stem}.bin"
        cue_src = PRISTINE / f"{stem}.cue"
        return bin_src, cue_src if cue_src.is_file() else None

    from_dir = from_dir.expanduser().resolve()
    if not from_dir.is_dir():
        raise SystemExit(f"Not a directory: {from_dir}")

    patched = from_dir / f"{PATCHED_NAME.format(disc=disc)}.bin"
    retail = from_dir / f"{DISC_STEM.format(disc=disc)}.bin"
    if retail.is_file():
        bin_src = retail
    elif patched.is_file():
        bin_src = patched
    else:
        raise SystemExit(
            f"Missing disc {disc} under {from_dir}\n"
            f"  looked for: {retail.name}\n"
            f"           or: {patched.name}"
        )

    cue_candidates = [
        bin_src.with_suffix(".cue"),
        from_dir / f"{DISC_STEM.format(disc=disc)}.cue",
        from_dir / f"{PATCHED_NAME.format(disc=disc)}.cue",
    ]
    cue_src = next((c for c in cue_candidates if c.is_file()), None)
    return bin_src, cue_src


def prepare_disc(disc: int, *, force: bool, from_dir: Path | None) -> None:
    stem = DISC_STEM.format(disc=disc)
    print(f"\n=== Disc {disc}: refresh working copy ===")
    bin_src, cue_src = source_bin_and_cue(disc, from_dir)
    copy_one(bin_src, ISO / f"{stem}.bin", force=force)
    if cue_src is not None:
        copy_one(cue_src, ISO / f"{stem}.cue", force=force)
    else:
        print("  (no .cue found — add one next to the source .bin if CDmage needs it)")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Copy a base disc into iso-extract for CDmage Encounter work."
    )
    ap.add_argument("--discs", required=True, help="Comma list, e.g. 1 or 1,2,3")
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing working copies in iso-extract",
    )
    ap.add_argument(
        "--from-dir",
        default=None,
        help=(
            "Folder of the stack base to copy (CSR patched images). "
            "Default: workspace/pristine (retail / Unmodified)."
        ),
    )
    args = ap.parse_args()

    from_dir = Path(args.from_dir) if args.from_dir else None
    if from_dir is None and not PRISTINE.is_dir():
        raise SystemExit(
            f"Missing {PRISTINE}\n"
            "Create it and place FINALFANTASY7_D1.bin … D3.bin (+ .cue) there."
        )

    discs = parse_discs(args.discs)
    print(f"Source:      {from_dir or PRISTINE}")
    print(f"Working dir: {ISO}")
    print("Never open the source folder in CDmage for import — only iso-extract.")

    for disc in discs:
        prepare_disc(disc, force=args.force, from_dir=from_dir)

    against_hint = "clean"
    if from_dir is not None:
        name = from_dir.name.lower()
        if "plusplus" in name or "plus-plus" in name:
            against_hint = "csr-plusplus"
        elif "plus" in name:
            against_hint = "csr-plus"
        elif "csr" in name:
            against_hint = "csr"

    build_cmd = (
        f"python scripts/build_encounter_layers.py --version 0.1.0 --discs N "
        f"--against {against_hint}"
    )
    if from_dir is not None:
        build_cmd += f" --base-dir {from_dir}"

    print(
        "\nNext (per disc):\n"
        "  1. Open workspace/iso-extract/FINALFANTASY7_DN.cue in CDmage\n"
        "  2. Extract FIELD/FIELD.BIN → iso-extract/FIELD.BIN\n"
        "  3. python scripts/build_field_encounter_patch.py workspace/iso-extract/FIELD.BIN\n"
        "  4. Import FIELD.BIN.new over FIELD/FIELD.BIN (pad if shorter; no truncate)\n"
        f"  5. {build_cmd}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
