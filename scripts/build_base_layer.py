#!/usr/bin/env python3
"""Build and locally publish one mod disc layer from an edited BIN.

  python3 scripts/build_base_layer.py \\
    cache/fanfare-skip-on-csr-plus/FINALFANTASY7_D1.bin --version 0.1.7

Same interface as the CSR command of the same name. The edited BIN's parent
folder is the mod id (``cache/<mod-id>/``). The layer is a diff against that
mod's compatible base, not against pristine. Parent BIN order: ``--parent``,
then this repo's ``cache/<base>/``, then pristine plus the CSR base layer
written into that cache. CSR's own cache directory is never read.

Writes builder/<mod>/layers/discN.layer.json, merges pack.json + VERSION +
manifest.json, and verifies parent + layer = edited image.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from libs.layer import apply_layer, build_layer
from libs.local_paths import csr_root, ensure_parent_image, pristine_bin

DISC_BIN_NAME = re.compile(
    r"^FINALFANTASY7_D([123])(?: \(patched\))?\.bin$",
    re.IGNORECASE,
)


def disc_from_bin_path(patched: Path) -> int:
    """Read disc number from a FINALFANTASY7_DN.bin filename."""
    match = DISC_BIN_NAME.match(patched.name)
    if not match:
        raise SystemExit(
            f"Cannot infer disc from {patched.name} — "
            "expected FINALFANTASY7_D1.bin (or D2/D3, optional ' (patched)')."
        )
    return int(match.group(1))


def load_mod(builder_dir: Path, mod_id: str) -> dict:
    """Load an existing mod; new mods are not invented here."""
    meta_path = builder_dir / mod_id / "pack.json"
    if not meta_path.is_file():
        raise SystemExit(
            f"Unknown mod folder '{mod_id}'. Expected the image under "
            f"cache/<mod-id>/ matching an existing builder/{mod_id}/pack.json."
        )
    mod = json.loads(meta_path.read_text(encoding="utf-8"))
    if str(mod.get("id", "")) != mod_id:
        raise SystemExit(f"{meta_path}: id {mod.get('id')!r} does not match folder {mod_id!r}")
    return mod


def compatible_base(mod: dict) -> str:
    """Each published mod targets one exclusive base."""
    bases = mod.get("compatibleBases") or []
    if len(bases) != 1:
        raise SystemExit(
            f"{mod.get('id')}: expected exactly one compatibleBases entry, got {bases!r}"
        )
    return str(bases[0])


def sorted_disc_map(discs: dict) -> dict[str, str]:
    """Keep disc keys in 1, 2, 3 order for stable JSON."""
    return {k: discs[k] for k in sorted(discs, key=lambda d: int(d))}


def upsert_mod_json(mod_dir: Path, mod: dict, version: str, disc: int) -> dict:
    """Write one disc into pack.json without dropping extra mod fields."""
    discs = dict(mod.get("discs") or {})
    discs[str(disc)] = f"./layers/disc{disc}.layer.json"
    mod["version"] = version
    mod["kind"] = mod.get("kind") or "mod"
    mod["format"] = mod.get("format") or "ic-layer-v1"
    mod["discs"] = sorted_disc_map(discs)
    mod_dir.mkdir(parents=True, exist_ok=True)
    (mod_dir / "pack.json").write_text(json.dumps(mod, indent=2) + "\n", encoding="utf-8")
    (mod_dir / "VERSION").write_text(version + "\n", encoding="utf-8")
    return mod


def update_manifest(mod: dict, disc: int, builder_dir: Path) -> None:
    """Merge one disc into the matching enabled mod, preserving other entries."""
    manifest_path = builder_dir / "manifest.json"
    if manifest_path.is_file():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        data = {
            "version": 1,
            "source": "Final-Fantasy-7-Modding",
            "addons": [],
        }
    mod_id = mod["id"]
    disc_rel = f"./{mod_id}/layers/disc{disc}.layer.json"

    addons = data.setdefault("addons", [])
    existing_index = None
    existing: dict = {}
    for i, candidate in enumerate(addons):
        if str(candidate.get("id", "")) == mod_id:
            existing_index = i
            existing = dict(candidate)
            break

    entry = dict(existing)
    entry.update(mod)
    discs = dict(existing.get("discs") or {})
    discs[str(disc)] = disc_rel
    entry["discs"] = sorted_disc_map(discs)
    entry["enabled"] = True
    if existing_index is None:
        addons.append(entry)
    else:
        addons[existing_index] = entry

    manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def verify(parent: Path, layer: dict, patched: Path) -> None:
    """Require an exact parent + layer = patched round trip."""
    image = bytearray(parent.read_bytes())
    apply_layer(image, layer)
    expect = patched.read_bytes()
    if bytes(image) != expect:
        lim = min(len(image), len(expect))
        for i in range(lim):
            if image[i] != expect[i]:
                raise SystemExit(f"VERIFY FAIL at offset {i} (0x{i:X})")
        raise SystemExit(f"VERIFY FAIL size {len(image)} vs {len(expect)}")


def build_one_disc(
    *,
    mod: dict,
    version: str,
    disc: int,
    patched: Path,
    parent: Path,
    builder_dir: Path,
    skip_verify: bool,
) -> Path:
    """Diff, write, and optionally round-trip one disc layer."""
    if not parent.is_file():
        raise SystemExit(f"Missing parent: {parent}")
    if not patched.is_file():
        raise SystemExit(f"Missing patched: {patched}")

    mod_id = mod["id"]
    out_dir = builder_dir / mod_id / "layers"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"disc{disc}.layer.json"

    layer_id = f"{mod_id}-disc{disc}"
    description = f"{mod.get('name') or mod_id} v{version} — NTSC-U Disc {disc}"
    print(f"=== Disc {disc}: diff ===")
    print(f"  parent:  {parent}")
    print(f"  patched: {patched}")
    layer = build_layer(
        parent,
        patched,
        layer_id=layer_id,
        description=description,
    )
    stats = layer["stats"]
    if stats["records"] == 0:
        raise SystemExit("Empty layer — edited image matches the parent base")

    if not skip_verify:
        print(f"=== Disc {disc}: verify ===")
        verify(parent, layer, patched)
        print("  OK — layer apply matches patched image")

    out_path.write_text(json.dumps(layer, indent=2) + "\n", encoding="utf-8")
    print(
        f"  wrote {out_path}  "
        f"records={stats['records']} changedBytes={stats['changedBytes']}"
    )
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build one mod disc layer for the browser builder."
    )
    ap.add_argument(
        "image",
        type=Path,
        help="Edited BIN, e.g. cache/fanfare-skip-on-csr-plus/FINALFANTASY7_D1.bin",
    )
    ap.add_argument("--version", required=True, help="Version string, e.g. 0.1.7")
    ap.add_argument(
        "--parent",
        type=Path,
        help="Parent base BIN to diff against (default: cache/<compatibleBase>/)",
    )
    ap.add_argument(
        "--csr-root",
        type=Path,
        help="Final-Fantasy-7-CSR checkout (or set FF7_CSR_ROOT)",
    )
    ap.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip apply_layer round-trip checks (not recommended)",
    )
    ap.add_argument(
        "--builder-dir",
        type=Path,
        default=ROOT / "builder",
        help=argparse.SUPPRESS,
    )
    args = ap.parse_args()

    version = args.version.strip()
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)*", version):
        raise SystemExit(f"Weird version '{version}' — expected like 0.1.7")

    patched = args.image.expanduser().resolve()
    disc = disc_from_bin_path(patched)
    mod_id = patched.parent.name
    builder_dir = args.builder_dir.expanduser().resolve()
    mod = load_mod(builder_dir, mod_id)
    mod_dir = builder_dir / mod_id
    base_id = compatible_base(mod)

    if args.parent:
        parent = args.parent.expanduser().resolve()
        if not parent.is_file():
            raise SystemExit(f"Missing parent: {parent}")
    else:
        _data, parent = ensure_parent_image(
            base_id=base_id,
            disc=disc,
            pristine=pristine_bin(disc),
            csr=csr_root(args.csr_root),
        )

    print(f"Mod:     {mod.get('name') or mod_id} ({mod_id})")
    print(f"Against: {base_id}")
    print(f"Version: {version}")
    print(f"Image:   {patched}")
    print(f"Disc:    {disc}")
    print(f"Parent:  {parent}")
    print(f"Output:  {mod_dir}")

    build_one_disc(
        mod=mod,
        version=version,
        disc=disc,
        patched=patched,
        parent=parent,
        builder_dir=builder_dir,
        skip_verify=args.skip_verify,
    )

    mod = upsert_mod_json(mod_dir, mod, version, disc)
    update_manifest(mod, disc, builder_dir)
    print(f"Updated {mod_dir / 'pack.json'}")
    print(f"Updated {builder_dir / 'manifest.json'} (enabled=true)")
    print("Commit JSON under builder/ only — not .bin/.cue.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
