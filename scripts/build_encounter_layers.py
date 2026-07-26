#!/usr/bin/env python3
"""Build Encounter ic-layer-v1 packs for Disc 1–3.

Git Bash (after prepare + CDmage — see builder/WINDOWS-INSTRUCTIONS.md):

  python scripts/prepare_encounter_workspace.py --discs 1
  # … extract FIELD.BIN, stub, import into the open working image …
  python scripts/build_encounter_layers.py --version 0.1.0 --discs 1

Diffs:
  workspace/pristine/FINALFANTASY7_DN.bin
    vs workspace/iso-extract/FINALFANTASY7_DN.bin   (working copy after import)

Writes builder/encounter-v<version>/layers/discN.layer.json, updates pack.json +
manifest.json (enabled, discs map for all discs built).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
_ROOT = _SCRIPTS.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402

PRISTINE_DIR = _ROOT / "workspace" / "pristine"
ISO = _ROOT / "workspace" / "iso-extract"
MANIFEST_PATH = _ROOT / "builder" / "manifest.json"
BLURB = (
    "RCnt2 FORCE stub — Enemy Lure / Away still scale. NTSC-U field encounters. "
    "Unmodified base only (CSR stacks need a CSR-built Encounter layer)."
)
COMPATIBLE_BASES = ["clean"]


def disc_paths(disc: int) -> tuple[Path, Path]:
    stem = f"FINALFANTASY7_D{disc}"
    # Same filename in both folders: vault stays clean; iso-extract is the
    # CDmage working image (import auto-saves into whatever file is open).
    pristine = PRISTINE_DIR / f"{stem}.bin"
    patched = ISO / f"{stem}.bin"
    return pristine, patched


def available_discs() -> list[int]:
    return [d for d in (1, 2, 3) if all(p.is_file() for p in disc_paths(d))]


def parse_discs(spec: str | None) -> list[int]:
    if spec:
        discs = []
        for part in spec.split(","):
            part = part.strip()
            if not part:
                continue
            disc = int(part)
            if disc not in (1, 2, 3):
                raise SystemExit(f"Disc must be 1, 2, or 3 — got {disc}")
            discs.append(disc)
        return discs
    found = available_discs()
    if not found:
        raise SystemExit(
            "No disc pairs found.\n"
            f"  Pristine: {PRISTINE_DIR}/FINALFANTASY7_DN.bin\n"
            f"  Working:  {ISO}/FINALFANTASY7_DN.bin\n"
            "Run prepare_encounter_workspace.py, then import FIELD.BIN.new in CDmage."
        )
    return found


def verify(pristine: Path, layer_path: Path, patched: Path) -> None:
    image = bytearray(pristine.read_bytes())
    layer = json.loads(layer_path.read_text(encoding="utf-8"))
    apply_layer(image, layer)
    expect = patched.read_bytes()
    if bytes(image) != expect:
        lim = min(len(image), len(expect))
        for i in range(lim):
            if image[i] != expect[i]:
                raise SystemExit(f"VERIFY FAIL at offset {i} (0x{i:X}) for {layer_path.name}")
        raise SystemExit(
            f"VERIFY FAIL size {len(image)} vs {len(expect)} for {layer_path.name}"
        )


def write_pack_json(pack_dir: Path, version: str, discs: list[int]) -> None:
    pack = {
        "id": f"encounter-v{version}",
        "name": "Encounter rate",
        "kind": "addon",
        "version": version,
        "blurb": BLURB,
        "format": "ic-layer-v1",
        "compatibleBases": COMPATIBLE_BASES,
        "discs": {str(d): f"./layers/disc{d}.layer.json" for d in discs},
    }
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")


def update_manifest(version: str, discs: list[int]) -> None:
    if not MANIFEST_PATH.is_file():
        raise SystemExit(f"Missing {MANIFEST_PATH}")
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    pack_id = f"encounter-v{version}"
    entry = {
        "id": pack_id,
        "name": f"Encounter rate v{version}",
        "kind": "addon",
        "blurb": BLURB,
        "format": "ic-layer-v1",
        "compatibleBases": COMPATIBLE_BASES,
        "discs": {
            str(d): f"./{pack_id}/layers/disc{d}.layer.json" for d in discs
        },
        "enabled": True,
    }

    addons = data.setdefault("addons", [])
    replaced = False
    for i, existing in enumerate(addons):
        ex_id = str(existing.get("id", ""))
        if ex_id == pack_id or ex_id.startswith("encounter-v"):
            addons[i] = entry
            replaced = True
            break
    if not replaced:
        addons.append(entry)

    MANIFEST_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_one_disc(*, version: str, disc: int, skip_verify: bool) -> Path:
    pristine, patched = disc_paths(disc)
    if not pristine.is_file():
        raise SystemExit(
            f"Missing pristine vault image: {pristine}\n"
            "Place clean retail FINALFANTASY7_DN.bin under workspace/pristine/."
        )
    if not patched.is_file():
        raise SystemExit(
            f"Missing working image: {patched}\n"
            "Run prepare_encounter_workspace.py, then import FIELD.BIN.new in CDmage."
        )

    # Same path / same file = operator error; also catch identical content early messaging.
    if pristine.resolve() == patched.resolve():
        raise SystemExit("Pristine and patched paths are the same file — check layout.")

    pack_id = f"encounter-v{version}"
    out_dir = _ROOT / "builder" / pack_id / "layers"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"disc{disc}.layer.json"

    layer_id = f"encounter-disc{disc}-v{version}"
    description = f"Encounter RCnt2 FORCE stub — NTSC-U Disc {disc}"
    print(f"\n=== Disc {disc}: diff ===")
    print(f"  pristine: {pristine}")
    print(f"  patched:  {patched}")
    layer = build_layer(
        pristine,
        patched,
        layer_id=layer_id,
        description=description,
    )
    out_path.write_text(json.dumps(layer, indent=2) + "\n", encoding="utf-8")
    stats = layer["stats"]
    print(
        f"  wrote {out_path.relative_to(_ROOT)}  "
        f"records={stats['records']} changedBytes={stats['changedBytes']}"
    )
    if stats["records"] == 0 or stats["changedBytes"] == 0:
        raise SystemExit(
            f"Disc {disc}: pristine vault and iso-extract working image are identical.\n"
            "  • Stub never landed (import failed / wrong file open), or\n"
            "  • Vault under workspace/pristine/ is already patched "
            "(restore a clean retail dump), or\n"
            "  • You re-ran prepare --force after patching (wiped the working copy).\n"
            "Re-prepare from a clean vault, open the iso-extract image, import FIELD.BIN.new."
        )

    if not skip_verify:
        print(f"=== Disc {disc}: verify ===")
        verify(pristine, out_path, patched)
        print("  OK — layer apply matches patched image")

    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build Encounter layers for Disc 1–3 for the browser builder."
    )
    ap.add_argument("--version", required=True, help="Version string, e.g. 0.1.0")
    ap.add_argument(
        "--discs",
        default=None,
        help="Comma list (default: all pairs that exist). Example: 1,2,3",
    )
    ap.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip apply_layer checks (not recommended)",
    )
    args = ap.parse_args()

    version = args.version.strip()
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)*", version):
        raise SystemExit(f"Weird version '{version}' — expected like 0.1.0")

    discs = parse_discs(args.discs)
    pack_id = f"encounter-v{version}"
    pack_dir = _ROOT / "builder" / pack_id

    print(f"Addon:    Encounter rate")
    print(f"Version:  {version}")
    print(f"Pristine: {PRISTINE_DIR}")
    print(f"Working:  {ISO}")
    print(f"Discs:    {discs}")
    print(f"Output:   builder/{pack_id}/")

    for disc in discs:
        build_one_disc(version=version, disc=disc, skip_verify=args.skip_verify)

    write_pack_json(pack_dir, version, discs)
    update_manifest(version, discs)
    print(f"\nUpdated {pack_dir / 'pack.json'}")
    print(f"Updated {MANIFEST_PATH.relative_to(_ROOT)} (enabled=true, discs={discs})")
    print("\nDone. Commit JSON under builder/ only — not .bin/.cue.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
