#!/usr/bin/env python3
"""Movie relocation delta: MD8_5 (#731) dir/Main PMVIE id 53, single-disc.

See docs/findings/2026-08-27-fship12-md8-5-mid53-lba-collision.md.

MD8_5's `dir` entity (index 0), script slot 1 (Main), calls `PMVIE id=53`
right before the 67->731 transition's post-movie game-logic setup. D1's
`MINT/MOVIE_ID.BIN` row 53 has LBA 295563, which belongs to
`/MOVIE/OPENINGE.MOV`'s EOF-appended block (the PARASHOT inject target from
v0.1.4/v0.1.5) -- NOT `/MOVIE/NIVLSFS.MOV` (id 53's actual D1 dirent,
LBA 198348). This is a stale collision left over from the v0.1.4/v0.1.5
inject restore; confirmed present in both the current build and the known-
working reference bin.

Fix: give id 53 its own freshly EOF-appended copy of CSR D2's
`MOVIE/NRCRLB.MOV`, independent of whatever landed at LBA 295563 for
OPENINGE/PARASHOT. Same "repoint in place" pattern as
ship_movie_relocation_fship12_canonht.py's `repoint_id`, just for one id.

Base: single-disc-csr-manip-movies-v0.1.5's output. (Originally chained on
top of a v0.1.6 FSHIP_12/CANONHT pack; that pack was confirmed dead code
and deleted 2026-08-29, so this fix -- a real, unrelated bug -- was
rebuilt directly on v0.1.5's output and reclaimed the v0.1.6 version slot.)

Usage (from repo root):
  python3 mods/single-disc/scripts/ship_movie_relocation_v017_mid53.py
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from disc_sources import load_csr_image  # noqa: E402
from psx_mode2_iso import SECTOR, extract_file, find_file, replace_file_within_sectors  # noqa: E402
from inject_movies_by_disc_id import _append_raw_grow, _movie_id_meta_by_lba, _raw_sectors  # noqa: E402

VERSION = "0.1.6"
PACK_ID = f"single-disc-csr-manip-movies-v{VERSION}"
PARENT_PACK = "single-disc-csr-manip-movies-v0.1.5"
COMPATIBLE_BASE = "csr-v0.14.2"

MOVIE_ID = 53
SRC_NAME = "NRCRLB.MOV"


def build_base_image(root: Path) -> bytearray:
    pristine = root / "workspace/pristine/FINALFANTASY7_D1.bin"
    csr_layer = (root.parent / "Final-Fantasy-7-CSR/builder/csr-v0.14.2/layers/disc1.layer.json").resolve()
    core_layer = root / "builder/single-disc-on-csr/layers/disc1.layer.json"
    movie_layer_v4 = root / "builder/single-disc-csr-manip-movies-v0.1.4/layers/disc1.layer.json"
    movie_layer_v5 = root / "builder/single-disc-csr-manip-movies-v0.1.5/layers/disc1.layer.json"
    img = bytearray(pristine.read_bytes())
    apply_layer(img, json.loads(csr_layer.read_text(encoding="utf-8")))
    apply_layer(img, json.loads(core_layer.read_text(encoding="utf-8")))
    apply_layer(img, json.loads(movie_layer_v4.read_text(encoding="utf-8")))
    apply_layer(img, json.loads(movie_layer_v5.read_text(encoding="utf-8")))
    return img


def main() -> int:
    print("Building base image (CSR + single-disc-on-csr + manip-movies v0.1.4/5)...")
    base_img = build_base_image(ROOT)
    base_bytes = bytes(base_img)
    print("  base", len(base_bytes), "bytes")

    print("Loading CSR D2 (repoint source)...")
    cd2 = bytes(load_csr_image(2))

    img = bytearray(base_bytes)

    mid_blob = extract_file(bytes(img), "MINT/MOVIE_ID.BIN")
    old_lba, _old_size = struct.unpack_from("<II", mid_blob, MOVIE_ID * 20)
    print(f"id {MOVIE_ID} current lba={old_lba} (expect 295563, the OPENINGE collision)")

    # id 53's own D1 dirent is NIVLSFS.MOV -- that's the path whose dirent we
    # repoint (matches the v0.1.4/v0.1.5 slot-reuse convention), even though
    # its MOVIE_ID row's LBA had drifted onto OPENINGE's block.
    d1_path = "MOVIE/NIVLSFS.MOV"
    find_file(bytes(img), d1_path)  # sanity: dirent must exist

    src_meta = find_file(cd2, "MOVIE/" + SRC_NAME)
    raw = _raw_sectors(cd2, src_meta.lba, src_meta.size)
    eng = _movie_id_meta_by_lba(cd2, src_meta.lba)
    if eng is None:
        raise SystemExit(f"no CSR D2 MOVIE_ID row for {SRC_NAME}")
    eng_size, a, b, c = eng

    new_lba = _append_raw_grow(img, d1_path, raw, src_meta.size)
    mid_blob = bytearray(extract_file(bytes(img), "MINT/MOVIE_ID.BIN"))
    struct.pack_into("<IIIII", mid_blob, MOVIE_ID * 20, new_lba, eng_size, a, b, c)
    replace_file_within_sectors(img, "MINT/MOVIE_ID.BIN", bytes(mid_blob))
    print(f"  id {MOVIE_ID} ({d1_path.split('/')[-1]}) <- CSR D2 {SRC_NAME}: lba {old_lba}->{new_lba} eng_size={eng_size}")

    print("\nVerify: MD8_5.DAT / FSHIP_12.DAT untouched (no script bytes changed)...")
    for path in ("FIELD/MD8_5.DAT", "FIELD/FSHIP_12.DAT"):
        if extract_file(base_bytes, path) != extract_file(bytes(img), path):
            raise SystemExit(f"{path} changed unexpectedly")

    print(f"Verify: id {MOVIE_ID} points at fresh {SRC_NAME} content (not OPENINGE)...")
    mid_final = extract_file(bytes(img), "MINT/MOVIE_ID.BIN")
    lba = struct.unpack_from("<I", mid_final, MOVIE_ID * 20)[0]
    got = bytes(img[lba * SECTOR : (lba + 1) * SECTOR])
    want = cd2[src_meta.lba * SECTOR : (src_meta.lba + 1) * SECTOR]
    if got != want:
        raise SystemExit(f"id {MOVIE_ID} raw sector0 does not match CSR D2 {SRC_NAME}")
    opening_meta = find_file(bytes(img), "MOVIE/OPENINGE.MOV")
    if lba == opening_meta.lba:
        raise SystemExit(f"id {MOVIE_ID} still collides with OPENINGE.MOV lba")
    print("  ok")

    out_dir = ROOT / "workspace/iso-extract"
    out_path = out_dir / "sd_movie_relocation_v017_mid53_work.bin"
    out_path.write_bytes(bytes(img))
    print(f"\nWrote {out_path} ({len(img):,} bytes)")

    base_path = out_dir / "sd_movie_relocation_v017_mid53_base.bin"
    base_path.write_bytes(base_bytes)

    print("\nBuilding delta layer (base = manip-movies v0.1.5 output)...")
    pack_dir = ROOT / "builder" / PACK_ID
    layer_dir = pack_dir / "layers"
    layer_dir.mkdir(parents=True, exist_ok=True)
    layer = build_layer(
        base_path,
        out_path,
        layer_id=PACK_ID + "-disc1",
        description=(
            "Movie relocation v0.1.7: MD8_5 (#731) dir/Main PMVIE id 53 -- "
            "repoint to a freshly appended CSR D2 NRCRLB.MOV copy. Id 53's "
            "MOVIE_ID.BIN LBA had drifted onto /MOVIE/OPENINGE.MOV's "
            "appended block (v0.1.4/v0.1.5 inject-restore collision), so "
            "the 67->731 transition movie never played and MD8_5's post-"
            "movie logic desynced."
        ),
    )
    layer_path = layer_dir / "disc1.layer.json"
    layer_path.write_text(json.dumps(layer, separators=(",", ":")) + "\n")
    print("layer", layer_path, layer.get("stats"))

    pack = {
        "id": PACK_ID,
        "version": VERSION,
        "name": "(auto) CSR manip movies delta",
        "blurb": (
            "D2 manip FMVs on D1 (delta pack, applies after manip-movies "
            "v0.1.5). Fixes MD8_5 (#731) PMVIE id 53's LBA collision with "
            "OPENINGE.MOV, which broke the 67->731 transition movie."
        ),
        "hint": "Always with Single-disc.",
        "format": "ic-layer-v1",
        "compatibleBases": [COMPATIBLE_BASE],
        "layout": "global",
        "discs": {"1": "./layers/disc1.layer.json"},
        "enabled": True,
        "uiHidden": True,
        "hidden": True,
        "beta": True,
        "status": "beta",
        "autoIncludeWhen": {"addonSelected": PARENT_PACK},
    }
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2) + "\n")

    man_path = ROOT / "builder/manifest.json"
    man = json.loads(man_path.read_text())
    entry = {
        "id": PACK_ID,
        "name": pack["name"],
        "kind": "mod",
        "version": VERSION,
        "blurb": pack["blurb"],
        "hint": pack["hint"],
        "format": "ic-layer-v1",
        "compatibleBases": [COMPATIBLE_BASE],
        "layout": "global",
        "discs": {"1": "./" + PACK_ID + "/layers/disc1.layer.json"},
        "enabled": True,
        "uiHidden": True,
        "hidden": True,
        "beta": True,
        "status": "beta",
        "autoIncludeWhen": {"addonSelected": PARENT_PACK},
    }
    ids = [a.get("id") for a in man["addons"]]
    if PACK_ID in ids:
        man["addons"] = [entry if a.get("id") == PACK_ID else a for a in man["addons"]]
    else:
        man["addons"].append(entry)
    man_path.write_text(json.dumps(man, indent=2) + "\n")
    print("manifest ok", PACK_ID)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
