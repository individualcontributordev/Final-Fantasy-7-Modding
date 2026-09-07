#!/usr/bin/env python3
"""Common commands for this add-on repo.

A new mod starts as a copy of the retail discs (pristine). The builder shows
that parent as Unmodified; pack.json records it as catalog id ``clean``. There
is no ``builder/clean/`` layer — applying one is the mistake this tool exists
to prevent.

  python3 scripts/ff7mod.py new
  python3 scripts/ff7mod.py rebuild all
  python3 scripts/ff7mod.py verify unmodified
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRISTINE_DIR = ROOT / "workspace" / "pristine"
SCRIPTS = ROOT / "scripts"

STEM_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^[0-9]+(\.[0-9]+)*$")


def _ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    if value:
        return value
    if default is not None:
        return default
    raise SystemExit(f"Need a value for: {prompt}")


def _ask_yes(prompt: str, *, default_yes: bool = True) -> bool:
    hint = "Y/n" if default_yes else "y/N"
    value = input(f"{prompt} [{hint}]: ").strip().lower()
    if not value:
        return default_yes
    return value in ("y", "yes")


def parse_discs(spec: str) -> list[int]:
    discs: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        disc = int(part)
        if disc not in (1, 2, 3):
            raise SystemExit(f"Disc must be 1, 2, or 3 -- got {disc}")
        discs.append(disc)
    if not discs:
        raise SystemExit("Pass at least one disc, e.g. 1,2,3")
    return list(dict.fromkeys(discs))


def pristine_bin(root: Path, disc: int) -> Path:
    return root / "workspace" / "pristine" / f"FINALFANTASY7_D{disc}.bin"


def scaffold(
    *,
    root: Path,
    pack_id: str,
    name: str,
    blurb: str,
    hint: str,
    version: str,
    discs: list[int],
    copy_bins: bool = True,
    force: bool = False,
) -> list[Path]:
    """Create recipe + Unmodified pack stub, and copy pristine into cache.

    Later recuts onto csr / csr-plus / highwind are separate pack ids
    (``<id>-on-csr-plus``, …), not extra entries in this pack's
    compatibleBases.
    """
    if not STEM_RE.fullmatch(pack_id):
        raise SystemExit(
            f"Pack id {pack_id!r} must be kebab-case, e.g. diamond-weapon-speed"
        )
    if not VERSION_RE.fullmatch(version):
        raise SystemExit(f"Bad version {version!r}")
    if not name.strip() or not blurb.strip() or not hint.strip():
        raise SystemExit("name, blurb, and hint are required")

    recipe_dir = root / "mods" / pack_id
    pack_dir = root / "builder" / pack_id
    cache_dir = root / "cache" / pack_id
    pack_json = pack_dir / "pack.json"
    version_file = recipe_dir / "VERSION"

    existing = [p for p in (pack_json, version_file) if p.exists()]
    if existing and not force:
        listed = ", ".join(str(p.relative_to(root)) for p in existing)
        raise SystemExit(f"Already exists ({listed}). Pass --force to replace.")

    written: list[Path] = []
    recipe_scripts = recipe_dir / "scripts"
    recipe_scripts.mkdir(parents=True, exist_ok=True)
    version_file.write_text(version + "\n", encoding="utf-8", newline="\n")
    written.append(version_file)

    pack = {
        "id": pack_id,
        "name": name.strip(),
        "kind": "mod",
        "blurb": blurb.strip(),
        "hint": hint.strip(),
        "format": "ic-layer-v1",
        "compatibleBases": ["clean"],
    }
    pack_dir.mkdir(parents=True, exist_ok=True)
    pack_json.write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    written.append(pack_json)

    cache_dir.mkdir(parents=True, exist_ok=True)
    if copy_bins:
        for disc in discs:
            src = pristine_bin(root, disc)
            if not src.is_file():
                raise SystemExit(
                    f"Missing {src}. Put retail NTSC-U MODE2/2352 images in "
                    "workspace/pristine/ (never edit those copies)."
                )
            dest = cache_dir / f"FINALFANTASY7_D{disc}.bin"
            shutil.copy2(src, dest)
            written.append(dest)
            print(f"  copied pristine disc {disc} -> {dest.relative_to(root)}")

    return written


def cmd_new(args: argparse.Namespace) -> int:
    interactive = sys.stdin.isatty() and not args.yes
    pack_id = args.id
    name = args.name
    blurb = args.blurb
    hint = args.hint
    version = args.version
    discs_spec = args.discs

    if interactive:
        print(
            "New add-ons start from a copy of the retail discs (pristine).\n"
            "The builder lists that parent as Unmodified; pack.json uses\n"
            'compatibleBases: ["clean"]. There is no clean layer to apply.\n'
        )
        pack_id = pack_id or _ask("Pack id (kebab-case)")
        name = name or _ask("Display name", pack_id.replace("-", " ").title())
        blurb = blurb or _ask("Blurb")
        hint = hint or _ask("Hint (short UI line)")
        version = version or _ask("Version", "0.1.0")
        discs_spec = discs_spec or _ask("Discs to copy", "1,2,3")
    else:
        missing = [
            label
            for label, value in (
                ("--id", pack_id),
                ("--name", name),
                ("--blurb", blurb),
                ("--hint", hint),
            )
            if not value
        ]
        if missing:
            raise SystemExit(
                "Non-interactive new needs " + ", ".join(missing)
            )
        version = version or "0.1.0"
        discs_spec = discs_spec or "1,2,3"

    discs = parse_discs(discs_spec)
    print(
        f"\nWill write (against Unmodified / clean):\n"
        f"  mods/{pack_id}/VERSION\n"
        f"  mods/{pack_id}/scripts/\n"
        f"  builder/{pack_id}/pack.json\n"
        f"  cache/{pack_id}/FINALFANTASY7_D{{n}}.bin  discs {discs}\n"
    )
    if interactive and not _ask_yes("Create these files?"):
        print("Cancelled.")
        return 1

    written = scaffold(
        root=ROOT,
        pack_id=pack_id,
        name=name,
        blurb=blurb,
        hint=hint,
        version=version,
        discs=discs,
        copy_bins=not args.no_bins,
        force=args.force,
    )
    print("Created:")
    for path in written:
        try:
            print(f"  {path.relative_to(ROOT)}")
        except ValueError:
            print(f"  {path}")
    print(
        "\nEdit the BINs under cache/<id>/, then repair and "
        "python3 scripts/build_base_layer.py IMAGE --version "
        f"{version}\n"
        "Recut onto csr / csr-plus / highwind later as separate pack ids."
    )
    return 0


def _delegate(script: str, argv: list[str]) -> int:
    return subprocess.call(
        [sys.executable, str(SCRIPTS / script), *argv], cwd=ROOT
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Modding-repo helper. New mods copy pristine; Unmodified is "
            "catalog id clean (no layer)."
        )
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    new_p = sub.add_parser(
        "new",
        help="Scaffold a pack from a copy of pristine (Unmodified / clean)",
    )
    new_p.add_argument("--id", help="Pack id, e.g. diamond-weapon-speed")
    new_p.add_argument("--name", help="Builder display name")
    new_p.add_argument("--blurb")
    new_p.add_argument("--hint")
    new_p.add_argument("--version", default=None)
    new_p.add_argument("--discs", default=None, help="Comma list, default 1,2,3")
    new_p.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing stub pack.json / VERSION",
    )
    new_p.add_argument(
        "--no-bins",
        action="store_true",
        help="Write metadata only (no pristine copies)",
    )
    new_p.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Do not prompt; requires --id --name --blurb --hint",
    )

    rebuild_p = sub.add_parser(
        "rebuild",
        help="Recut overlay recipes (same as rebuild_on_base.py)",
    )
    rebuild_p.add_argument(
        "rest",
        nargs=argparse.REMAINDER,
        help="Passed through: all | unmodified | csr | csr-plus | highwind",
    )

    verify_p = sub.add_parser(
        "verify",
        help="Validate published packs (same as verify_builder_config.py)",
    )
    verify_p.add_argument("rest", nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)
    if args.cmd == "new":
        return cmd_new(args)
    if args.cmd == "rebuild":
        return _delegate("rebuild_on_base.py", args.rest)
    if args.cmd == "verify":
        return _delegate("verify_builder_config.py", args.rest)
    raise SystemExit(f"unknown command {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
