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

from analyze_movie_reachability import analyze_field_bytes, field_gateway_targets  # local dir on path via sys.path below
from disc_sources import load_csr_image  # noqa: E402
from psx_mode2_iso import USER, _list_dir, _u32_le, _user, extract_file  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Field-graph entry point: field id 116 = md1stin, Reactor 1 train platform --
# the very first field a new-game playthrough enters (confirmed via
# docs/reference/field-id-mapping.txt + ff7speedruns.com "md1stin is the
# first field map in Reactor 1"). BFS from here over MAPJUMP edges gives the
# set of fields CSR can actually make the player enter.
ENTRY_FIELD_ID = 116


def _load_field_id_mapping() -> dict[int, str]:
    root = Path(__file__).resolve().parents[3]
    path = root / "docs/reference/field-id-mapping.txt"
    out: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fid_s, name = line.split(maxsplit=1)
        out[int(fid_s)] = name.strip().upper()
    return out


# Field id 97 = blackbg5, a generic character-select/party-swap background
# screen. Its scripts MAPJUMP to whatever field each individually-named
# character (earith/tifa/pri/cefiros/ketcy/doctor/girl/yufi/crew2/...) last
# came from -- dozens of arbitrary story fields, not real walkmesh/story
# navigation. Treating those as real graph edges makes nearly every field in
# the game "reachable" from here and defeats the whole point of the
# reachability scan. Exclude its MAPJUMP edges (gateways, if any, still
# count).
MAPJUMP_FANOUT_EXCLUDE = {"BLACKBG5"}


def build_field_graph(img: bytes, fields: dict[str, tuple[int, int]]) -> dict[str, set[int]]:
    """field NAME -> set of target field IDs reachable from it, via either a
    reachable scripted MAPJUMP or a walkmesh gateway (door/exit line)."""
    graph: dict[str, set[int]] = {}
    for name, (lba, size) in fields.items():
        raw = read_extent(img, lba, size)
        targets: set[int] = set()
        if name.upper() not in MAPJUMP_FANOUT_EXCLUDE:
            try:
                slots = analyze_field_bytes(raw, name)
                for s in slots:
                    targets.update(s.reachable_mapjump_targets())
            except Exception:  # noqa: BLE001
                pass
        try:
            targets.update(field_gateway_targets(raw, name))
        except Exception:  # noqa: BLE001
            pass
        graph[name] = targets
    return graph


def reachable_field_names(fields: dict[str, tuple[int, int]], graph: dict[str, set[int]]) -> set[str]:
    """BFS from ENTRY_FIELD_ID over the MAPJUMP graph -> set of enterable field NAMEs."""
    id_to_name = _load_field_id_mapping()
    # This disc's FIELD/*.DAT names are upper-case; id_to_name values are
    # upper-cased too, but the disc's field-name set is the ground truth for
    # what's actually present on this disc image.
    name_set = set(fields)
    entry_name = id_to_name.get(ENTRY_FIELD_ID)
    if entry_name is None or entry_name not in name_set:
        # Fall back: can't resolve entry field on this disc (e.g. D2/D3 don't
        # ship md1stin) -- caller should treat every field as reachable
        # rather than silently reporting an empty set as "nothing reachable".
        return set(name_set)

    visited: set[str] = set()
    stack = [entry_name]
    while stack:
        cur = stack.pop()
        if cur in visited:
            continue
        visited.add(cur)
        for tid in graph.get(cur, ()):
            tname = id_to_name.get(tid)
            if tname and tname in name_set and tname not in visited:
                stack.append(tname)
    return visited


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

    print("  Building field-level MAPJUMP graph...", file=sys.stderr)
    graph = build_field_graph(img, fields)
    field_reachable = reachable_field_names(fields, graph)
    print(f"  {len(field_reachable)}/{len(fields)} fields reachable from entry field", file=sys.stderr)

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
        field_ok = name in field_reachable
        rows = []
        for s in slots:
            # Use reachable_movie_resolutions(), not all_pmvie(): PMVIE is a
            # no-op byte-store that's reachable even when a later JMPF skips
            # clean over the actual MOVIE opcode (e.g. NRTHMK dir/31 after
            # csr-v0.14.2 -- PMVIE still executes, MOVIE does not). Gating on
            # PMVIE reachability alone produces false-positive "live movie"
            # rows for exactly this pattern.
            for off, mid in s.reachable_movie_resolutions():
                if mid is None:
                    mfile = "UNRESOLVED"
                else:
                    mfile = movies[mid] if 0 <= mid < len(movies) else f"OOB({mid})"
                reach = field_ok
                rows.append(
                    {
                        "entity": s.entity,
                        "slot": s.slot,
                        "offset": off,
                        "movie_id": mid,
                        "movie_file": mfile,
                        "reachable": reach,
                        "field_reachable": field_ok,
                        "slot_live": s.live,
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
        "field_reachable_count": len(field_reachable),
        "unreachable_fields": sorted(set(fields) - field_reachable),
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
        # "required" = reachable AND slot_live (confirmed auto-run/REQ'd
        # caller). Reachable-but-not-slot_live rows are uncalled script
        # bodies -- CFG-reachable within their own slot, but nothing ever
        # invokes that slot -- so they're not required on disc, not "needs
        # manual review" (project convention: uncalled scripts are left
        # untouched during CSR editing precisely because they don't run).
        required_files = set()
        for entries in data["per_field"].values():
            for e in entries:
                if e["reachable"] and e["slot_live"]:
                    required_files.add(e["movie_file"])
        n_uncalled = n_reach - len(required_files)
        print(f"{d}: {len(required_files)} movies required (reachable + called), "
              f"{n_uncalled} reachable-but-uncalled slot (not required), "
              f"{n_dead} referenced-but-dead, {len(data['errors'])} field parse errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
