#!/usr/bin/env python3
"""Build Encounter ic-layer-v1 packs for Disc 1–3.

Retail / Unmodified (default --against clean):

  python scripts/prepare_encounter_workspace.py --discs 1
  # … stub + CDmage import …
  python scripts/build_encounter_layers.py --version 0.1.0 --discs 1

CSR stack (layer must be diffed against that CSR base, not retail):

  python scripts/prepare_encounter_workspace.py --discs 1 --force \\
    --from-dir /c/path/to/Final-Fantasy-7-CSR/workspace/csr-plus
  # … stub + CDmage import on the iso-extract working copy …
  python scripts/build_encounter_layers.py --version 0.1.0 --discs 1 \\
    --against csr-plus \\
    --base-dir /c/path/to/Final-Fantasy-7-CSR/workspace/csr-plus

See builder/WINDOWS-INSTRUCTIONS.md.
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

# --against key → builder base id + pack naming
AGAINST = {
    "clean": {
        "base_id": "clean",
        "pack_prefix": "encounter",
        "display": "Encounter rate",
        "blurb": (
            "RCnt2 FORCE at lure/2 (~3.1%/check default; 50% of raw lure/256). "
            "Enemy Lure / Away still scale. Use with Unmodified only."
        ),
    },
    "csr": {
        "base_id": "csr-v0.14.0",
        "pack_prefix": "encounter-on-csr",
        "display": "Encounter rate (on CSR)",
        "blurb": (
            "RCnt2 FORCE at lure/2 on CSR FIELD.BIN (~3.1%/check default). "
            "Use with CSR base only."
        ),
    },
    "csr-plus": {
        "base_id": "csr-plus-v0.1.0",
        "pack_prefix": "encounter-on-csr-plus",
        "display": "Encounter rate (on CSR+)",
        "blurb": (
            "RCnt2 FORCE at lure/2 on CSR+ FIELD.BIN (~3.1%/check default). "
            "Use with CSR+ base only."
        ),
    },
    "csr-plusplus": {
        "base_id": "csr-plusplus-v0.1.0",
        "pack_prefix": "encounter-on-csr-plusplus",
        "display": "Encounter rate (on CSR++)",
        "blurb": (
            "RCnt2 FORCE at lure/2 on CSR++ FIELD.BIN (~3.1%/check default). "
            "Use with CSR++ base only."
        ),
    },
}


def parse_discs(spec: str | None, base_bin_fn, working_bin_fn) -> list[int]:
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
    found = [
        d
        for d in (1, 2, 3)
        if base_bin_fn(d).is_file() and working_bin_fn(d).is_file()
    ]
    if not found:
        raise SystemExit(
            "No disc pairs found (base + iso-extract working image).\n"
            "Run prepare_encounter_workspace.py, stub, import, then re-run."
        )
    return found


def verify(base: Path, layer_path: Path, patched: Path) -> None:
    image = bytearray(base.read_bytes())
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


def write_pack_json(
    pack_dir: Path,
    *,
    pack_id: str,
    version: str,
    display: str,
    blurb: str,
    compatible_bases: list[str],
    discs: list[int],
) -> None:
    pack = {
        "id": pack_id,
        "name": display,
        "kind": "addon",
        "version": version,
        "blurb": blurb,
        "format": "ic-layer-v1",
        "compatibleBases": compatible_bases,
        "discs": {str(d): f"./layers/disc{d}.layer.json" for d in discs},
    }
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")


def update_manifest(
    *,
    pack_id: str,
    pack_prefix: str,
    version: str,
    display: str,
    blurb: str,
    compatible_bases: list[str],
    discs: list[int],
) -> None:
    if not MANIFEST_PATH.is_file():
        raise SystemExit(f"Missing {MANIFEST_PATH}")
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entry = {
        "id": pack_id,
        "name": f"{display} v{version}",
        "kind": "addon",
        "blurb": blurb,
        "format": "ic-layer-v1",
        "compatibleBases": compatible_bases,
        "discs": {
            str(d): f"./{pack_id}/layers/disc{d}.layer.json" for d in discs
        },
        "enabled": True,
    }

    addons = data.setdefault("addons", [])
    replaced = False
    version_prefix = f"{pack_prefix}-v"
    for i, existing in enumerate(addons):
        ex_id = str(existing.get("id", ""))
        if ex_id == pack_id:
            addons[i] = entry
            replaced = True
        elif ex_id.startswith(version_prefix):
            # Older encounter packs for the same base family
            existing["enabled"] = False
            existing["note"] = (
                f"Superseded by {pack_id}. Disabled automatically on rebuild."
            )
    if not replaced:
        addons.append(entry)

    MANIFEST_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def resolve_base_bin(disc: int, against: str, base_dir: Path | None) -> Path:
    if against == "clean":
        return PRISTINE_DIR / f"FINALFANTASY7_D{disc}.bin"

    if base_dir is None:
        raise SystemExit(
            f"--against {against} requires --base-dir "
            "(CSR repo folder with FINALFANTASY7_DN (patched).bin)."
        )
    base_dir = base_dir.expanduser().resolve()
    patched = base_dir / f"FINALFANTASY7_D{disc} (patched).bin"
    retail_name = base_dir / f"FINALFANTASY7_D{disc}.bin"
    if patched.is_file():
        return patched
    if retail_name.is_file():
        return retail_name
    raise SystemExit(f"Missing base image for disc {disc} under {base_dir}")


def working_bin(disc: int) -> Path:
    return ISO / f"FINALFANTASY7_D{disc}.bin"


def build_one_disc(
    *,
    version: str,
    disc: int,
    against: str,
    meta: dict,
    base_dir: Path | None,
    skip_verify: bool,
) -> Path:
    base = resolve_base_bin(disc, against, base_dir)
    patched = working_bin(disc)
    if not base.is_file():
        raise SystemExit(f"Missing stack-base image: {base}")
    if not patched.is_file():
        raise SystemExit(
            f"Missing working image: {patched}\n"
            "prepare → stub → import FIELD.BIN.new into iso-extract."
        )
    if base.resolve() == patched.resolve():
        raise SystemExit("Base and working paths are the same file — check layout.")

    pack_id = f"{meta['pack_prefix']}-v{version}"
    out_dir = _ROOT / "builder" / pack_id / "layers"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"disc{disc}.layer.json"

    layer_id = f"{meta['pack_prefix']}-disc{disc}-v{version}"
    description = (
        f"Encounter RCnt2 FORCE stub — NTSC-U Disc {disc} "
        f"(against {meta['base_id']})"
    )
    print(f"\n=== Disc {disc}: diff ===")
    print(f"  base:    {base}")
    print(f"  working: {patched}")
    layer = build_layer(
        base,
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
            f"Disc {disc}: base and working images are identical.\n"
            "Stub never landed, or you re-prepared over the working copy."
        )

    if not skip_verify:
        print(f"=== Disc {disc}: verify ===")
        verify(base, out_path, patched)
        print("  OK — layer apply matches working image")

    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build Encounter layers for the browser builder."
    )
    ap.add_argument("--version", required=True, help="Version string, e.g. 0.1.0")
    ap.add_argument(
        "--discs",
        default=None,
        help="Comma list (default: all pairs that exist). Example: 1,2,3",
    )
    ap.add_argument(
        "--against",
        default="clean",
        choices=sorted(AGAINST.keys()),
        help="Which builder base this Encounter layer stacks on (default: clean)",
    )
    ap.add_argument(
        "--base-dir",
        default=None,
        help="CSR workspace folder with FINALFANTASY7_DN (patched).bin (required unless --against clean)",
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

    against = args.against
    meta = AGAINST[against]
    base_dir = Path(args.base_dir) if args.base_dir else None
    if against != "clean" and base_dir is None:
        raise SystemExit(f"--against {against} requires --base-dir")

    discs = parse_discs(
        args.discs,
        lambda d: resolve_base_bin(d, against, base_dir),
        working_bin,
    )
    pack_id = f"{meta['pack_prefix']}-v{version}"
    pack_dir = _ROOT / "builder" / pack_id
    compatible = [meta["base_id"]]

    print(f"Addon:     {meta['display']}")
    print(f"Version:   {version}")
    print(f"Against:   {against} → compatibleBases={compatible}")
    print(f"Working:   {ISO}")
    print(f"Discs:     {discs}")
    print(f"Output:    builder/{pack_id}/")

    for disc in discs:
        build_one_disc(
            version=version,
            disc=disc,
            against=against,
            meta=meta,
            base_dir=base_dir,
            skip_verify=args.skip_verify,
        )

    write_pack_json(
        pack_dir,
        pack_id=pack_id,
        version=version,
        display=meta["display"],
        blurb=meta["blurb"],
        compatible_bases=compatible,
        discs=discs,
    )
    update_manifest(
        pack_id=pack_id,
        pack_prefix=meta["pack_prefix"],
        version=version,
        display=meta["display"],
        blurb=meta["blurb"],
        compatible_bases=compatible,
        discs=discs,
    )
    print(f"\nUpdated {pack_dir / 'pack.json'}")
    print(f"Updated {MANIFEST_PATH.relative_to(_ROOT)} (enabled=true, discs={discs})")
    print("\nDone. Commit JSON under builder/ only — not .bin/.cue.")
    print("Existing retail encounter-v* addon is left as-is when building a CSR-on pack.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
