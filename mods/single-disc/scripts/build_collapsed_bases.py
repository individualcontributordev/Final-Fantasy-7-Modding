#!/usr/bin/env python3
"""Build ONE collapsed disc1.layer.json each for the csr-plus and highwind
single-disc bases (excluding the large ending-movie payloads, which stay
chunked separately for GitHub's 100MB/file limit).

Collapses, in order, onto Disc 1:
  csr-plus:
    CSR D1 (v0.14.2) -> rework/safe FIELD merges (D2/D3->D1, CSR's own
    single-disc core) -> JUNAIR precision patch -> BLACKBGB DSKCG (ask)
    removal -> CSR+ scene trims (Hojo, Aerith house, Endgame) -> FIELD.BIN/
    WORLD.BIN table fix -> SNOVA D3->D1 inject.
  highwind:
    Highwind D1 (v0.2.0) -> Highwind D2/D3 FIELD merge (existing merge
    list) -> BLACKBGB ask-removal (borrowed from the finished csr-plus
    image, since the byte content is disc/version-agnostic) -> CSR+ scene
    trims (same 3, injected from CSR D2/D3-with-trim source) -> table fix
    -> SNOVA inject.

"Manip movies" and "movie relocation" are intentionally NOT folded in --
CSR+/Highwind keep vanilla intro/multi-disc FMVs.

Usage (repo root):
  python3 mods/single-disc/scripts/build_collapsed_bases.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from disc_sources import csr_root, load_csr_image, pristine_bin  # noqa: E402
from psx_mode2_iso import extract_file, find_file, replace_file_within_sectors  # noqa: E402

from merge_rework_fields import SLOT_SPLICE_FIELDS, WHOLE_FILE_FIELDS, merge_slots  # noqa: E402
from merge_safe_fields import find_safe_whole_file_merges  # noqa: E402
from scan_all_field_collisions import list_field_dir  # noqa: E402
from fix_field_bin_table import fix_field_and_world_bins  # noqa: E402
from fix_junair_air0_slot3 import fix_junair  # noqa: E402
from build_work_bin import apply_manual_blackbgb  # noqa: E402

CSR = csr_root()
PRISTINE_D1 = pristine_bin(1)
WORK = ROOT / "workspace/iso-extract/collapsed-bases-build"

# Hojo/Endgame trims only ship a disc2/disc3 layer -- the trimmed field is
# extracted from that (already-CSR) disc image. Aerith house only ships a
# disc1.layer.json (diffed directly against CSR D1), so it's applied as a
# byte-offset patch instead of extracted from another disc.
CSRPLUS_TRIMS_FROM_DISC = [
    {"id": "csr-plus-scene-hojo-fd-manip-v0.1.0", "src_disc": 2,
     "files": ["FIELD/BLIN66_6.DAT", "FIELD/CANON_2.DAT", "FIELD/FSHIP_24.DAT"]},
    {"id": "csr-plus-scene-endgame-fd-manip-v0.1.0", "src_disc": 3,
     "files": ["FIELD/LAS0_3.DAT", "FIELD/LAS4_0.DAT", "FIELD/LAS2_1.DAT", "FIELD/LAS4_1.DAT"]},
]
CSRPLUS_TRIM_DISC1 = {"id": "csr-plus-scene-aerith-house-v0.1.1", "files": ["FIELD/EALS_1.DAT"]}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def trim_source_image(pack_id: str, src_disc: int) -> bytearray:
    img = load_csr_image(src_disc)
    layer = CSR / f"builder/{pack_id}/layers/disc{src_disc}.layer.json"
    apply_layer(img, load_json(layer))
    return img


def _inject_one(img: bytearray, pack_id: str, path: str, data: bytes, log: list[str]) -> None:
    before = find_file(img, path)
    replace_file_within_sectors(img, path, data)
    got = extract_file(img, path)
    if got != data:
        raise RuntimeError(f"{pack_id} {path}: inject mismatch")
    log.append(f"{pack_id} {path}: {before.size} -> {len(data)}")


def inject_trims(img: bytearray) -> list[str]:
    log: list[str] = []
    for trim in CSRPLUS_TRIMS_FROM_DISC:
        src = trim_source_image(trim["id"], trim["src_disc"])
        for path in trim["files"]:
            _inject_one(img, trim["id"], path, extract_file(src, path), log)

    # Aerith house: disc1-only layer, diffed directly against CSR D1 baseline.
    aerith = CSRPLUS_TRIM_DISC1
    baseline = bytes(load_csr_image(1))
    aerith_img = bytearray(baseline)
    apply_layer(
        aerith_img,
        load_json(CSR / f"builder/{aerith['id']}/layers/disc1.layer.json"),
    )
    for path in aerith["files"]:
        _inject_one(img, aerith["id"], path, extract_file(aerith_img, path), log)
    return log


def build_csrplus_core() -> bytearray:
    print("=== csr-plus: base + core merges ===")
    c1 = bytes(load_csr_image(1))
    c2 = bytes(load_csr_image(2))
    img = bytearray(c1)

    print("Applying 8-field rework merge...")
    for field, disc in WHOLE_FILE_FIELDS.items():
        src = c1 if disc == 1 else c2
        path = f"FIELD/{field}.DAT"
        replace_file_within_sectors(img, path, extract_file(src, path))
    for field, slot_discs in SLOT_SPLICE_FIELDS.items():
        merge_slots(img, field, slot_discs, c1, c2)

    print("Applying bulk safe-field merge...")
    merges = find_safe_whole_file_merges()
    src_imgs = {2: bytes(load_csr_image(2)), 3: bytes(load_csr_image(3))}
    for field, disc in sorted(merges.items()):
        path = f"FIELD/{field}.DAT"
        data = extract_file(src_imgs[disc], path)
        if data != extract_file(img, path):
            replace_file_within_sectors(img, path, data)

    print("JUNAIR air0/3 precision patch...")
    fix_junair(img)

    print("BLACKBGB DSKCG (ask) removal...")
    blackbgb_diff = ROOT / "mods/single-disc/patches/BLACKBGB.dskcg-removal.layer.json"
    apply_manual_blackbgb(img, blackbgb_diff)

    print("Injecting CSR+ scene trims (Hojo, Aerith house, Endgame)...")
    for line in inject_trims(img):
        print(f"  {line}")

    return img


def finish_and_diff(img: bytearray, out_dir: Path, layer_id: str, description: str) -> None:
    print("Patching FIELD.BIN/WORLD.BIN tables...")
    fixed = fix_field_and_world_bins(img)
    print(f"  entries patched: {fixed}")

    WORK.mkdir(parents=True, exist_ok=True)
    work_bin = WORK / f"{layer_id}_pre-snova.bin"
    work_bin.write_bytes(img)

    print("Injecting SNOVA D3 -> D1...")
    snova_script = Path(__file__).resolve().parent / "inject_snova_d3_to_d1.py"
    subprocess.check_call(
        [sys.executable, str(snova_script), "--d1", str(work_bin), "--d3", str(pristine_bin(3)), "--in-place"],
        cwd=str(ROOT),
    )

    print("Diffing vs pristine D1...")
    layer = build_layer(PRISTINE_D1, work_bin, layer_id=layer_id, description=description)
    write_json(out_dir / "disc1.layer.json", layer)
    print(f"wrote {out_dir/'disc1.layer.json'} records={layer['stats']['records']} bytes={layer['stats']['changedBytes']}")


def find_highwind_safe_merges(hw1: bytes, hw2: bytes, hw3: bytes) -> dict[str, int]:
    """{field: disc} for every field present on 2+ Highwind discs where
    exactly one of D2/D3 differs from D1 (true single-disc-edit fields).
    Fields where BOTH D2 and D3 differ from D1 (and from each other) are
    genuine collisions -- logged and skipped rather than guessed at."""
    listings = {1: list_field_dir(hw1), 2: list_field_dir(hw2), 3: list_field_dir(hw3)}
    all_names = sorted(set(listings[1]) | set(listings[2]) | set(listings[3]))
    imgs = {1: hw1, 2: hw2, 3: hw3}
    out: dict[str, int] = {}
    for name in all_names:
        present = [d for d in (1, 2, 3) if name in listings[d]]
        if 1 not in present or len(present) < 2:
            continue
        path = f"FIELD/{name}.DAT"
        d1_data = extract_file(imgs[1], path)
        diffs = [d for d in present if d != 1 and extract_file(imgs[d], path) != d1_data]
        if len(diffs) == 1:
            out[name] = diffs[0]
        elif len(diffs) > 1:
            print(f"  COLLISION (skipped, needs manual verdict): {name} differs on {diffs}")
    return out


def build_highwind(csrplus_final_bin: Path) -> None:
    print("\n=== highwind: base + own D2/D3 merge ===")
    hw1 = bytearray(pristine_bin(1).read_bytes())
    apply_layer(hw1, load_json(CSR / "builder/highwind-v0.2.0/layers/disc1.layer.json"))
    hw2 = bytearray(pristine_bin(2).read_bytes())
    apply_layer(hw2, load_json(CSR / "builder/highwind-v0.2.0/layers/disc2.layer.json"))
    hw3 = bytearray(pristine_bin(3).read_bytes())
    apply_layer(hw3, load_json(CSR / "builder/highwind-v0.2.0/layers/disc3.layer.json"))

    merges = find_highwind_safe_merges(bytes(hw1), bytes(hw2), bytes(hw3))
    print(f"  HW D2/D3 safe merges found: {len(merges)}")

    img = bytearray(hw1)
    n_ok = n_skip = 0
    for name, disc in sorted(merges.items()):
        path = f"FIELD/{name}.DAT"
        src = hw2 if disc == 2 else hw3
        data = extract_file(src, path)
        try:
            replace_file_within_sectors(img, path, data)
            n_ok += 1
        except ValueError as e:
            print(f"  FAIL {path}: {e}")
            n_skip += 1
    print(f"  HW D2/D3 merge: ok={n_ok} skip={n_skip}")

    print("Borrowing finished BLACKBGB.DAT from csr-plus core...")
    csrplus_final = bytearray(csrplus_final_bin.read_bytes())
    data = extract_file(csrplus_final, "FIELD/BLACKBGB.DAT")
    replace_file_within_sectors(img, "FIELD/BLACKBGB.DAT", data)

    print("Injecting CSR+ scene trims (Hojo, Aerith house, Endgame)...")
    for line in inject_trims(img):
        print(f"  {line}")

    out_dir = CSR / "builder/highwind-v0.3.0/layers"
    finish_and_diff(
        img, out_dir,
        layer_id="highwind-v0.3.0-disc1",
        description="Highwind single-disc: D2/D3 FIELD merge + CSR+ trims + ask-removal + SNOVA, collapsed",
    )


def main() -> None:
    csrplus_final_bin = WORK / "csr-plus-v0.1.0-disc1_pre-snova.bin"
    csrplus_layer = CSR / "builder/csr-plus-v0.1.0/layers/disc1.layer.json"
    if "--skip-csrplus" in sys.argv and csrplus_final_bin.is_file() and csrplus_layer.is_file():
        print("=== csr-plus: skipped (--skip-csrplus, using existing build) ===")
    else:
        core = build_csrplus_core()
        WORK.mkdir(parents=True, exist_ok=True)
        core_bin = WORK / "csrplus_core_pre-table-fix.bin"
        core_bin.write_bytes(core)

        out_dir = csrplus_layer.parent
        finish_and_diff(
            core, out_dir,
            layer_id="csr-plus-v0.1.0-disc1",
            description="CSR+ single-disc: CSR core merges + scene trims + ask-removal + SNOVA, collapsed",
        )

    build_highwind(csrplus_final_bin)
    print("\nDONE")


if __name__ == "__main__":
    main()
