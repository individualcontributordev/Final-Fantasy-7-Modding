#!/usr/bin/env python3
"""single-disc-on-csr-v0.1.24: full SD on CSR+movies with unique path-FMV LBAs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mods/single-disc/scripts"))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from disc_sources import csr_root, pristine_bin  # noqa: E402
from inject_movies_by_disc_id import (  # noqa: E402
    inject_one,
    _append_raw_grow,
    _patch_dirent_lba_size,
    _patch_movie_id_bin,
    _raw_sectors,
)
from psx_mode2_iso import (  # noqa: E402
    SECTOR,
    USER,
    extract_file,
    find_file,
    replace_file_padded,
    _list_dir,
    _u32_le,
    _user,
    _write_user,
)

MOVIES = "single-disc-csr-manip-movies-v0.1.4"
PREV = "single-disc-on-csr-v0.1.23"


def _walk_files(img, dir_lba, dir_size, prefix=""):
    out = []
    for n, lba, sz, d in _list_dir(img, dir_lba, dir_size):
        if n in (".", ".."):
            continue
        path = f"{prefix}{n}"
        if d:
            out.extend(_walk_files(img, lba, sz, path + "/"))
        else:
            out.append(path)
    return out


def all_iso_files(img):
    pvd = _user(img, 16)
    root = pvd[156:190]
    return _walk_files(img, _u32_le(root, 2), _u32_le(root, 10))


def install_file_grow(img: bytearray, path: str, data: bytes) -> None:
    """Install file; grow via EOF raw sectors if larger than slot (Form1 user)."""
    meta = find_file(img, path)
    if len(data) <= meta.size:
        replace_file_padded(img, path, data)
        return
    # Build Mode2 Form1 sectors for the payload
    nsec = (len(data) + USER - 1) // USER
    if len(img) % SECTOR:
        img.extend(b"\x00" * (SECTOR - (len(img) % SECTOR)))
    new_lba = len(img) // SECTOR
    # Clone template sector header from original file sector 0
    tmpl = bytes(img[meta.lba * SECTOR : (meta.lba + 1) * SECTOR])
    for i in range(nsec):
        sec = bytearray(tmpl)
        # bump sector address BCD? keep simple - many tools leave MSF stale (emulators OK)
        off = i * USER
        chunk = data[off : off + USER]
        if len(chunk) < USER:
            chunk = chunk + b"\x00" * (USER - len(chunk))
        sec[24 : 24 + USER] = chunk
        img.extend(sec)
    _patch_dirent_lba_size(img, path, new_lba, len(data))


def main() -> int:
    csr = csr_root()
    movies_layer = ROOT / f"builder/{MOVIES}/layers/disc1.layer.json"
    prev_layer = ROOT / f"builder/{PREV}/layers/disc1.layer.json"
    base_path = ROOT / "workspace/iso-extract/_csr_plus_movies_baseline_sd024.bin"
    work = ROOT / "workspace/iso-extract/sd_v024_path_after_movies.bin"

    print("CSR...")
    csr_img = bytearray(pristine_bin(1).read_bytes())
    apply_layer(
        csr_img,
        json.loads((csr / "builder/csr-v0.14.1/layers/disc1.layer.json").read_text()),
    )
    csr_b = bytes(csr_img)

    print("CSR+SD0.1.23 donor...")
    sd_img = bytearray(csr_b)
    apply_layer(sd_img, json.loads(prev_layer.read_text()))
    sd_b = bytes(sd_img)

    print("CSR+movies baseline...")
    base = bytearray(csr_b)
    apply_layer(base, json.loads(movies_layer.read_text()))
    base_path.write_bytes(base)
    print("baseline", len(base))

    print("Install all non-movie SD deltas (grow if needed)...")
    n_copy = n_grow = 0
    for path in all_iso_files(sd_b):
        up = path.upper()
        if up.startswith("MOVIE/") or up == "MINT/MOVIE_ID.BIN":
            continue
        try:
            a = extract_file(csr_b, path)
            b = extract_file(sd_b, path)
        except Exception:
            continue
        if a == b:
            continue
        before = find_file(base, path).size
        install_file_grow(base, path, b)
        after = find_file(base, path).size
        if after > before:
            n_grow += 1
        n_copy += 1
    print("installed", n_copy, "grew", n_grow)

    csr_d2p = Path.home() / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D2.bin"
    if not csr_d2p.is_file():
        csr_d2p = csr / "cache/csr/FINALFANTASY7_D2.bin"
    cd2 = csr_d2p.read_bytes()
    for stem in ("FSHIP_12", "MD8_52"):
        install_file_grow(base, f"FIELD/{stem}.DAT", extract_file(cd2, f"FIELD/{stem}.DAT"))
        print("CSR", stem)

    d2 = pristine_bin(2).read_bytes()
    injects = [
        ("PARASHOT.MOV", "OPENINGE.MOV"),
        ("METEOFIX.MOV", "MTCRL.STR"),
        ("METEOSKY.MOV", "MTNVL.STR"),
        ("NRCRL.MOV", "MTNVL2.STR"),
        ("NRCRLB.MOV", "NIVLSFS.MOV"),
    ]
    for src, dst in injects:
        print("force_append", src, "->", dst)
        print(inject_one(base, d2, src, 2, target_d1=dst, force_append=True))

    for src, dst in injects:
        s = extract_file(d2, "MOVIE/" + src)
        g = extract_file(bytes(base), "MOVIE/" + dst)
        if g != s and not g.startswith(s):
            raise SystemExit(f"payload fail {src}")
    j = extract_file(bytes(base), "MOVIE/JAIROFAL.MOV")
    c = extract_file(d2, "MOVIE/CANONON.MOV")
    if j != c and not j.startswith(c):
        raise SystemExit("JAIROFAL clobbered")
    # unique LBAs for path slots
    from collections import defaultdict
    lbs = defaultdict(list)
    for _, dst in injects:
        m = find_file(base, "MOVIE/" + dst)
        lbs[m.lba].append(dst)
    jm = find_file(base, "MOVIE/JAIROFAL.MOV")
    lbs[jm.lba].append("JAIROFAL.MOV")
    for lb, names in lbs.items():
        if len(names) > 1:
            raise SystemExit(f"shared LBA {lb}: {names}")
    print("payloads + unique LBAs OK")

    work.write_bytes(base)
    print("wrote", work, len(base))

    pack_id = "single-disc-on-csr-v0.1.24"
    pack_dir = ROOT / "builder" / pack_id
    layer_dir = pack_dir / "layers"
    layer_dir.mkdir(parents=True, exist_ok=True)
    print("diff...")
    layer = build_layer(
        base_path,
        work,
        layer_id=pack_id + "-disc1",
        description=(
            "Single-disc on CSR v0.1.24 — full SD fields on CSR+movies + "
            "force-append PARASHOT/NRCRL/NRCRLB (unique LBAs)"
        ),
    )
    (layer_dir / "disc1.layer.json").write_text(
        json.dumps(layer, separators=(",", ":")) + "\n"
    )
    print("records", len(layer["records"]), layer.get("stats"))

    old = json.loads((ROOT / f"builder/{PREV}/pack.json").read_text())
    pack = {
        **{k: v for k, v in old.items() if k not in ("id", "version", "blurb", "betaNote")},
        "id": pack_id,
        "version": "0.1.24",
        "name": "Single-disc",
        "blurb": (
            "Play the whole game from one Disc 1 image on CSR. "
            "v0.1.24: PARASHOT/NRCRL after manip-movies with unique LBAs. "
            "Hojo/break kept."
        ),
        "hint": "Use one Disc 1 image for the full CSR game.",
        "beta": True,
        "status": "beta",
        "betaNote": (
            "Single-disc is still playtesting; known freezes and glitches on some paths."
        ),
        "discs": {"1": "./layers/disc1.layer.json"},
    }
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2) + "\n")

    man_path = ROOT / "builder/manifest.json"
    man = json.loads(man_path.read_text())
    entry = {
        "id": pack_id,
        "name": "Single-disc",
        "kind": "mod",
        "version": "0.1.24",
        "blurb": pack["blurb"],
        "hint": pack["hint"],
        "format": "ic-layer-v1",
        "compatibleBases": ["csr-v0.14.1"],
        "layout": "global",
        "discs": {"1": "./" + pack_id + "/layers/disc1.layer.json"},
        "enabled": True,
        "beta": True,
        "status": "beta",
        "betaNote": pack["betaNote"],
    }
    for a in man["addons"]:
        aid = a.get("id", "")
        if aid.startswith("single-disc-on-csr-v0.1.") and aid != pack_id:
            a["enabled"] = False
        aw = a.get("autoIncludeWhen") or {}
        if isinstance(aw.get("addonSelected"), str) and aw["addonSelected"].startswith(
            "single-disc-on-csr-v0.1."
        ):
            aw["addonSelected"] = pack_id
            a["autoIncludeWhen"] = aw
    if any(a.get("id") == pack_id for a in man["addons"]):
        man["addons"] = [entry if a.get("id") == pack_id else a for a in man["addons"]]
    else:
        man["addons"].append(entry)
    man_path.write_text(json.dumps(man, indent=2) + "\n")
    print("manifest ok", pack_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
