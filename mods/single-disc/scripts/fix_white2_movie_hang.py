#!/usr/bin/env python3
"""Strip WHITE2's (field 643) `mdir`/31 PMVIE/MOVIE movie-play block.

Root cause: WHITE2's `mdir` slot 31 plays two FMVs (PMVIE 0x1C "fallpl",
PMVIE 0x2A "boogdemo") gated by an IFSW on GameMoment, and on the
single-disc build neither movie ID resolves to a valid stream at its
single-disc location, so playback hangs (MDEC decode of garbage / DMA
FIFO underrun -- see docs/findings/2026-08-11-single-disc-white2-movie-crawl.md):

     UC / MENU2 / MVCAM 1
     IFSW GM >= 0x1620, else jump to PMVIE 0x2A
     PMVIE 0x1C
     JMPF -> NFADE (skip second PMVIE)
     PMVIE 0x2A
     NFADE (fade to black, speed=30, type=12)
     MOVIE
     RET

Both IFSW branches converge on the same NFADE/RET tail, so the whole
IFSW/PMVIE/JMPF/PMVIE/MOVIE block can be dropped, leaving just:

     UC / MENU2 / MVCAM 1
     NFADE (fade to black, speed=30, type=12)
     RET

Note: WHITE2's `cl`/31 slot also contains a PMVIE/MOVIE pair, but CSR
Disc 2 wraps it (and everything after) in an unconditional `JMPF` that
jumps clean over that block every time the script runs -- it's dead
code, never reached at runtime (see
docs/findings/2026-08-18-loslake1-hojo-audio-flicker-on-csr-overwrite.md).
An earlier version of this script also stripped `cl`/31's PMVIE/MOVIE
bytes, but doing so shifts every opcode after the removed bytes back
without updating the JMPF's fixed relative-offset literal, so the jump
lands mid-instruction and hangs the field -- worse than leaving the
(unreachable) movie call in place. `cl`/31 is intentionally left
untouched here.

Usage:
  python3 mods/single-disc/scripts/fix_white2_movie_hang.py \\
    --bin workspace/iso-extract/work.bin --in-place
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from field_dat import load_field_dat  # noqa: E402
from field_dat_write import write_field_dat  # noqa: E402
from psx_mode2_iso import extract_file, replace_file_within_sectors  # noqa: E402

FIELD = "FIELD/WHITE2.DAT"

MDIR_ENTITY, MDIR_SLOT = "mdir", 31
# Full original script (pristine D1/D2 and CSR D1/D2 all agree on this
# slot): UC, MENU2, MVCAM 1, IFSW.., PMVIE 1C, JMPF 3, PMVIE 2A, NFADE, MOVIE, RET
MDIR_ORIGINAL = bytes.fromhex(
    "33014a01fb011620000054060405f81c1003f82a2500000c0000001e00f900"
)
# Trimmed: UC, MENU2, MVCAM 1, NFADE, RET (movie block + gate removed)
MDIR_TRIMMED = bytes.fromhex("33014a01fb012500000c0000001e0000")


def _fix_mdir(img: bytearray, fd) -> tuple[bool, dict]:
    slot = next((s for s in fd.scripts if s.entity == MDIR_ENTITY and s.slot == MDIR_SLOT), None)
    if slot is None:
        raise SystemExit(f"{FIELD}: no {MDIR_ENTITY}/{MDIR_SLOT} script slot found")
    if slot.raw == MDIR_TRIMMED:
        print(f"  {MDIR_ENTITY}/{MDIR_SLOT} already trimmed, nothing to do")
        return False, {}
    if slot.raw != MDIR_ORIGINAL:
        raise SystemExit(
            f"{FIELD} {MDIR_ENTITY}/{MDIR_SLOT}: unexpected script bytes {slot.raw.hex()}, "
            f"expected {MDIR_ORIGINAL.hex()}"
        )
    print(f"  {FIELD} {MDIR_ENTITY}/{MDIR_SLOT}: removed IFSW/PMVIE/JMPF/PMVIE/MOVIE block "
          f"({len(MDIR_ORIGINAL)} -> {len(MDIR_TRIMMED)} bytes)")
    return True, {(MDIR_ENTITY, MDIR_SLOT): MDIR_TRIMMED}


def fix_white2(img: bytearray) -> bool:
    raw = extract_file(bytes(img), FIELD)
    fd = load_field_dat(raw)

    changed_mdir, edits = _fix_mdir(img, fd)
    if not edits:
        return False

    new_raw = write_field_dat(fd, edits)
    fd2 = load_field_dat(new_raw)
    for (entity, slot_idx), expected in edits.items():
        new_slot = next(s for s in fd2.scripts if s.entity == entity and s.slot == slot_idx)
        if new_slot.raw != expected:
            raise SystemExit(f"post-write verification failed: {entity}/{slot_idx} not trimmed as expected")
    replace_file_within_sectors(img, FIELD, new_raw)
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bin", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()
    if not args.in_place and not args.output:
        raise SystemExit("pass --in-place or -o/--output")

    img = bytearray(args.bin.read_bytes())
    print("Fixing WHITE2 movie hang (field 643)...")
    fix_white2(img)

    out = args.bin if args.in_place else args.output
    out.write_bytes(img)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
