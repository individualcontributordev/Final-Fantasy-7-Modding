#!/usr/bin/env python3
"""Full CSR D1/D2/D3 FIELD scan: which PMVIE/MOVIE pairs are actually reachable.

Uses analyze_movie_reachability.py's CFG analysis (not opcode presence) on
every FIELD/*.DAT on each CSR disc, resolves each PMVIE id to that disc's
movie filename (sorted MOVIE/ dir order = disc-local PMVIE id, confirmed by
inject_movies_by_disc_id.py / docs/reference/movie-id-mapping.txt), and
reports the disc-by-disc "the experience actually plays this" movie set.

Usage:
  python3 mods/single-disc/scripts/scan_csr_movie_reachability.py \\
      -o /tmp/csr_movie_reachability.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))

import struct  # noqa: E402

from analyze_movie_reachability import analyze_field_bytes  # local dir on path via sys.path below
from disc_sources import load_csr_image  # noqa: E402
from psx_mode2_iso import USER, _list_dir, _u32_le, _user, extract_file  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))


def _movie_dir_by_lba(img: bytes) -> dict[int, str]:
    """LBA -> filename for every MOVIE/ dirent (unsorted; keyed by real LBA)."""
    pvd = _user(img, 16)
    root = pvd[156:190]
    for n, lba, sz, d in _list_dir(img, _u32_le(root, 2), _u32_le(root, 10)):
        if n == "MOVIE" and d:
            out = {}
            for nn, lb, ss, dd in _list_dir(img, lba, sz):
                if nn in (".", "..") or dd:
                    continue
                out[lb] = nn.upper()
            return out
    return {}


def movie_id_table(img: bytes) -> list[str]:
    """PMVIE id -> movie filename, resolved via this disc's own MOVIE_ID.BIN
    (row[id].lba), NOT sorted-directory-order. Sorted-dir-order != PMVIE id
    (confirmed: CSR D2 MOVIE_ID row 0 LBA 129252 = FSHIP2.BIN, while sorted
    MOVIE/ index 0 is BOOGDOWN.STR -- an unrelated file at a different LBA).
    """
    by_lba = _movie_dir_by_lba(img)
    try:
        blob = extract_file(img, "MINT/MOVIE_ID.BIN")
    except FileNotFoundError:
        return []
    n = len(blob) // 20
    out = []
    for i in range(n):
        lba = struct.unpack_from("<I", blob, i * 20)[0]
        out.append(by_lba.get(lba, f"UNRESOLVED_LBA_{lba}"))
    return out


# Back-compat alias: some earlier code called this movie_entries(); keep the
# name available for the sd requirements scanner but delegate to the correct
# by-lba table.
def movie_entries(img: bytes):
    table = movie_id_table(img)
    return [(name, None, None) for name in table]


def field_dat_listing(img: bytes) -> dict[str, tuple[int, int]]:
    pvd = _user(img, 16)
    root = pvd[156:190]
    for n, lba, sz, d in _list_dir(img, _u32_le(root, 2), _u32_le(root, 10)):
        if n == "FIELD" and d:
            out = {}
            for nn, lb, ss, dd in _list_dir(img, lba, sz):
                if dd or not nn.upper().endswith(".DAT"):
                    continue
                out[nn.upper()[: -len(".DAT")]] = (lb, ss)
            return out
    raise FileNotFoundError("FIELD/")


def read_extent(img: bytes, lba: int, size: int) -> bytes:
    remaining = size
    sector = lba
    out = bytearray()
    while remaining > 0:
        take = min(USER, remaining)
        out.extend(_user(img, sector)[:take])
        remaining -= take
        sector += 1
    return bytes(out)


def scan_disc(disc: int) -> dict:
    print(f"Loading CSR D{disc}...", file=sys.stderr)
    img = bytes(load_csr_image(disc))
    movies = movie_id_table(img)
    fields = field_dat_listing(img)
    print(f"  {len(fields)} FIELD/*.DAT, {len(movies)} MOVIE_ID.BIN rows", file=sys.stderr)

    # field name -> list of {movie_id, movie_file, reachable, entity, slot}
    per_field: dict[str, list[dict]] = {}
    # movie filename -> True if reachable from ANY field on this disc
    movie_reachable: dict[str, bool] = {}
    errors: list[str] = []

    for i, (name, (lba, size)) in enumerate(sorted(fields.items())):
        raw = read_extent(img, lba, size)
        try:
            slots = analyze_field_bytes(raw, name)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {e!r}")
            continue
        rows = []
        for s in slots:
            for off, mid, reach in s.all_pmvie():
                mfile = movies[mid] if 0 <= mid < len(movies) else f"OOB({mid})"
                rows.append(
                    {
                        "entity": s.entity,
                        "slot": s.slot,
                        "offset": off,
                        "movie_id": mid,
                        "movie_file": mfile,
                        "reachable": reach,
                    }
                )
                if reach:
                    movie_reachable[mfile] = True
                else:
                    movie_reachable.setdefault(mfile, False)
        if rows:
            per_field[name] = rows
        if (i + 1) % 150 == 0:
            print(f"  ...{i + 1}/{len(fields)}", file=sys.stderr)

    return {
        "disc": disc,
        "movie_count": len(movies),
        "field_count": len(fields),
        "movies": movies,
        "per_field": per_field,
        "movie_reachable_anywhere": movie_reachable,
        "errors": errors,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--discs", default="1,2,3")
    args = ap.parse_args()

    result = {}
    for d in [int(x) for x in args.discs.split(",")]:
        result[f"D{d}"] = scan_disc(d)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {args.output}")
    for d, data in result.items():
        n_reach = sum(1 for v in data["movie_reachable_anywhere"].values() if v)
        n_dead = sum(1 for v in data["movie_reachable_anywhere"].values() if not v)
        print(f"{d}: {n_reach} movies reachable from >=1 field, {n_dead} referenced-but-dead, "
              f"{len(data['errors'])} field parse errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
