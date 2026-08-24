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

from analyze_movie_reachability import analyze_field_bytes  # noqa: E402
from disc_sources import load_csr_image, load_pristine_image  # noqa: E402
from psx_mode2_iso import USER, _list_dir, _u32_le, _user, extract_file  # noqa: E402


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
        pmvies = []
        for s in slots:
            for off, mid, reach in s.all_pmvie():
                if reach:
                    pmvies.append((s.entity, s.slot, off, mid))
        if not pmvies:
            continue
        origin = origin_for(name, built_bytes)
        origin_movies = src_movies.get(origin, sd_movies)
        for entity, slot, off, mid in pmvies:
            intended = origin_movies[mid] if 0 <= mid < len(origin_movies) else f"OOB({mid})"
            current = sd_movies[mid] if 0 <= mid < len(sd_movies) else f"OOB({mid})"
            rows.append(
                {
                    "field": name,
                    "entity": entity,
                    "slot": slot,
                    "offset": off,
                    "movie_id": mid,
                    "origin": origin,
                    "intended_movie": intended,
                    "current_d1_movie_at_id": current,
                    "mismatch": intended != current,
                }
            )
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
    print(f"Wrote {args.output}")
    print(f"Total reachable PMVIE rows: {len(rows)}; mismatches (intended != current D1 slot): {len(mismatches)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
