#!/usr/bin/env python3
"""Extract the SCUS_941.6x kernel EXE from one or more pristine discs and
produce a Ghidra-ready ".body" file (PS-X EXE header stripped).

The kernel EXE filename differs per disc:
    Disc 1: SCUS_941.63
    Disc 2: SCUS_941.64
    Disc 3: SCUS_941.65

Usage:
    python scripts/extract_kernel_exe.py [D1] [D2] [D3]
    python scripts/extract_kernel_exe.py            # all three discs

Outputs (per disc):
    workspace/iso-extract/battle-raw/<exe>_<disc>        (full PS-X EXE)
    workspace/iso-extract/battle-dec/<exe>_<disc>.body   (header stripped,
                                                           import this in
                                                           Ghidra as Raw
                                                           Binary @ 0x80010000)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from psx_mode2_iso import extract_file

REPO_ROOT = Path(__file__).parent.parent
PRISTINE_DIR = REPO_ROOT / "workspace" / "pristine"
RAW_DIR = REPO_ROOT / "workspace" / "iso-extract" / "battle-raw"
BODY_DIR = REPO_ROOT / "workspace" / "iso-extract" / "battle-dec"

# (disc label, kernel EXE filename on that disc's root)
KERNEL_EXE_BY_DISC = {
    "D1": "SCUS_941.63",
    "D2": "SCUS_941.64",
    "D3": "SCUS_941.65",
}

EXE_HEADER_SIZE = 0x800  # PS-X EXE header; code/data starts right after it


def extract_disc(disc: str) -> None:
    exe = KERNEL_EXE_BY_DISC[disc]
    iso_path = PRISTINE_DIR / f"FINALFANTASY7_{disc}.bin"
    if not iso_path.exists():
        print(f"❌ Pristine ISO not found: {iso_path}")
        sys.exit(1)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    BODY_DIR.mkdir(parents=True, exist_ok=True)

    img = bytearray(iso_path.read_bytes())
    data = extract_file(img, exe)
    if data[:8] != b"PS-X EXE":
        print(f"❌ {exe} on {disc} does not start with PS-X EXE magic: {data[:8]!r}")
        sys.exit(1)

    raw_path = RAW_DIR / f"{exe}_{disc}"
    raw_path.write_bytes(data)

    body = data[EXE_HEADER_SIZE:]
    body_path = BODY_DIR / f"{exe}_{disc}.body"
    body_path.write_bytes(body)

    print(f"{disc} ({exe}): full {len(data):,} bytes -> {raw_path}")
    print(f"{disc} ({exe}): body {len(body):,} bytes -> {body_path}")


def main() -> None:
    discs = [d.upper() for d in sys.argv[1:]] or list(KERNEL_EXE_BY_DISC)
    for disc in discs:
        if disc not in KERNEL_EXE_BY_DISC:
            print(f"❌ Unknown disc {disc!r}; expected one of {list(KERNEL_EXE_BY_DISC)}")
            sys.exit(1)
    for disc in discs:
        extract_disc(disc)


if __name__ == "__main__":
    main()
