#!/usr/bin/env python3
"""Movie relocation delta for single-disc-on-csr (docs/findings/2026-08-25-movie-relocation-plan.md).

Repoints 3 D1 MOVIE_ID.BIN slots to CSR D2 content and grows the table by
one row for a 4th (FF_DAIKU), since its target id (24/MAINPLR.MOV) is
still live-needed by ROOTMAP:

  id 21 (NORTHMK.MOV slot) <- CSR D2 C_SCENE1.MOV   (JUNAIR conflict: none)
  id 23 (ONTRAIN.MOV slot) <- CSR D2 C_SCENE3.MOV   (conflict: none)
  id 40 (GOLD1.MOV slot)   <- CSR D2 GELNICA.MOV    (JUNAIR field 384)
  id 54 (NEW row)          <- CSR D2 FF_DAIKU.MOV; TRNAD_51 (field 706)
                              tg_d slots 4/5/6/7 PMVIE operand 24->54
                              (leaves id 24/MAINPLR.MOV/ROOTMAP field 143
                              untouched)

All 3 repoint targets are larger than their D1 slot -> EOF append + patch
MOVIE_ID.BIN row (lba/size), matching inject_movies_by_disc_id.py's
force_append path. Table growth follows ship_v026.py's in-place pattern
(MOVIE_ID.BIN stays same LBA; only its own dirent size grows by 20 bytes,
capped at one 2048-byte sector: 55*20=1100 < 2048, safe).

Usage (from repo root):
  python3 mods/single-disc/scripts/ship_movie_relocation_v1.py
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bin_diff_to_layer import build_layer  # noqa: E402
from disc_sources import load_csr_image  # noqa: E402
from field_dat import load_field_dat, op_size  # noqa: E402
from ff7_opcodes import OPCODE_NAMES  # noqa: E402
from lzs import compress_all_with_header, decompress_all_with_header  # noqa: E402
from psx_mode2_iso import (  # noqa: E402
    SECTOR,
    USER,
    extract_file,
    find_file,
    replace_file_within_sectors,
)
from inject_movies_by_disc_id import (  # noqa: E402
    _append_raw_grow,
    _movie_id_meta_by_lba,
    _patch_dirent_lba_size,
    _raw_sectors,
)

VERSION = "0.1.0"
PACK_ID = f"single-disc-movie-relocation-v{VERSION}"
CORE_PACK = "single-disc-on-csr"
COMPATIBLE_BASE = "csr-v0.14.2"

# id -> CSR D2 source movie name (same-id repoint; slot grows via EOF append)
REPOINTS = {21: "C_SCENE1.MOV", 23: "C_SCENE3.MOV", 40: "GELNICA.MOV"}
GROW_MOVIE = "FF_DAIKU.MOV"
GROW_NEW_ID = 54
PMVIE_REMAP = {24: GROW_NEW_ID}
# tg_d slots 3-31 all alias ONE physical script blob (field_dat dedup: many
# (entity, slot) table entries point at the same raw bytes) -- confirmed by
# byte-identical s.raw + identical decompressed offset across slots 3..31.
# So there is exactly 1 physical PMVIE 24 occurrence to patch, not one per
# slot number.
TRNAD_51_PMVIE24_OCCURRENCES_EXPECTED = 1


def install_grow_movie_id(img: bytearray, new_row_count: int) -> None:
    mid_meta = find_file(bytes(img), "MINT/MOVIE_ID.BIN")
    blob = bytearray(extract_file(bytes(img), "MINT/MOVIE_ID.BIN"))
    want = new_row_count * 20
    if want > USER:
        raise SystemExit(f"MOVIE_ID.BIN grown table ({want}B) exceeds one sector ({USER}B)")
    if len(blob) < want:
        blob.extend(b"\x00" * (want - len(blob)))
    replace_file_within_sectors(img, "MINT/MOVIE_ID.BIN", bytes(blob))
    mid2 = find_file(bytes(img), "MINT/MOVIE_ID.BIN")
    if mid2.lba != mid_meta.lba:
        raise SystemExit(f"MOVIE_ID.BIN moved {mid_meta.lba}->{mid2.lba} (must stay in place)")


def repoint_id(img: bytearray, cd2: bytes, movie_id: int, src_name: str) -> None:
    mid_blob = extract_file(bytes(img), "MINT/MOVIE_ID.BIN")
    old_lba, old_eng_size = struct.unpack_from("<II", mid_blob, movie_id * 20)
    d1_path = None
    from inject_movies_by_disc_id import _movie_entries

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
    struct.pack_into("<IIIII", mid_blob := bytearray(extract_file(bytes(img), "MINT/MOVIE_ID.BIN")),
                      movie_id * 20, new_lba, eng_size, a, b, c)
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
    # Append a brand-new dirent for this movie so ISO9660 also lists it.
    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    # Reuse _append_raw_grow's raw-append but need a dirent: create by
    # patching an unused existing MOVIE dirent copy is unsafe; instead
    # append raw sectors directly and only register the LBA/size in
    # MOVIE_ID.BIN (engine resolves via that table, not by filename for
    # PMVIE ids -- confirmed in movie-system.md). No ISO9660 entry needed
    # for the engine path.
    new_lba = len(img) // SECTOR
    img.extend(raw)
    mid_blob = bytearray(extract_file(bytes(img), "MINT/MOVIE_ID.BIN"))
    struct.pack_into("<IIIII", mid_blob, new_id * 20, new_lba, eng_size, a, b, c)
    replace_file_within_sectors(img, "MINT/MOVIE_ID.BIN", bytes(mid_blob))
    print(f"  NEW id {new_id} <- CSR D2 {src_name}: lba={new_lba} eng_size={eng_size} (no dirent; engine-table only)")


def brute_patch_pmvie(dat: bytes, remap: dict[int, int]) -> tuple[bytes, int]:
    """Port of ship_v026.py's PMVIE remapper: rewrite PMVIE operand bytes
    in-place across every script slot without reparsing the whole DAT."""
    fd = load_field_dat(dat)
    buf = bytearray(decompress_all_with_header(dat))
    changed = 0
    search_from = 0
    for s in fd.scripts:
        idx = buf.find(s.raw, search_from)
        if idx < 0:
            idx = buf.find(s.raw)
        if idx < 0:
            continue
        piece = bytearray(s.raw)
        pos = 0
        dirty = False
        while pos < len(piece):
            op = piece[pos]
            sz = max(op_size(piece, pos), 1)
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
            if name == "PMVIE" and len(piece) > pos + 1 and piece[pos + 1] in remap:
                piece[pos + 1] = remap[piece[pos + 1]]
                dirty = True
                changed += 1
            pos += sz
        if dirty:
            buf[idx : idx + len(s.raw)] = piece
        search_from = idx + max(len(s.raw), 1)
    return compress_all_with_header(bytes(buf)), changed


def pmvie_set(dat: bytes) -> set[int]:
    fd = load_field_dat(dat)
    out: set[int] = set()
    for s in fd.scripts:
        pos = 0
        while pos < len(s.raw):
            op = s.raw[pos]
            sz = max(op_size(s.raw, pos), 1)
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
            if name == "PMVIE" and len(s.raw) > pos + 1:
                out.add(s.raw[pos + 1])
            pos += sz
    return out


def main() -> int:
    core_bin = ROOT / "workspace/iso-extract/ff7_d1_singledisc_core.bin"
    if not core_bin.is_file():
        raise SystemExit(
            f"missing {core_bin} -- build it first:\n"
            "  python3 mods/single-disc/scripts/build_singledisc_core_bin.py"
        )
    base_path = core_bin  # diff base for this delta layer

    print("Loading CSR D2 (repoint/grow source) + single-disc core base...")
    cd2 = bytes(load_csr_image(2))
    img = bytearray(core_bin.read_bytes())

    print("\n1/3 Repointing 3 same-id slots (EOF append, no table growth)...")
    for movie_id, name in REPOINTS.items():
        repoint_id(img, cd2, movie_id, name)

    print(f"\n2/3 Growing MOVIE_ID.BIN to id {GROW_NEW_ID} for {GROW_MOVIE}...")
    grow_and_add_row(img, cd2, GROW_NEW_ID, GROW_MOVIE)

    print("\n3/3 Patching TRNAD_51 tg_d PMVIE operand 24 -> %d..." % GROW_NEW_ID)
    trnad_dat = extract_file(cd2, "FIELD/TRNAD_51.DAT")
    before = pmvie_set(trnad_dat)
    if 24 not in before:
        raise SystemExit("TRNAD_51.DAT (CSR D2) has no PMVIE 24 -- source assumption stale")
    new_dat, n = brute_patch_pmvie(trnad_dat, PMVIE_REMAP)
    print(f"  patched {n} PMVIE operand(s) (expected {TRNAD_51_PMVIE24_OCCURRENCES_EXPECTED})")
    if n != TRNAD_51_PMVIE24_OCCURRENCES_EXPECTED:
        raise SystemExit(
            f"expected {TRNAD_51_PMVIE24_OCCURRENCES_EXPECTED} PMVIE 24 occurrence(s), got {n}"
        )
    after = pmvie_set(new_dat)
    if 24 in after:
        raise SystemExit("PMVIE 24 still present after remap")
    if GROW_NEW_ID not in after:
        raise SystemExit(f"PMVIE {GROW_NEW_ID} missing after remap")
    replace_file_within_sectors(img, "FIELD/TRNAD_51.DAT", new_dat)

    print("\nVerify: decode TRNAD_51 from built image matches remap...")
    got = extract_file(bytes(img), "FIELD/TRNAD_51.DAT")
    if pmvie_set(got) != after:
        raise SystemExit("built image TRNAD_51.DAT does not match expected PMVIE set")

    print("\nVerify: ROOTMAP untouched, still resolves id 24 -> MAINPLR.MOV...")
    rootmap_before = extract_file(core_bin.read_bytes(), "FIELD/ROOTMAP.DAT")
    rootmap_after = extract_file(bytes(img), "FIELD/ROOTMAP.DAT")
    if rootmap_before != rootmap_after:
        raise SystemExit("ROOTMAP.DAT changed unexpectedly")
    mid_final = extract_file(bytes(img), "MINT/MOVIE_ID.BIN")
    lba24 = struct.unpack_from("<I", mid_final, 24 * 20)[0]
    from inject_movies_by_disc_id import _movie_entries

    name24 = next((n for n, l, _s in _movie_entries(bytes(img)) if l == lba24), None)
    if name24 != "MAINPLR.MOV":
        raise SystemExit(f"id 24 no longer resolves to MAINPLR.MOV (got {name24})")

    out_dir = ROOT / "workspace/iso-extract"
    out_path = out_dir / "sd_movie_relocation_v1_work.bin"
    out_path.write_bytes(bytes(img))
    print(f"\nWrote {out_path} ({len(img):,} bytes)")

    print("\nBuilding delta layer (base = single-disc core, not CSR D1)...")
    pack_dir = ROOT / "builder" / PACK_ID
    layer_dir = pack_dir / "layers"
    layer_dir.mkdir(parents=True, exist_ok=True)
    layer = build_layer(
        base_path,
        out_path,
        layer_id=PACK_ID + "-disc1",
        description=(
            "Movie relocation v0.1.0: repoint D1 ids 21/23/40 to CSR D2 "
            "C_SCENE1/C_SCENE3/GELNICA; grow MOVIE_ID.BIN to 55 rows for "
            "FF_DAIKU at new id 54; patch TRNAD_51 tg_d PMVIE 24->54 "
            "(leaves ROOTMAP's id 24/MAINPLR.MOV untouched)."
        ),
    )
    layer_path = layer_dir / "disc1.layer.json"
    layer_path.write_text(json.dumps(layer, separators=(",", ":")) + "\n")
    print("layer", layer_path, layer.get("stats"))

    pack = {
        "id": PACK_ID,
        "version": VERSION,
        "name": "(auto) movie relocation",
        "blurb": (
            "Internal auto: JUNAIR/GELNICA + TRNAD_51/C_SCENE1+3+FF_DAIKU "
            "movie fixes, docs/findings/2026-08-25-movie-relocation-plan.md."
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
        "autoIncludeWhen": {"addonSelected": CORE_PACK},
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
        "autoIncludeWhen": {"addonSelected": CORE_PACK},
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
