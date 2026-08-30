#!/usr/bin/env python3
"""Place a Disc 3 ending stream at its Disc 3 absolute LBA on a D1 image.

Post-final-battle sequence issues a hardcoded Setloc to MSF 43:51:67 = ISO
LBA 197242 -- ENDING2E.MOV's D3 file start. CONFIRMED via a full DuckStation
capture (save-state -> 4 boss fights -> ending, 2026-08-30 dslogs.txt): no
Setloc to ENDING01's LBA (163608) or ENDING3E's LBA (172631) ever fires in
this trigger path; the *only* ending-related seek is the single jump to
197242. Grown end-of-disc LBAs in MOVIE_ID alone are ignored for this path
(seek fails / decodes whatever D1 file physically occupies that LBA). Same
class of fix as CANONON @250450.

Writes full MODE2/2352 sectors from pristine D3, retargets the chosen D1
MOVIE/ dirent, and sets the MINT/MOVIE_ID.BIN row to Disc 3 LBA + size/aux.

Before writing, any other D1 MOVIE/ file whose sectors overlap the incoming
D3 range is relocated to free space at EOF and its dirent/MOVIE_ID updated
(see RELOCATE_NAMES). Splicing those files back in afterward at their
original LBAs would punch holes into the newly written ending stream and
corrupt playback.

  python3 mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py \\
    --d1 workspace/iso-extract/ff7_d1_playtest_ending_test.bin --in-place
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "mods/single-disc/scripts"))

from inject_movies_by_disc_id import (  # noqa: E402
    _movie_id_meta_by_lba,
    _patch_dirent_lba_size,
    _patch_movie_id_bin,
)
from psx_mode2_iso import (  # noqa: E402
    SECTOR,
    USER,
    _list_dir,
    _u32_le,
    _user,
    extract_file,
    find_file,
    replace_file_padded,
    set_pvd_volume_space_size,
)

# (MOVIE_ID row, D3 MOVIE name, D1 slot to retarget)
#
# id24/LASTFLOR.MOV removed 2026-08-23: the fresh CSR D3 LASTMAP edit
# strips PMVIE f818 (the opcode that set MOVIE_ID row 24) from AD script 4,
# so id24 is never referenced by the field anymore -- confirmed no other
# field DAT sets MOVIE_ID row 24 either. Keeping the alias would just be
# dead weight in the layer.
#
# id23/ONTRAIN.MOV removed 2026-08-24: user requested removal for testing.
#
# 2026-08-30 (2nd log capture, ENDING01-only build): a full dslogs.txt
# spanning save-state -> 4 boss fights -> ending shows NO Setloc to
# 36:23:33/LBA 163608 (ENDING01's D3 start) anywhere in the log. The *only*
# ending-related Setloc that ever fires is a single jump straight to MSF
# 43:51:67 = LBA 197242 -- ENDING2E.MOV's D3 start (MOVIE_ID row 29). The
# previously assumed "ENDING01 -> ENDING3E -> ENDING2E" chain does not
# happen for this trigger; ENDING01/ENDING3E are never sought at all.
#
# This means aliasing ENDING01 was a red herring for this corruption --
# the only file that needs to be physically present at its D3 LBA is
# ENDING2E. Switched JOBS accordingly per explicit user request.
JOBS = (
    (29, "ENDING2E.MOV", "MONITOR.STR"),
)

PRISTINE_D3 = _ROOT / "workspace/pristine/FINALFANTASY7_D3.bin"


def _raw(src: bytes, lba: int, nsec: int) -> bytes:
    off = lba * SECTOR
    return src[off : off + nsec * SECTOR]


def _write_raw(img: bytearray, lba: int, raw: bytes) -> None:
    if len(raw) % SECTOR:
        raise ValueError("raw length not multiple of 2352")
    nsec = len(raw) // SECTOR
    need = (lba + nsec) * SECTOR
    if need > len(img):
        if len(img) % SECTOR:
            img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
        img.extend(b"\x00" * (need - len(img)))
    off = lba * SECTOR
    img[off : off + len(raw)] = raw


def _movie_files(img: bytes | bytearray):
    pvd = _user(img, 16)
    root = pvd[156:190]
    for n, lba, sz, d in _list_dir(img, _u32_le(root, 2), _u32_le(root, 10)):
        if n == "MOVIE" and d:
            return [
                (nn, lb, ss)
                for nn, lb, ss, dd in _list_dir(img, lba, sz)
                if nn not in (".", "..") and not dd
            ]
    raise FileNotFoundError("MOVIE/")


# 2026-08-30: previously a hardcoded allowlist ({"GOLD7_2.MOV", "CANONON.MOV"}
# scoped to the now-removed ENDING2E span). That was the root cause of the
# PLREXP/FALLPL corruption bug -- ENDING01 alone still overruns SMK.STR's
# original dirent bounds and physically clobbers whatever real MOVIE/ files
# sit in its path (MAINPLR, SOUTHMK, PLREXP, FALLPL), none of which were in
# the allowlist. _relocate_collisions now moves ANY colliding file, not just
# a fixed set.


def _relocate_collisions(
    img: bytearray, ranges: list[tuple[int, int]], keep_names: set[str]
) -> list[str]:
    """Move every D1 MOVIE/ file whose sectors overlap `ranges` to EOF.

    `keep_names` are the D1 slots the caller is about to overwrite on purpose
    (the ending-stream targets) -- those are skipped here since clobbering
    them is the intended effect, not a collision to repair. Every other
    overlapping file is relocated so the raw ending-stream write can't
    physically stomp its sectors.
    """
    notes: list[str] = []
    for name, lba, size in sorted(_movie_files(bytes(img)), key=lambda x: x[1]):
        if name.upper() in keep_names:
            continue
        nsec = (size + USER - 1) // USER
        file_end = lba + nsec - 1
        if not any(file_end >= r0 and lba <= r1 for r0, r1 in ranges):
            continue
        path = "MOVIE/" + name
        raw = _raw(bytes(img), lba, nsec)
        new_lba = len(img) // SECTOR if len(img) % SECTOR == 0 else (len(img) // SECTOR) + 1
        _write_raw(img, new_lba, raw)
        _patch_dirent_lba_size(img, path, new_lba, size)
        # MOVIE_ID.BIN's "size" field is the Form2 engine length
        # (nsec*2336, sometimes not exactly that), NOT the ISO9660 dirent
        # byte size -- overwriting it with `size` (ISO bytes) here was the
        # actual root cause of relocated movies not playing (engine size
        # field went from e.g. 5847008 to 5126144 for PLREXP). Preserve the
        # existing engine size + aux fields verbatim; only the LBA changes.
        eng_meta = _movie_id_meta_by_lba(img, lba)
        if eng_meta is not None:
            eng_size, a, b, c = eng_meta
            n = _patch_movie_id_bin(img, lba, new_lba, eng_size, aux=(a, b, c))
        else:
            notes.append(f"WARN {name}: no MOVIE_ID row found for LBA {lba}, using ISO size")
            n = _patch_movie_id_bin(img, lba, new_lba, size)
        notes.append(
            f"RELOCATE {name} LBA {lba}..{file_end} -> EOF LBA {new_lba} "
            f"(MOVIE_ID x{n})"
        )
    return notes


def apply(img: bytearray, d3: bytes) -> list[str]:
    blob3 = extract_file(d3, "MINT/MOVIE_ID.BIN")
    notes: list[str] = []

    # Relocation stays generic over JOBS (currently just ENDING2E, LBA
    # 197242..277345) so any D1 MOVIE/ file physically overlapping that
    # range gets moved to free space at EOF first instead of being clobbered
    # by the raw write below.
    ranges = []
    for mid, d3name, _d1name in JOBS:
        m3 = find_file(d3, f"MOVIE/{d3name}")
        nsec = (m3.size + USER - 1) // USER
        ranges.append((m3.lba, m3.lba + nsec - 1))
    keep_names = {d1name.upper() for _mid, _d3name, d1name in JOBS}
    notes.extend(_relocate_collisions(img, ranges, keep_names))

    blob = bytearray(extract_file(img, "MINT/MOVIE_ID.BIN"))
    for mid, d3name, d1name in JOBS:
        m3 = find_file(d3, f"MOVIE/{d3name}")
        nsec = (m3.size + USER - 1) // USER
        r3 = struct.unpack_from("<IIIII", blob3, mid * 20)
        d3_lba = m3.lba
        if r3[0] != d3_lba:
            notes.append(
                f"WARN id{mid}: MOVIE_ID LBA {r3[0]} != file {d3_lba}; using file"
            )
        raw = _raw(d3, d3_lba, nsec)
        _write_raw(img, d3_lba, raw)
        _patch_dirent_lba_size(img, f"MOVIE/{d1name}", d3_lba, m3.size)
        struct.pack_into(
            "<IIIII", blob, mid * 20, d3_lba, r3[1], r3[2], r3[3], r3[4]
        )
        notes.append(
            f"OK id{mid} {d3name} -> {d1name} LBA={d3_lba} nsec={nsec} eng={r3[1]}"
        )
    replace_file_padded(img, "MINT/MOVIE_ID.BIN", bytes(blob))
    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    # Relocation + the raw D3 write can grow the image past the PVD's
    # original volume space size. Update it so the ISO9660 driver doesn't
    # treat the new EOF sectors (relocated MOVIE/ files, ENDING2E) as past
    # end-of-disc and refuse to read them.
    new_nsectors = len(img) // SECTOR
    old_nsectors = _u32_le(_user(img, 16), 80)
    if new_nsectors != old_nsectors:
        set_pvd_volume_space_size(img, new_nsectors)
        notes.append(f"PVD volume space size {old_nsectors} -> {new_nsectors}")
    return notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--d1", type=Path, required=True)
    ap.add_argument("--d3", type=Path, default=PRISTINE_D3)
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()
    if not args.d1.is_file():
        print("missing", args.d1, file=sys.stderr)
        return 1
    if not args.d3.is_file():
        print("missing", args.d3, file=sys.stderr)
        return 1
    img = bytearray(args.d1.read_bytes())
    d3 = args.d3.read_bytes()
    for line in apply(img, d3):
        print(line)
    out = args.d1 if args.in_place else args.output
    if out is None:
        print("pass --in-place or -o", file=sys.stderr)
        return 2
    out.write_bytes(img)
    print("wrote", out, len(img), "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
