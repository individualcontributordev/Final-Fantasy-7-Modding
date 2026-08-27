#!/usr/bin/env python3
"""Movie relocation delta: FSHIP_12 (#67) ad/3 CANONHT triplet, single-disc.

FSHIP_12's `ad` Script 2 (physical slot 3, called via drctr's init REQEW
0x02 -> ad slot 3) plays 3 movies in sequence right before REQ'ing Script 3
(ad slot 4), which does the ASK+MAPJUMP to MD8_5 (#731). This is confirmed
live: drctr's S0-Init/Main REQEWs ad slot 3 and slot 4 directly (not a
REQ/PREQ chain the liveness scanner in scan_sd_movie_requirements.py
follows -- hence its stale "slot_live=False" verdict for this row).

PMVIE ids called (pristine D1 == CSR D1, unchanged by any CSR/SD field-merge
step -- this is retail multi-disc behavior, not a regression):

  PMVIE 0x3b (59) -- OOB on the 54-row D1 MOVIE_ID.BIN table entirely.
  PMVIE 0x32 (50) -- resolves to EARITHDD.MOV on D1 (wrong).
  PMVIE 0x33 (51) -- resolves to FUNERAL.STR on D1 (wrong, and a still-image
                     .STR, not a movie).

On retail multi-disc this scene only plays correctly with D2 inserted; CSR
D2's own MOVIE_ID.BIN row for these same 3 ids resolves to the Highwind
Junon-cannon-assault CANONHT triplet:

  id 50 -> CANONHT1.MOV
  id 51 -> CANONHT2.MOV
  id 59 -> CANONH1P.MOV

Fix: repoint D1 ids 50/51 in place (EOF append, both sources larger than
their current D1 slot) and grow MOVIE_ID.BIN to 60 rows for a new id 59
(CANONH1P.MOV) -- same "same-id repoint + table growth" pattern as
ship_movie_relocation_v010.py, just no PMVIE remap needed here since all 3
ids the script already calls (59/50/51) become directly resolvable; no
field script bytes change.

Base: single-disc-csr-manip-movies-v0.1.5's output (top of the current
manip-movies layer chain -- see build_playtest_bin.py), NOT the CSR base,
since ids 21/23/40 (from v010) and 47/53/52 (seed) are already relocated
there and must not be clobbered.

Usage (from repo root):
  python3 mods/single-disc/scripts/ship_movie_relocation_fship12_canonht.py
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
from psx_mode2_iso import extract_file, find_file, replace_file_within_sectors  # noqa: E402
from inject_movies_by_disc_id import (  # noqa: E402
    _append_raw_grow,
    _movie_entries,
    _movie_id_meta_by_lba,
    _raw_sectors,
)
from ship_movie_relocation_v010 import install_grow_movie_id  # noqa: E402

VERSION = "0.1.6"
PACK_ID = f"single-disc-csr-manip-movies-v{VERSION}"
PARENT_PACK = "single-disc-csr-manip-movies-v0.1.5"
CORE_PACK = "single-disc-on-csr"
COMPATIBLE_BASE = "csr-v0.14.2"

REPOINTS = {50: "CANONHT1.MOV", 51: "CANONHT2.MOV"}
GROW_MOVIE = "CANONH1P.MOV"
GROW_NEW_ID = 59


def repoint_id(img: bytearray, cd2: bytes, movie_id: int, src_name: str) -> None:
    mid_blob = extract_file(bytes(img), "MINT/MOVIE_ID.BIN")
    old_lba, _old_eng_size = struct.unpack_from("<II", mid_blob, movie_id * 20)
    d1_path = None
    for name, lba, _sz in _movie_entries(bytes(img)):
        if lba == old_lba:
            d1_path = "MOVIE/" + name
            break
    if d1_path is None:
        raise SystemExit(f"no D1 dirent for MOVIE_ID row {movie_id} lba={old_lba}")

    src_meta = find_file(cd2, "MOVIE/" + src_name)
    raw = _raw_sectors(cd2, src_meta.lba, src_meta.size)
    eng = _movie_id_meta_by_lba(cd2, src_meta.lba)
    if eng is None:
        raise SystemExit(f"no CSR D2 MOVIE_ID row for {src_name}")
    eng_size, a, b, c = eng

    new_lba = _append_raw_grow(img, d1_path, raw, src_meta.size)
    mid_blob = bytearray(extract_file(bytes(img), "MINT/MOVIE_ID.BIN"))
    struct.pack_into("<IIIII", mid_blob, movie_id * 20, new_lba, eng_size, a, b, c)
    replace_file_within_sectors(img, "MINT/MOVIE_ID.BIN", bytes(mid_blob))
    print(f"  id {movie_id} ({d1_path.split('/')[-1]}) <- CSR D2 {src_name}: lba {old_lba}->{new_lba} eng_size={eng_size}")


def grow_and_add_row(img: bytearray, cd2: bytes, new_id: int, src_name: str) -> None:
    install_grow_movie_id(img, new_id + 1)
    src_meta = find_file(cd2, "MOVIE/" + src_name)
    raw = _raw_sectors(cd2, src_meta.lba, src_meta.size)
    eng = _movie_id_meta_by_lba(cd2, src_meta.lba)
    if eng is None:
        raise SystemExit(f"no CSR D2 MOVIE_ID row for {src_name}")
    eng_size, a, b, c = eng
    from psx_mode2_iso import SECTOR

    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    new_lba = len(img) // SECTOR
    img.extend(raw)
    mid_blob = bytearray(extract_file(bytes(img), "MINT/MOVIE_ID.BIN"))
    struct.pack_into("<IIIII", mid_blob, new_id * 20, new_lba, eng_size, a, b, c)
    replace_file_within_sectors(img, "MINT/MOVIE_ID.BIN", bytes(mid_blob))
    print(f"  NEW id {new_id} <- CSR D2 {src_name}: lba={new_lba} eng_size={eng_size} (no dirent; engine-table only)")


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
    print("Building base image (CSR + single-disc-on-csr + manip-movies v0.1.4/v0.1.5)...")
    base_img = build_base_image(ROOT)
    base_bytes = bytes(base_img)
    print("  base", len(base_bytes), "bytes")

    print("Loading CSR D2 (repoint/grow source)...")
    cd2 = bytes(load_csr_image(2))

    img = bytearray(base_bytes)

    print("\n1/2 Repointing 2 same-id slots (EOF append)...")
    for movie_id, name in REPOINTS.items():
        repoint_id(img, cd2, movie_id, name)

    print(f"\n2/2 Growing MOVIE_ID.BIN to id {GROW_NEW_ID} for {GROW_MOVIE}...")
    grow_and_add_row(img, cd2, GROW_NEW_ID, GROW_MOVIE)

    print("\nVerify: FSHIP_12.DAT untouched (no script bytes changed)...")
    fship_before = extract_file(base_bytes, "FIELD/FSHIP_12.DAT")
    fship_after = extract_file(bytes(img), "FIELD/FSHIP_12.DAT")
    if fship_before != fship_after:
        raise SystemExit("FSHIP_12.DAT changed unexpectedly")

    print("Verify: ids 50/51/59 point at CANONHT1/CANONHT2/CANONH1P content...")
    # Dirents keep their D1 slot name (EARITHDD.MOV / FUNERAL.STR) -- only the
    # LBA is repointed, same convention as the NRCRLB->NIVLSFS slot reuse.
    # Verify by raw sector bytes at the new LBA against CSR D2's source.
    from psx_mode2_iso import SECTOR

    mid_final = extract_file(bytes(img), "MINT/MOVIE_ID.BIN")
    for mid, want in ((50, "CANONHT1.MOV"), (51, "CANONHT2.MOV")):
        lba = struct.unpack_from("<I", mid_final, mid * 20)[0]
        src_meta = find_file(cd2, "MOVIE/" + want)
        got = bytes(img[lba * SECTOR : (lba + 1) * SECTOR])
        want_raw = cd2[src_meta.lba * SECTOR : (src_meta.lba + 1) * SECTOR]
        if got != want_raw:
            raise SystemExit(f"id {mid} raw sector0 does not match CSR D2 {want}")
    lba59 = struct.unpack_from("<I", mid_final, 59 * 20)[0]
    src_meta = find_file(cd2, "MOVIE/" + GROW_MOVIE)
    got59 = bytes(img[lba59 * SECTOR : (lba59 + 1) * SECTOR])
    want59 = cd2[src_meta.lba * SECTOR : (src_meta.lba + 1) * SECTOR]
    if got59 != want59:
        raise SystemExit("id 59 raw sector0 does not match CSR D2 CANONH1P.MOV")
    print("  ok")

    out_dir = ROOT / "workspace/iso-extract"
    out_path = out_dir / "sd_movie_relocation_fship12_canonht_work.bin"
    out_path.write_bytes(bytes(img))
    print(f"\nWrote {out_path} ({len(img):,} bytes)")

    base_path = out_dir / "sd_movie_relocation_fship12_canonht_base.bin"
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
            "Movie relocation v0.1.6: FSHIP_12 (#67) ad/3 CANONHT triplet -- "
            "repoint D1 ids 50/51 to CSR D2 CANONHT1/CANONHT2; grow "
            "MOVIE_ID.BIN to 60 rows for CANONH1P at new id 59 (OOB on "
            "retail D1's 54-row table). Fixes 67->731 (MD8_5) transition "
            "skipping its background movies and desyncing field logic."
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
            "v0.1.5). Fixes FSHIP_12 (#67) ad/3 CANONHT1/CANONHT2/CANONH1P "
            "movie ids (59 was OOB; 50/51 pointed at wrong D1 content), "
            "which broke the 67->731 (MD8_5) transition timing."
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
