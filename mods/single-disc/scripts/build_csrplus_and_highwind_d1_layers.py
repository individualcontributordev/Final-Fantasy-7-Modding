#!/usr/bin/env python3
"""Build disc1 layers for CSR+ scene packs so single-disc D1 stacks get D2/D3 trims.

Why: CSR+ packs only shipped disc2/disc3 layers. A Disc 1 single-disc build never
applied Hojo/COTA/endgame. This writes disc1.layer.json by injecting the CSR+
FIELD maps from the retail disc into a CSR+single-disc D1 baseline, then
bin-diffing.

Also rebuilds Highwind single-disc main option by merging HW D2/D3 FIELD bytes
that differ from HW D1 into D1 (sector-safe grow).

Usage (repo root):
  python3 mods/single-disc/scripts/build_csrplus_and_highwind_d1_layers.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from disc_sources import csr_root, load_csr_image, pristine_bin  # noqa: E402
from psx_mode2_iso import (  # noqa: E402
    extract_file,
    find_file,
    replace_file_within_sectors,
)

CSR = csr_root()
PRISTINE_D1 = pristine_bin(1)

CSRPLUS_PACKS = [
    {
        "id": "csr-plus-scene-hojo-fd-manip-v0.1.0",
        "src_disc": 2,
        "files": ["FIELD/BLIN66_6.DAT", "FIELD/CANON_2.DAT", "FIELD/FSHIP_24.DAT"],
    },
    {
        "id": "csr-plus-scene-cota-fd-manip-v0.1.0",
        "src_disc": 2,
        "files": ["FIELD/BLIN70_4.DAT", "FIELD/LOSLAKE1.DAT"],
    },
    {
        "id": "csr-plus-scene-endgame-fd-manip-v0.1.0",
        "src_disc": 3,
        "files": [
            "FIELD/LAS0_3.DAT",
            "FIELD/LAS4_0.DAT",
            "FIELD/LAS2_1.DAT",
            "FIELD/LAS4_1.DAT",
        ],
    },
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def csr_sd_d1_baseline() -> bytearray:
    img = bytearray(PRISTINE_D1.read_bytes())
    apply_layer(img, load_json(CSR / "builder/csr-v0.14.1/layers/disc1.layer.json"))
    apply_layer(
        img,
        load_json(ROOT / "builder/single-disc-on-csr-v0.1.2/layers/disc1.layer.json"),
    )
    return img


def csrplus_source_image(pack_id: str, src_disc: int) -> bytearray:
    img = load_csr_image(src_disc)
    layer = CSR / f"builder/{pack_id}/layers/disc{src_disc}.layer.json"
    apply_layer(img, load_json(layer))
    return img


def inject_files(dst: bytearray, src: bytearray, files: list[str]) -> list[str]:
    log = []
    for path in files:
        data = extract_file(src, path)
        before = find_file(dst, path)
        replace_file_within_sectors(dst, path, data)
        after = find_file(dst, path)
        got = extract_file(dst, path)
        if got != data:
            raise RuntimeError(f"{path}: inject mismatch")
        log.append(f"{path}: {before.size} -> {after.size}")
    return log


def build_csrplus_disc1_layers() -> None:
    base = csr_sd_d1_baseline()
    out_base = ROOT / "workspace/iso-extract/csrplus-d1-build"
    out_base.mkdir(parents=True, exist_ok=True)
    base_path = out_base / "baseline_csr_sd_d1.bin"
    base_path.write_bytes(base)
    print("baseline", base_path, len(base))

    for pack in CSRPLUS_PACKS:
        pid = pack["id"]
        src = csrplus_source_image(pid, pack["src_disc"])
        img = bytearray(base)
        for line in inject_files(img, src, pack["files"]):
            print(f"  {pid}: {line}")
        mod_path = out_base / f"{pid}_d1.bin"
        mod_path.write_bytes(img)
        layer = build_layer(
            base_path,
            mod_path,
            layer_id=f"{pid}-disc1",
            description=f"{pid} FIELD maps on single-disc D1 (from disc {pack['src_disc']})",
        )
        dest = CSR / f"builder/{pid}/layers/disc1.layer.json"
        write_json(dest, layer)
        # pack.json discs
        pp = CSR / f"builder/{pid}/pack.json"
        pj = load_json(pp)
        discs = dict(pj.get("discs") or {})
        discs["1"] = "./layers/disc1.layer.json"
        pj["discs"] = discs
        write_json(pp, pj)
        print(f"wrote {dest} records={layer['stats']['records']} bytes={layer['stats']['changedBytes']}")


def highwind_image(disc: int) -> bytearray:
    img = bytearray(pristine_bin(disc).read_bytes())
    apply_layer(
        img,
        load_json(CSR / f"builder/highwind-v0.2.0/layers/disc{disc}.layer.json"),
    )
    return img


def build_highwind_single_disc() -> None:
    """Merge HW D2/D3 FIELD files that differ from HW D1 onto a HW D1 image + SNOVA-less SD trims.

    Starts from HW D1 + copies of single-disc-on-csr Ask/SNOVA pieces are HW-specific;
    for now inject FIELD maps from HW D2/D3 where bytes differ and fit sectors.
    Also copy single-disc Ask removals are already in CSR SD pack — for HW we rebuild
    from HW D1 and apply CSR SD layer may fight HW. Safer: only FIELD merge D2/D3→D1.
    """
    from psx_mode2_iso import extract_file as ex

    hw1 = highwind_image(1)
    hw2 = highwind_image(2)
    hw3 = highwind_image(3)
    # candidates: all FIELD/*.DAT on d2/d3 that exist on d1 and differ
    from psx_mode2_iso import find_file

    def list_field_names(img: bytearray) -> list[str]:
        # walk FIELD dir via finding known set from csr merge list
        return []

    merge_list = Path(ROOT / "mods/single-disc/patches/csr-d2d3-field-merge-on-d1.md")
    # parse FIELD paths from table
    paths = []
    for line in merge_list.read_text().splitlines():
        if "FIELD/" not in line or not line.strip().startswith("|"):
            continue
        # | D2 | FIELD/X.DAT | ...
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 2 and parts[1].startswith("FIELD/") and parts[1].endswith(".DAT"):
            if parts[0] in ("D2", "D3") and "FIELD.BIN" not in parts[1]:
                paths.append((parts[0], parts[1]))
    print("merge candidates", len(paths))

    base = bytearray(hw1)
    base_path = ROOT / "workspace/iso-extract/hw_sd_build/baseline_hw_d1.bin"
    base_path.parent.mkdir(parents=True, exist_ok=True)
    base_path.write_bytes(base)

    img = bytearray(base)
    n_ok = n_skip = 0
    for disc_label, path in paths:
        src = hw2 if disc_label == "D2" else hw3
        try:
            data = ex(src, path)
            slot = find_file(img, path)
        except Exception as e:
            print("skip missing", path, e)
            n_skip += 1
            continue
        if data == ex(img, path):
            continue
        try:
            replace_file_within_sectors(img, path, data)
            n_ok += 1
            print(f"  HW {disc_label} {path}: {slot.size} -> {len(data)}")
        except ValueError as e:
            print(f"  FAIL {path}: {e}")
            n_skip += 1

    # Apply single-disc essentials: use CSR SD layer on top may break HW maps —
    # Instead take BLACKBGB ask-free from CSR SD if exists.
    csr_sd = bytearray(Path("workspace/pristine/FINALFANTASY7_D1.bin").read_bytes())
    apply_layer(csr_sd, load_json(CSR / "builder/csr-v0.14.1/layers/disc1.layer.json"))
    apply_layer(
        csr_sd,
        load_json(ROOT / "builder/single-disc-on-csr-v0.1.2/layers/disc1.layer.json"),
    )
    for must in ["FIELD/BLACKBGB.DAT"]:
        try:
            data = ex(csr_sd, must)
            replace_file_within_sectors(img, must, data)
            print(f"  borrow {must} from CSR SD ask-removal")
        except Exception as e:
            print("  borrow fail", must, e)

    # SNOVA inject for highwind single-disc
    from importlib.util import spec_from_loader, module_from_spec
    # call inject script
    snova = ROOT / "mods/single-disc/scripts/inject_snova_d3_to_d1.py"
    mod_path = ROOT / "workspace/iso-extract/hw_sd_build/hw_sd_work.bin"
    mod_path.write_bytes(img)
    import subprocess

    # inject needs pristine d3 and may grow image
    try:
        subprocess.check_call(
            [
                sys.executable,
                str(snova),
                "--d1",
                str(mod_path),
                "--d3",
                str(pristine_bin(3)),
                "--in-place",
            ],
            cwd=str(ROOT),
        )
    except subprocess.CalledProcessError as e:
        print("SNOVA inject failed (may already present):", e)

    # layer vs pristine d1+highwind only? For builder, base is highwind so layer =
    # diff(hw_d1, hw_d1+merges+snova)
    final = bytearray(mod_path.read_bytes())
    # baseline for layer must match builder base image = pristine+hw d1 layer (fixed size?)
    # SNOVA grows image — same as CSR SD
    bl = highwind_image(1)
    bl_path = ROOT / "workspace/iso-extract/hw_sd_build/baseline_hw_d1_only.bin"
    bl_path.write_bytes(bl)
    fin_path = ROOT / "workspace/iso-extract/hw_sd_build/hw_sd_final.bin"
    fin_path.write_bytes(final)

    layer = build_layer(
        bl_path,
        fin_path,
        layer_id="single-disc-on-highwind-v0.1.0-disc1",
        description="Single-disc for Highwind: D2/D3 FIELD merge + SNOVA + ask fix",
    )
    out_dir = ROOT / "builder/single-disc-on-highwind-v0.1.0/layers"
    write_json(out_dir / "disc1.layer.json", layer)
    pack = {
        "id": "single-disc-on-highwind-v0.1.0",
        "name": "Single-disc",
        "kind": "mod",
        "version": "0.1.0",
        "blurb": (
            "Play the whole game from one Disc 1 image on Highwind. "
            "Merges Highwind Disc 2/3 field maps onto Disc 1 and adds Supernova. "
            "Ending/credits movies auto-apply with this option."
        ),
        "hint": "Use one Disc 1 image for the full Highwind game.",
        "format": "ic-layer-v1",
        "compatibleBases": ["highwind-v0.2.0"],
        "layout": "global",
        "discs": {"1": "./layers/disc1.layer.json"},
    }
    write_json(ROOT / "builder/single-disc-on-highwind-v0.1.0/pack.json", pack)
    print(
        f"Highwind SD layer records={layer['stats']['records']} "
        f"changed={layer['stats']['changedBytes']} ok={n_ok} skip={n_skip}"
    )


def update_csr_manifest_discs() -> None:
    man = CSR / "builder/manifest.json"
    m = load_json(man)
    for a in m.get("addons", []):
        for pack in CSRPLUS_PACKS:
            if a.get("id") == pack["id"]:
                discs = dict(a.get("discs") or {})
                discs["1"] = f"./{pack['id']}/layers/disc1.layer.json"
                a["discs"] = discs
                print("manifest discs", pack["id"], discs)
    write_json(man, m)


def update_modding_manifest_highwind_sd() -> None:
    man = ROOT / "builder/manifest.json"
    m = load_json(man)
    aid = "single-disc-on-highwind-v0.1.0"
    entry = {
        "id": aid,
        "name": "Single-disc",
        "kind": "mod",
        "blurb": (
            "Play the whole game from one Disc 1 image on Highwind. "
            "Field maps from Highwind discs 2 and 3 are included. Ending movies auto-apply."
        ),
        "hint": "Use one Disc 1 image for the full Highwind game.",
        "format": "ic-layer-v1",
        "compatibleBases": ["highwind-v0.2.0"],
        "layout": "global",
        "discs": {
            "1": f"./single-disc-on-highwind-v0.1.0/layers/disc1.layer.json",
        },
        "enabled": True,
    }
    ids = {a["id"] for a in m["addons"]}
    if aid in ids:
        m["addons"] = [entry if a["id"] == aid else a for a in m["addons"]]
    else:
        # after single-disc-on-csr-v0.1.2
        idx = next(
            (i for i, a in enumerate(m["addons"]) if a["id"] == "single-disc-on-csr-v0.1.2"),
            len(m["addons"]) - 1,
        )
        m["addons"].insert(idx + 1, entry)
    # endings autoInclude also for highwind when this SD selected
    for a in m["addons"]:
        if str(a.get("id", "")).startswith("single-disc-endings-v0.1.0-part"):
            rule = dict(a.get("autoIncludeWhen") or {})
            # support either single-disc on csr OR highwind
            sel = rule.get("addonSelected")
            # switch to multi if needed
            if "addonSelectedAny" not in rule:
                rule["addonSelectedAny"] = [
                    "single-disc-on-csr-v0.1.2",
                    "single-disc-on-highwind-v0.1.0",
                ]
                rule.pop("addonSelected", None)
            bases = list(rule.get("bases") or ["csr-v0.14.1", "highwind-v0.2.0"])
            if "highwind-v0.2.0" not in bases:
                bases.append("highwind-v0.2.0")
            rule["bases"] = bases
            a["autoIncludeWhen"] = rule
    write_json(man, m)
    print("modding manifest updated")


def main() -> None:
    print("=== CSR+ disc1 layers ===")
    build_csrplus_disc1_layers()
    update_csr_manifest_discs()
    print("=== Highwind single-disc ===")
    build_highwind_single_disc()
    update_modding_manifest_highwind_sd()
    print("DONE")


if __name__ == "__main__":
    main()
