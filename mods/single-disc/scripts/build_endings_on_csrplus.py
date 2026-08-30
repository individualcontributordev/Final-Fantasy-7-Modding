#!/usr/bin/env python3
"""Re-diff the single-disc ending/credits movies against the collapsed
csr-plus-v0.1.0 base (no manip-movies dependency).

The original single-disc-endings-v0.1.0-partN layers were diffed against
ff7_d1_playtest_csr_sd_movies.bin, which stacked CSR + single-disc-on-csr +
manip-movies v0.1.4/5/6 first. csr-plus-v0.1.0 intentionally does NOT fold in
manip-movies (vanilla intro/multi-disc FMVs stay), so those old parts don't
apply cleanly on top of it. This script rebuilds the ending-stream diff
directly against the csr-plus-v0.1.0 disc1 image:

  pristine D1 -> csr-plus-v0.1.0/layers/disc1.layer.json (base, no endings)
  -> alias_d3_ending_lbas_on_d1.apply() (D3 ENDING01/2E/3E streams at D3 LBAs,
     relocating any colliding D1 GOLD7_2/CANONON slots to EOF)
  -> diff vs the base (pre-endings) image, chunked into <=30MiB parts

Writes builder/single-disc-endings-csrplus-v0.1.0-partN/layers/disc1.layer.json

Usage (repo root):
  python3 mods/single-disc/scripts/build_endings_on_csrplus.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import MAX_RECORD_BYTES, iter_runs  # noqa: E402
from check_movie_id_collisions import check as check_movie_id_collisions  # noqa: E402
from disc_sources import csr_root, pristine_bin  # noqa: E402
from psx_mode2_iso import SECTOR  # noqa: E402

import alias_d3_ending_lbas_on_d1 as alias_endings  # noqa: E402

CSR = csr_root()
CD80_SECTORS = 360000
MAX_CHANGED_PER_PART = 30 * 1024 * 1024
PACK_PREFIX = "single-disc-endings-csrplus-v0.1.0"
WORK = ROOT / "workspace/iso-extract/collapsed-bases-build"


def _flush_part(part_idx: int, records: list[dict], changed: int, orig_size: int, mod_size: int) -> Path:
    pack_id = f"{PACK_PREFIX}-part{part_idx}"
    out = ROOT / "builder" / pack_id / "layers" / "disc1.layer.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    layer = {
        "format": "ic-layer-v1",
        "id": f"{pack_id}-disc1",
        "description": f"CSR+ single-disc ending/credits movies on D1 (part {part_idx}). Stack directly on csr-plus-v0.1.0.",
        "target": "disc-image",
        "stats": {
            "originalBytes": orig_size,
            "modifiedBytes": mod_size,
            "changedBytes": changed,
            "records": len(records),
        },
        "records": records,
    }
    out.write_text(json.dumps(layer, indent=2) + "\n", encoding="utf-8")
    mb = out.stat().st_size / (1024 * 1024)
    print(f"WROTE {out.relative_to(ROOT)}  json={mb:.1f}MiB  changed={changed/1024/1024:.1f}MiB  recs={len(records)}")
    if out.stat().st_size >= 100 * 1024 * 1024:
        raise SystemExit(f"part {part_idx} still >= 100 MiB")
    return out


def main() -> int:
    d3 = pristine_bin(3)
    csrplus_layer = CSR / "builder/csr-plus-v0.1.0/layers/disc1.layer.json"
    if not csrplus_layer.is_file():
        print("MISSING", csrplus_layer, file=sys.stderr)
        return 1

    print("1/4 building csr-plus-v0.1.0 base (pre-endings)...")
    base_img = bytearray(pristine_bin(1).read_bytes())
    apply_layer(base_img, json.loads(csrplus_layer.read_text(encoding="utf-8")))
    WORK.mkdir(parents=True, exist_ok=True)
    base_bin = WORK / "csrplus_pre-endings.bin"
    base_bin.write_bytes(base_img)
    print("   ", len(base_img), "bytes")

    print("2/4 applying D3 ending streams (ENDING01/2E/3E)...")
    end_img = bytearray(base_img)
    for line in alias_endings.apply(end_img, d3.read_bytes()):
        print("  ", line)

    sz = len(end_img)
    nsec_img = sz // SECTOR
    free = CD80_SECTORS - nsec_img
    print(f"CD budget size={sz} sectors={nsec_img} free80={free}")
    if nsec_img > CD80_SECTORS:
        print("FAIL: over 80-min sector budget", file=sys.stderr)
        return 3

    print("3/4 checking MINT/MOVIE_ID.BIN for LBA collisions...")
    # csr-plus keeps the vanilla movie layout (no manip-movies relocation), so
    # ENDING2E's hardcoded-LBA stream unavoidably overwrites other D1 movie
    # files' bytes. Per project decision, CSR+ single-disc doesn't need any
    # D1/D2/D3 movies to play correctly except the endings themselves --
    # those overwritten cutscenes going glitchy/wrong-clip is accepted (see
    # README beta notes), not a build blocker. Reported as a warning only.
    errors = check_movie_id_collisions(bytes(end_img))
    if errors:
        print(f"WARNING: {len(errors)} movie id LBA collision(s) found (expected -- "
              "non-ending movies are not needed for CSR+ single-disc):")
        for e in errors:
            print("  -", e)
    else:
        print("    no movie id LBA collisions")

    end_bin = WORK / "csrplus_with-endings.bin"
    end_bin.write_bytes(end_img)

    print("4/4 diffing vs csr-plus-v0.1.0 base into parts...")
    orig_size = base_bin.stat().st_size
    mod_size = end_bin.stat().st_size
    part = 1
    records: list[dict] = []
    changed = 0
    paths: list[Path] = []
    for off, data in iter_runs(base_bin, end_bin):
        piece = len(data)
        if records and changed + piece > MAX_CHANGED_PER_PART:
            paths.append(_flush_part(part, records, changed, orig_size, mod_size))
            part += 1
            records, changed = [], 0
        records.append({"offset": off, "hex": data.hex()})
        changed += piece
    if records:
        paths.append(_flush_part(part, records, changed, orig_size, mod_size))

    meta = ROOT / "builder" / f"{PACK_PREFIX}-PARTS.txt"
    meta.write_text("\n".join(str(p.relative_to(ROOT)) for p in paths) + "\n", encoding="utf-8")
    print("WROTE", meta.relative_to(ROOT))
    print(f"parts={len(paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
