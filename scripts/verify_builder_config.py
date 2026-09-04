#!/usr/bin/env python3
"""Reconstruct and validate a local browser-builder mod selection.

One stack:

  python3 scripts/verify_builder_config.py \\
    --disc 1 --base csr-plus --addon fanfare-skip-on-csr-plus

Every published mod on one or more bases (same names as rebuild_on_base.py):

  python3 scripts/verify_builder_config.py all
  python3 scripts/verify_builder_config.py clean
  python3 scripts/verify_builder_config.py csr csr-plus

``all`` is every base, clean included.

Non-clean bases come from ``--csr-root`` or ``FF7_CSR_ROOT``. Add-on layers
come from this repository's ``builder/``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from libs.layer import apply_layer
from libs.local_paths import (
    csr_base_version,
    csr_root,
    default_pristine_arg,
    ensure_parent_image,
    expand_base_names,
)
from libs.timing import Timer


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


def addons_for_base(manifest: dict, base_id: str) -> list[str]:
    """Addon ids the builder would offer on this exclusive base."""
    need = "clean" if base_id in ("clean", "unmodified") else base_id
    ids: list[str] = []
    for entry in manifest.get("addons") or []:
        pid = entry.get("id")
        if not pid:
            continue
        compat = entry.get("compatibleBases") or []
        if need in compat:
            ids.append(str(pid))
    return ids


def discs_for_base(base_id: str, csr_manifest: dict | None) -> list[int]:
    if base_id in ("clean", "unmodified"):
        return [1, 2, 3]
    if csr_manifest is None:
        raise SystemExit(f"{base_id} needs the CSR manifest to know its discs")
    entry = next(
        (b for b in csr_manifest.get("bases") or [] if str(b.get("id")) == base_id),
        None,
    )
    if not entry:
        raise SystemExit(f"Base {base_id!r} not in CSR manifest")
    keys = sorted(int(k) for k in (entry.get("discs") or {}) if str(k).isdigit())
    if not keys:
        raise SystemExit(f"{base_id} lists no discs")
    return keys


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


def _check_records(image: bytes | bytearray, layer_path: Path, label: str) -> int:
    """Fail unless every layer record already matches image (no write)."""
    layer = json.loads(layer_path.read_text(encoding="utf-8"))
    if layer.get("format") != "ic-layer-v1":
        raise SystemExit(f"{layer_path}: expected ic-layer-v1")
    records = layer.get("records") or []
    for rec in records:
        off = int(rec["offset"])
        data = bytes.fromhex(rec["hex"])
        if bytes(image[off : off + len(data)]) != data:
            raise SystemExit(f"layer mismatch: {label} {layer_path.name} @ {off:#x}")
    return len(records)


def _apply_and_check(image: bytearray, layer_path: Path, label: str) -> int:
    """Apply one layer and require every record to contain its requested bytes."""
    layer = json.loads(layer_path.read_text(encoding="utf-8"))
    if layer.get("format") != "ic-layer-v1":
        raise SystemExit(f"{layer_path}: expected ic-layer-v1")
    apply_layer(image, layer)
    return _check_records(image, layer_path, label)


def _load_catalog(
    manifest_paths: list[Path], csr: Path | None
) -> tuple[dict[str, dict], dict]:
    catalog: dict[str, dict] = {}
    primary: dict | None = None
    paths = list(manifest_paths)
    if csr is not None:
        paths.append(csr / "builder" / "manifest.json")
    for man in paths:
        bdir, data = _load_manifest(man)
        if primary is None:
            primary = data
        catalog.update(_index_mods(bdir, data))
    if primary is None:
        raise SystemExit("No manifest loaded")
    return catalog, primary


def _load_base(
    *,
    disc: int,
    base_id: str,
    catalog: dict[str, dict],
    pristine: Path,
    csr: Path | None,
    use_cache: bool,
    timer: Timer,
) -> tuple[bytes, str, int]:
    """The parent BIN for one base, its stack line, and its record count."""
    if base_id in ("clean", "unmodified"):
        print("  OK base clean (no base layer)")
        return pristine.read_bytes(), "base:clean (pristine only)", 0

    if csr is None and base_id not in catalog:
        raise SystemExit("Pass --csr-root or set FF7_CSR_ROOT")
    with timer.stage("load_base"):
        parent_bytes, parent_path = ensure_parent_image(
            base_id=base_id,
            disc=disc,
            pristine=pristine,
            csr=csr,
            use_cache=use_cache,
        )

    if base_id not in catalog:
        print(f"  OK base {base_id} <- {parent_path}")
        return parent_bytes, f"base:{base_id} (from {parent_path})", 0

    lp = _layer_path(catalog[base_id], disc)
    with timer.stage("check_base"):
        n = _check_records(parent_bytes, lp, f"base {base_id}")
    print(f"  OK base {base_id} <- {lp.name} ({n} records, src={parent_path})")
    return parent_bytes, f"base:{base_id} ({n} records)", n


def _check_addon(
    image: bytearray,
    *,
    addon_id: str,
    base_id: str,
    disc: int,
    catalog: dict[str, dict],
    csr_root_arg: Path | None,
) -> tuple[int, str]:
    """Apply one addon onto an already-loaded base; exit if anything misses."""
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
    # The builder hides mods whose baseVersion is not the live base build,
    # so catch that here rather than after publishing.
    want_base_version = csr_base_version(need, csr_root_arg)
    got_base_version = str(entry.get("baseVersion") or "")
    if want_base_version and got_base_version != want_base_version:
        raise SystemExit(
            f"{addon_id}: baseVersion={got_base_version or '(unset)'} but "
            f"{need} is {want_base_version} -- rebuild against the current base "
            "or the builder will hide this mod."
        )
    lp = _layer_path(meta, disc)
    n = _apply_and_check(image, lp, f"addon {addon_id}")
    print(f"  OK addon {addon_id} <- {lp.relative_to(meta['builder_dir'])} ({n} records)")
    return n, f"addon:{addon_id} ({lp.name}, {n} records)"


def verify_stack(
    *,
    disc: int,
    base_id: str,
    addons: list[str],
    catalog: dict[str, dict],
    pristine: Path,
    csr: Path | None,
    use_cache: bool,
    output: Path | None,
    timer: Timer,
    csr_root_arg: Path | None,
) -> None:
    """Apply base then addons on one disc; exit if any record misses."""
    print(f"Config: base={base_id} addons={addons or []} disc={disc}")
    print(f"Pristine: {pristine}")

    parent_bytes, base_line, total_recs = _load_base(
        disc=disc,
        base_id=base_id,
        catalog=catalog,
        pristine=pristine,
        csr=csr,
        use_cache=use_cache,
        timer=timer,
    )
    image = bytearray(parent_bytes)
    stack = [base_line]

    for addon_id in addons:
        with timer.stage(f"addon {addon_id}"):
            n, line = _check_addon(
                image,
                addon_id=addon_id,
                base_id=base_id,
                catalog=catalog,
                csr_root_arg=csr_root_arg,
                disc=disc,
            )
        total_recs += n
        stack.append(line)

    if output:
        with timer.stage("write"):
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(image)
        print(f"Wrote {output} ({len(image)} bytes)")

    print("Stack:")
    for line in stack:
        print(f"  - {line}")
    print(f"PASS -- builder config applies cleanly ({total_recs} total records)")


def verify_bases(
    bases: list[str],
    *,
    catalog: dict[str, dict],
    modding_manifest: dict,
    csr: Path | None,
    csr_manifest: dict | None,
    use_cache: bool,
    timer: Timer,
    csr_root_arg: Path | None,
    pristine_override: Path | None,
) -> None:
    """One addon at a time on each disc, matching a player picking one mod.

    The parent BIN is built once per disc and each addon is applied to a copy,
    so a three-disc base with seven addons rebuilds three images instead of
    twenty-one.
    """
    plan: list[tuple[str, list[int], list[str]]] = []
    for base_id in bases:
        discs = discs_for_base(base_id, csr_manifest)
        addon_ids = addons_for_base(modding_manifest, base_id)
        if not addon_ids:
            raise SystemExit(f"No addons in the manifest for base {base_id!r}")
        print(f"Queue {base_id} discs {discs} addons {len(addon_ids)}")
        plan.append((base_id, discs, addon_ids))

    stacks = sum(len(discs) * len(addons) for _, discs, addons in plan)
    print(f"\nVerifying {stacks} stacks, one addon at a time")
    for base_id, discs, addon_ids in plan:
        for disc in discs:
            pristine = (
                pristine_override.expanduser().resolve()
                if pristine_override
                else default_pristine_arg(disc).resolve()
            )
            if not pristine.is_file():
                raise SystemExit(f"Missing pristine image: {pristine}")
            print(f"\n======== {base_id} disc {disc} ========", flush=True)
            parent_bytes, _line, _recs = _load_base(
                disc=disc,
                base_id=base_id,
                catalog=catalog,
                pristine=pristine,
                csr=csr,
                use_cache=use_cache,
                timer=timer,
            )
            for addon_id in addon_ids:
                with timer.stage(f"{base_id} d{disc} {addon_id}"):
                    _check_addon(
                        bytearray(parent_bytes),
                        addon_id=addon_id,
                        base_id=base_id,
                        disc=disc,
                        catalog=catalog,
                        csr_root_arg=csr_root_arg,
                    )
            del parent_bytes

    print(f"\nPASS -- {stacks} base+addon stacks apply cleanly")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify builder base+addon stack on a pristine disc"
    )
    ap.add_argument(
        "bases",
        nargs="*",
        help="all, clean, csr, csr-plus, and/or highwind",
    )
    ap.add_argument(
        "--pristine",
        type=Path,
        default=None,
        help="Retail NTSC-U disc .bin (default: workspace/pristine/FINALFANTASY7_DN.bin)",
    )
    ap.add_argument("--disc", type=int, default=None, choices=(1, 2, 3))
    ap.add_argument(
        "--base",
        default=None,
        help="One stack: clean | csr | csr-plus | highwind (requires --disc)",
    )
    ap.add_argument(
        "--addon",
        action="append",
        default=[],
        dest="addons",
        help="Mod id for one stack (repeatable), in apply order",
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
        help="Ignore cache/<base>/ and rebuild the parent from pristine + CSR layer",
    )
    args = ap.parse_args()
    timer = Timer()

    one_stack = args.disc is not None or args.base is not None or bool(args.addons)
    if args.bases and one_stack:
        raise SystemExit(
            "Pass base names (all, clean, csr, ...) or --disc/--base/--addon, not both."
        )
    if args.output is not None and args.bases:
        raise SystemExit("--output only applies to a single --disc/--base stack")

    csr = csr_root(args.csr_root)
    catalog, modding_manifest = _load_catalog(
        [args.manifest, *args.extra_manifest], csr
    )

    if args.bases:
        bases = expand_base_names(args.bases)
        csr_manifest = None
        if any(b not in ("clean", "unmodified") for b in bases):
            if csr is None:
                raise SystemExit("Pass --csr-root or set FF7_CSR_ROOT")
            _, csr_manifest = _load_manifest(csr / "builder" / "manifest.json")
            print(f"CSR root: {csr}")
        verify_bases(
            bases,
            catalog=catalog,
            modding_manifest=modding_manifest,
            csr=csr,
            csr_manifest=csr_manifest,
            use_cache=not args.no_cache,
            timer=timer,
            csr_root_arg=args.csr_root,
            pristine_override=args.pristine,
        )
        timer.total()
        return 0

    if args.disc is None or not args.base:
        raise SystemExit(
            "Need --disc and --base for one stack, or pass all / clean / csr / "
            "csr-plus / highwind."
        )

    pristine = (
        args.pristine.expanduser().resolve()
        if args.pristine
        else default_pristine_arg(args.disc).resolve()
    )
    if not pristine.is_file():
        raise SystemExit(f"Missing pristine image: {pristine}")

    verify_stack(
        disc=args.disc,
        base_id=args.base.strip(),
        addons=args.addons,
        catalog=catalog,
        pristine=pristine,
        csr=csr,
        use_cache=not args.no_cache,
        output=args.output,
        timer=timer,
        csr_root_arg=args.csr_root,
    )
    timer.total()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
