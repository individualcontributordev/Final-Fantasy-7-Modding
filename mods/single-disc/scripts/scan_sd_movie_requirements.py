#!/usr/bin/env python3
"""Cross-reference: what movies does the CURRENT single-disc D1 build need?

For every FIELD/*.DAT actually present on the built single-disc-core image
(whichever disc's file was chosen per csr-field-disc-prefer / SD core
layer), run CFG reachability and resolve each reachable PMVIE id against
THAT FIELD's origin disc's MOVIE/ list (since the field script's opcode
bytes -- including PMVIE ids -- are whatever disc's file we copied in,
unmodified). This tells us the *intended* movie content per scene.

We separately record what movie is CURRENTLY at that PMVIE id when resolved
against the D1 disc's own MOVIE/ list (what the engine will actually play
today, since D1 is the only disc at runtime) so mismatches are obvious.

Origin-disc detection: compare built field bytes vs pristine D1/D2/D3 and
CSR D1/D2/D3 bytes for the same field name.

Usage:
  python3 mods/single-disc/scripts/scan_sd_movie_requirements.py \\
      --bin workspace/iso-extract/ff7_d1_singledisc_core.bin \\
      -o /tmp/sd_movie_requirements.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import struct  # noqa: E402

from analyze_movie_reachability import analyze_field_bytes, field_gateway_targets  # noqa: E402
from disc_sources import load_csr_image, load_pristine_image  # noqa: E402
from psx_mode2_iso import USER, _list_dir, _u32_le, _user, extract_file  # noqa: E402
from scan_csr_movie_reachability import (  # noqa: E402
    ENTRY_FIELD_ID,
    build_field_graph,
    reachable_field_names,
)


def _movie_dir_by_lba(img: bytes) -> dict[int, str]:
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
    """PMVIE id -> movie filename via this disc's own MOVIE_ID.BIN (row.lba),
    not sorted-directory order (sorted order != PMVIE id; verified against
    CSR D2's real table)."""
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bin", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    print("Loading built SD image...", file=sys.stderr)
    sd_img = args.bin.read_bytes()
    sd_movies = movie_id_table(sd_img)
    sd_fields = field_dat_listing(sd_img)
    print(f"  {len(sd_fields)} fields, {len(sd_movies)} D1 MOVIE_ID.BIN rows", file=sys.stderr)

    print("  Building field-level MAPJUMP+gateway graph...", file=sys.stderr)
    sd_graph = build_field_graph(sd_img, sd_fields)
    sd_field_reachable = reachable_field_names(sd_fields, sd_graph)
    print(
        f"  {len(sd_field_reachable)}/{len(sd_fields)} fields reachable from entry field "
        f"(id {ENTRY_FIELD_ID})",
        file=sys.stderr,
    )

    print("Loading comparison sources (pristine + CSR D1/D2/D3)...", file=sys.stderr)
    sources: dict[str, bytes] = {}
    for d in (1, 2, 3):
        sources[f"pristine_d{d}"] = bytes(load_pristine_image(d))
        sources[f"csr_d{d}"] = bytes(load_csr_image(d))
    src_movies = {
        label: movie_id_table(img) for label, img in sources.items()
    }

    def origin_for(name: str, built_bytes: bytes) -> str:
        path = f"FIELD/{name}.DAT"
        for label, img in sources.items():
            try:
                if extract_file(img, path) == built_bytes:
                    return label
            except FileNotFoundError:
                continue
        return "unknown"

    rows = []
    errors = []
    for i, (name, (lba, size)) in enumerate(sorted(sd_fields.items())):
        built_bytes = read_extent(sd_img, lba, size)
        try:
            slots = analyze_field_bytes(built_bytes, name)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {e!r}")
            continue
        field_ok = name in sd_field_reachable
        # PMVIE only stores an id byte and is HARMLESS on its own -- it can
        # never crash or misplay anything. The actual risk is a reachable
        # MOVIE call (the player invocation): if the id that's live when it
        # executes is OOB or points at the wrong file, THAT is what
        # crashes/misplays. So we must resolve, path-sensitively, which id
        # is live at each reachable MOVIE call within this slot -- not just
        # check "a PMVIE is reachable somewhere" and "a MOVIE is reachable
        # somewhere else in the field" independently (that both over-reports,
        # e.g. a later PMVIE overwriting an earlier one before MOVIE runs,
        # and under-reports/misses cases with no PMVIE in this slot at all).
        # `s.live` (compute_slot_liveness): whether *anything* actually runs
        # this (entity, slot) -- auto-run Init/Main, or a statically-resolved
        # REQ/REQSW/REQEW/PREQ/PRQSW/PRQEW call from another live slot. This
        # catches genuine orphans (confirmed for FSHIP_22/23/25 mov|move/31
        # and BLIN2_I AD/31: a MOVIE opcode reachable within its own slot's
        # CFG, but nothing ever calls that entity at all). It is NOT proven
        # authoritative for every row, though -- our REQ/PREQ call-graph only
        # models statically-resolvable calls, so `live=False` elsewhere is
        # "unconfirmed", not "confirmed dead" (e.g. NRTHMK dir/31 has no
        # detectable caller and was manually confirmed NOT played in CSR --
        # consistent with being dead, but other `live=False` rows haven't
        # been checked this way) -- so we surface `live=False` as
        # `needs_manual_review` rather than silently dropping the row.
        movie_calls: list[tuple[str, int, int, int, bool]] = []  # entity, slot, movie_off, id, live
        inherited: list[tuple[str, int, int, bool]] = []  # entity, slot, movie_off, live (id set outside this slot)
        if field_ok:
            for s in slots:
                for off, mid in s.reachable_movie_resolutions():
                    if mid is None:
                        inherited.append((s.entity, s.slot, off, s.live))
                    else:
                        movie_calls.append((s.entity, s.slot, off, mid, s.live))
        if not movie_calls and not inherited:
            continue
        origin = origin_for(name, built_bytes)
        origin_movies = src_movies.get(origin, sd_movies)
        for entity, slot, off, mid, slot_live in movie_calls:
            intended = origin_movies[mid] if 0 <= mid < len(origin_movies) else f"OOB({mid})"
            current = sd_movies[mid] if 0 <= mid < len(sd_movies) else f"OOB({mid})"
            row = {
                "field": name,
                "entity": entity,
                "slot": slot,
                "offset": off,
                "movie_id": mid,
                "origin": origin,
                "intended_movie": intended,
                "current_d1_movie_at_id": current,
                "mismatch": intended != current,
                "slot_live": slot_live,
            }
            if not slot_live:
                row["needs_manual_review"] = True
                row["review_reason"] = "slot appears never called (not Init/Main, no REQ/PREQ targets it) -- verify in Makou Reactor before treating as real"
            rows.append(row)
        for entity, slot, off, slot_live in inherited:
            row = {
                "field": name,
                "entity": entity,
                "slot": slot,
                "offset": off,
                "movie_id": None,
                "origin": origin,
                "intended_movie": "INHERITED (id set outside this slot -- needs cross-field trace)",
                "current_d1_movie_at_id": "N/A",
                "mismatch": False,
                "needs_manual_review": True,
                "slot_live": slot_live,
            }
            if not slot_live:
                row["review_reason"] = "slot appears never called (not Init/Main, no REQ/PREQ targets it) -- verify in Makou Reactor before treating as real"
            rows.append(row)
        if (i + 1) % 150 == 0:
            print(f"  ...{i + 1}/{len(sd_fields)}", file=sys.stderr)

    mismatches = [r for r in rows if r["mismatch"]]
    result = {
        "field_count": len(sd_fields),
        "d1_movie_slots": sd_movies,
        "rows": rows,
        "mismatches": mismatches,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    needs_review = [r for r in rows if r.get("needs_manual_review")]
    print(f"Wrote {args.output}")
    print(
        f"Total reachable MOVIE-call resolutions: {len(rows)}; "
        f"mismatches (intended != current D1 slot): {len(mismatches)}; "
        f"inherited-id (needs manual review): {len(needs_review)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
