#!/usr/bin/env python3
"""Force the LOST2 D1->D2 break-scene IFUW gate open on a work image.

Root cause (rediscovered from retired v0.1.37/v0.1.39 ship scripts, which
were never ported into build_work_bin.py): LOST2's init script (CSR D2
copy, merged in as the WHOLE_FILE_FIELDS["LOST2"] source) ends with an
IFUW checking Var[13][0] (GM) == 0xa455 before MAPJUMP-ing to field #526
(COS_BTM2, the disc-break scene):

  IFUW addr=0x0020 == 0xa455, else +0x0b   (6-byte op, else-byte is op[5])
  MAPJUMP field 526 (cos_btm2)

On multi-disc CSR this GM flag gets set by the real disc-swap event. On a
single-disc build nothing ever sets it, so the IFUW always takes the
"else" branch and skips the MAPJUMP -- LOST2's init just returns, and the
break scene / save prompt never fires. This clears that else-jump (0x0b
-> 0x00) so the MAPJUMP always executes.

Usage:
  python3 mods/single-disc/scripts/force_lost2_break_ifuw.py \\
    --bin workspace/iso-extract/work.bin --in-place
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from field_dat import load_field_dat, decode_ops  # noqa: E402
from lzs import compress_all_with_header, decompress_all_with_header  # noqa: E402
from psx_mode2_iso import extract_file, find_file, replace_file_within_sectors  # noqa: E402

FIELD = "FIELD/LOST2.DAT"
IFUW_PAT = bytes.fromhex("1820000055a4")  # IFUW Var[13][0] == 0xa455
MAPJUMP_TARGET_FIELD = 526  # cos_btm2


def force_lost2_ifuw(dec: bytearray) -> list[tuple[int, int]]:
    """Clear the final IFUW gate (the one immediately followed by the
    MAPJUMP to cos_btm2). Returns list of (offset, old_else_byte)."""
    forced: list[tuple[int, int]] = []
    i = 0
    while True:
        j = dec.find(IFUW_PAT, i)
        if j < 0:
            break
        op_len = 8  # IFUW: opcode(1) + addr(2) + value(2) + op(1) + else-jump(1) + pad? (see OPCODE_LENGTH)
        else_off = j + 7
        next_off = j + op_len
        if (
            next_off < len(dec)
            and dec[next_off] == 0x60  # MAPJUMP opcode
            and next_off + 3 <= len(dec)
        ):
            field_id = dec[next_off + 1] | (dec[next_off + 2] << 8)
            if field_id == MAPJUMP_TARGET_FIELD and dec[else_off] != 0x00:
                old = dec[else_off]
                dec[else_off] = 0x00
                forced.append((else_off, old))
        i = j + 1
    return forced


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bin", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()

    img = bytearray(args.bin.read_bytes())
    raw = extract_file(bytes(img), FIELD)
    meta = find_file(img, FIELD)
    nsec = max(1, (meta.size + 2047) // 2048)
    max_bytes = nsec * 2048

    dec = bytearray(decompress_all_with_header(raw))
    forced = force_lost2_ifuw(dec)
    if not forced:
        print("no LOST2 break-scene IFUW cleared (already open, or pattern not found)")
    for off, old in forced:
        print(f"  force IFUW else-byte @{off:#x}: {old:#x} -> 0x00")

    new_raw = compress_all_with_header(bytes(dec))
    print(f"recompressed {len(raw)} -> {len(new_raw)} (sector cap {max_bytes})")
    if len(new_raw) > max_bytes:
        raise SystemExit(f"too large for ISO slot {len(new_raw)} > {max_bytes}")

    # Sanity: confirm the target gate is open post-patch.
    f = load_field_dat(new_raw, "LOST2")
    still_closed = 0
    for s in f.scripts:
        ops = decode_ops(s.raw)
        for k, (rawop, name) in enumerate(ops):
            if name == "IFUW" and rawop.hex().startswith("1820000055a4") and rawop[7] != 0x00:
                if k + 1 < len(ops) and ops[k + 1][1] == "MAPJUMP":
                    still_closed += 1
    if still_closed:
        raise SystemExit(f"gate still closed on {still_closed} IFUW->MAPJUMP pair(s)")

    replace_file_within_sectors(img, FIELD, new_raw)
    out = args.bin if args.in_place or not args.output else args.output
    if not args.in_place and not args.output:
        raise SystemExit("pass --in-place or -o")
    out.write_bytes(img)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
