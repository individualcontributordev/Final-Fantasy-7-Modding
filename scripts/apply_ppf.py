#!/usr/bin/env python3
"""Apply a PPF 2.0/3.0 patch to a BIN/ISO — same idea as RomPatcher.js apply mode.

Example:
  python scripts/apply_ppf.py \\
    workspace/iso-extract/ff7_disc1_pristine.bin \\
    workspace/iso-extract/yourmod-disc1.ppf \\
    -o workspace/iso-extract/ff7_disc1_patched.bin

Never overwrite the pristine dump unless you pass --in-place (not recommended).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from make_ppf import apply_ppf3  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Apply a PPF patch to a BIN/ISO (RomPatcher.js-compatible)."
    )
    ap.add_argument("rom", type=Path, help="Pristine (or base) .bin / .iso")
    ap.add_argument("ppf", type=Path, help="Patch file (.ppf)")
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Patched output (default: <rom_stem>_patched.bin next to rom)",
    )
    ap.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the input rom (dangerous — keep a pristine backup)",
    )
    args = ap.parse_args()

    rom = args.rom.expanduser().resolve()
    ppf = args.ppf.expanduser().resolve()
    if not rom.is_file():
        raise SystemExit(f"not found: {rom}")
    if not ppf.is_file():
        raise SystemExit(f"not found: {ppf}")

    if args.in_place:
        output = rom
    elif args.output:
        output = args.output.expanduser().resolve()
    else:
        output = rom.with_name(rom.stem + "_patched.bin")

    if output.resolve() == rom.resolve() and not args.in_place:
        raise SystemExit("refusing to overwrite input without --in-place")

    print(f"ROM:    {rom} ({rom.stat().st_size} bytes)")
    print(f"PPF:    {ppf} ({ppf.stat().st_size} bytes)")
    print(f"Output: {output}")

    info = apply_ppf3(rom, ppf, output)
    print(f"PPF v{info['version']}: {info['description']!r}")
    print(f"Records: {info['records']}")
    print(f"Changed: {info['changed_bytes']} bytes")
    print(f"Wrote:   {info['output']} ({info['output_size']} bytes)")
    print("Done.")


if __name__ == "__main__":
    main()
