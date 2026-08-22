#!/usr/bin/env python3
"""Strip the movie-play block from WHITE2's mdir/31 script (field 643).

Root cause: WHITE2's `mdir` slot 31 script plays two FMVs (PMVIE 0x1C
"fallpl", PMVIE 0x2A "boogdemo") gated by an IFSW on GameMoment, then a
MOVIE opcode that starts playback:

  UC / MENU2 / MVCAM 1
  IFSW GM >= 0x1620, else jump to PMVIE 0x2A
  PMVIE 0x1C
  JMPF -> NFADE (skip second PMVIE)
  PMVIE 0x2A
  NFADE (fade to black, speed=30, type=12)
  MOVIE
  RET

On the single-disc build these movie files no longer resolve to valid
streams at their expected disc locations, so the MOVIE opcode hangs
(MDEC decode of garbage / DMA FIFO underrun -- see
docs/findings/2026-08-11-single-disc-white2-movie-crawl.md for the
related v0.1.3 movie-pair regression on this same field).

Per the field 643 fix recorded in docs/INSTRUCTIONS.md (commit
3d9a73e): drop the IFSW/PMVIE/JMPF/PMVIE/MOVIE block entirely and keep
only the character-lock + fade-to-black + return, since both branches
of the IFSW converge on the same NFADE/RET tail anyway:

  UC / MENU2 / MVCAM 1
  NFADE (fade to black, speed=30, type=12)
  RET

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

from field_dat import load_field_dat, decode_ops  # noqa: E402
from field_dat_write import write_field_dat  # noqa: E402
from psx_mode2_iso import extract_file, replace_file_within_sectors  # noqa: E402

FIELD = "FIELD/WHITE2.DAT"
ENTITY = "mdir"
SLOT = 31

# Full original script (pristine D1/D2 and CSR D1/D2 all agree on this
# slot): UC, MENU2, MVCAM 1, IFSW.., PMVIE 1C, JMPF 3, PMVIE 2A, NFADE, MOVIE, RET
ORIGINAL = bytes.fromhex(
    "33014a01fb011620000054060405f81c1003f82a2500000c0000001e00f900"
)
# Trimmed: UC, MENU2, MVCAM 1, NFADE, RET (movie block + gate removed)
TRIMMED = bytes.fromhex("33014a01fb012500000c0000001e0000")


def fix_white2(img: bytearray) -> bool:
    raw = extract_file(bytes(img), FIELD)
    fd = load_field_dat(raw)
    slot = next((s for s in fd.scripts if s.entity == ENTITY and s.slot == SLOT), None)
    if slot is None:
        raise SystemExit(f"{FIELD}: no {ENTITY}/{SLOT} script slot found")
    if slot.raw == TRIMMED:
        print(f"  {ENTITY}/{SLOT} already trimmed, nothing to do")
        return False
    if slot.raw != ORIGINAL:
        raise SystemExit(
            f"{FIELD} {ENTITY}/{SLOT}: unexpected script bytes {slot.raw.hex()}, "
            f"expected {ORIGINAL.hex()}"
        )
    new_raw = write_field_dat(fd, {(ENTITY, SLOT): TRIMMED})
    fd2 = load_field_dat(new_raw)
    new_slot = next(s for s in fd2.scripts if s.entity == ENTITY and s.slot == SLOT)
    if new_slot.raw != TRIMMED:
        raise SystemExit("post-write verification failed: script not trimmed as expected")
    for name in ("PMVIE", "MOVIE"):
        if any(n == name for _, n in decode_ops(new_slot.raw)):
            raise SystemExit(f"post-write verification failed: {name} still present")
    replace_file_within_sectors(img, FIELD, new_raw)
    print(f"  {FIELD} {ENTITY}/{SLOT}: removed IFSW/PMVIE/JMPF/PMVIE/MOVIE block "
          f"({len(ORIGINAL)} -> {len(TRIMMED)} bytes)")
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
