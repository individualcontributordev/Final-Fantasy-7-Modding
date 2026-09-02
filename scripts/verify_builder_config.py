#!/usr/bin/env python3
"""Reconstruct and validate a local browser-builder mod selection.

  python3 scripts/verify_builder_config.py \\
    --disc 1 \\
    --base csr-plus \\
    --addon fanfare-skip-on-csr-plus

Same flags as the CSR command. Non-clean bases come from ``--csr-root`` or
``FF7_CSR_ROOT``. Add-on layers come from this repository's ``builder/``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from libs.layer import apply_layer
from libs.local_paths import csr_root, default_pristine_arg, ensure_parent_image


def _load_manifest(path: Path) -> tuple[Path, dict]:
    """Load a manifest and return its directory for relative layer resolution."""
    path = path.expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"Missing manifest: {path}")
    return path.parent, json.loads(path.read_text(encoding="utf-8"))


def _index_mods(builder_dir: Path, data: dict) -> dict[str, dict]:
    """id -> {entry, builder_dir}"""
    out: dict[str, dict] = {}
    for key in ("bases", "addons"):
        for entry in data.get(key) or []:
            pid = entry.get("id")
            if not pid:
                continue
            out[str(pid)] = {"entry": entry, "builder_dir": builder_dir, "kind": key[:-1]}
    return out


def _layer_path(meta: dict, disc: int) -> Path:
    """Resolve the selected disc layer relative to its indexed mod root."""
    entry = meta["entry"]
    discs = entry.get("discs") or {}
    rel = discs.get(str(disc)) or discs.get(disc)
    if not rel:
        raise SystemExit(f"{entry.get('id')}: no layer for disc {disc}")
    path = (meta["builder_dir"] / str(rel).lstrip("./")).resolve()
    if not path.is_file():
        raise SystemExit(f"Missing layer: {path}")
    return path


def _check_records(image: bytes | bytearray, layer_path: Path) -> int:
    """Fail unless every layer record already matches image (no write)."""
    layer = json.loads(layer_path.read_text(encoding="utf-8"))
    if layer.get("format") != "ic-layer-v1":
        raise SystemExit(f"{layer_path}: expected ic-layer-v1")
    records = layer.get("records") or []
    for rec in records:
        off = int(rec["offset"])
        data = bytes.fromhex(rec["hex"])
        if bytes(image[off : off + len(data)]) != data:
            raise SystemExit(f"layer mismatch in {layer_path.name} @ {off:#x}")
    return len(records)


def _apply_and_check(image: bytearray, layer_path: Path) -> int:
    """Apply one layer and require every record to contain its requested bytes."""
    layer = json.loads(layer_path.read_text(encoding="utf-8"))
    if layer.get("format") != "ic-layer-v1":
        raise SystemExit(f"{layer_path}: expected ic-layer-v1")
    apply_layer(image, layer)
    return _check_records(image, layer_path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify builder base+addon stack on a pristine disc")
    ap.add_argument(
        "--pristine",
        type=Path,
        default=None,
        help="Retail NTSC-U disc .bin (default: workspace/pristine/FINALFANTASY7_DN.bin)",
    )
    ap.add_argument("--disc", type=int, required=True, choices=(1, 2, 3))
    ap.add_argument(
        "--base",
        required=True,
        help="Base id: clean | csr | csr-plus | highwind",
    )
    ap.add_argument(
        "--addon",
        action="append",
        default=[],
        dest="addons",
        help="Mod id (repeatable), in apply order",
    )
    ap.add_argument(
        "--csr-root",
        type=Path,
        help="Final-Fantasy-7-CSR checkout (or set FF7_CSR_ROOT)",
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "builder" / "manifest.json",
        help="Primary builder/manifest.json (default: this repo)",
    )
    ap.add_argument(
        "--extra-manifest",
        action="append",
        default=[],
        type=Path,
        help="Additional manifest(s) e.g. CSR builder/manifest.json",
    )
    ap.add_argument("-o", "--output", type=Path, default=None)
    ap.add_argument(
        "--no-cache",
        action="store_true",
        help="Do not write cache/<base>/ when reconstructing a CSR base",
    )
    args = ap.parse_args()

    pristine = (
        args.pristine.expanduser().resolve()
        if args.pristine
        else default_pristine_arg(args.disc).resolve()
    )
    if not pristine.is_file():
        raise SystemExit(f"Missing pristine image: {pristine}")

    catalog: dict[str, dict] = {}
    manifests = [args.manifest, *args.extra_manifest]
    csr = csr_root(args.csr_root)
    if csr is not None:
        manifests.append(csr / "builder" / "manifest.json")
    for man in manifests:
        bdir, data = _load_manifest(man)
        catalog.update(_index_mods(bdir, data))

    base_id = args.base.strip()
    print(f"Config: base={base_id} addons={args.addons or []} disc={args.disc}")
    print(f"Pristine: {pristine}")

    total_recs = 0
    stack: list[str] = []

    if base_id in ("clean", "unmodified"):
        image = bytearray(pristine.read_bytes())
        stack.append("base:clean (pristine only)")
        print("  OK base clean (no base layer)")
    else:
        if csr is None and base_id not in catalog:
            raise SystemExit("Pass --csr-root or set FF7_CSR_ROOT")
        parent_bytes, parent_path = ensure_parent_image(
            base_id=base_id,
            disc=args.disc,
            pristine=pristine,
            csr=csr,
            use_cache=not args.no_cache,
        )
        image = bytearray(parent_bytes)
        if base_id in catalog:
            lp = _layer_path(catalog[base_id], args.disc)
            n = _check_records(image, lp)
            total_recs += n
            stack.append(f"base:{base_id} ({n} records)")
            print(f"  OK base {base_id} ← {lp.name} ({n} records, src={parent_path})")
        else:
            stack.append(f"base:{base_id} (from {parent_path})")
            print(f"  OK base {base_id} ← {parent_path}")

    for addon_id in args.addons:
        if addon_id not in catalog:
            raise SystemExit(f"Unknown addon id {addon_id!r}")
        meta = catalog[addon_id]
        entry = meta["entry"]
        compat = entry.get("compatibleBases") or []
        need = "clean" if base_id in ("clean", "unmodified") else base_id
        if compat and need not in compat:
            raise SystemExit(
                f"{addon_id}: compatibleBases={compat} does not include base {need!r}"
            )
        lp = _layer_path(meta, args.disc)
        n = _apply_and_check(image, lp)
        total_recs += n
        stack.append(f"addon:{addon_id} ({lp.name}, {n} records)")
        print(f"  OK addon {addon_id} ← {lp.relative_to(meta['builder_dir'])} ({n} records)")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(image)
        print(f"Wrote {args.output} ({len(image)} bytes)")

    print("Stack:")
    for line in stack:
        print(f"  - {line}")
    print(f"PASS — builder config applies cleanly ({total_recs} total records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
