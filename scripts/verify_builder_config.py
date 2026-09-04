#!/usr/bin/env python3
"""Reconstruct and validate a local browser-builder mod selection.

One stack:

  python3 scripts/verify_builder_config.py \\
    --disc 1 --base csr-plus --addon fanfare-skip-on-csr-plus

Every published mod on one or more bases (same names as rebuild_on_base.py):

  python3 scripts/verify_builder_config.py all
  python3 scripts/verify_builder_config.py clean
  python3 scripts/verify_builder_config.py csr csr-plus

``all`` is csr + csr-plus + highwind. Add ``clean`` to include Unmodified packs.

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
)
from libs.timing import Timer

CSR_FAMILY = ("csr", "csr-plus", "highwind")
KNOWN_BASES = CSR_FAMILY + ("clean",)


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


def expand_bases(tokens: list[str]) -> list[str]:
    """Turn rebuild-style names into unique bases, preserving order."""
    wanted: list[str] = []
    for token in tokens:
        if token == "all":
            wanted.extend(CSR_FAMILY)
        elif token in KNOWN_BASES:
            wanted.append(token)
        else:
            raise SystemExit(
                f"Unknown base {token!r}. Use all, clean, csr, csr-plus, or highwind."
            )
    return list(dict.fromkeys(wanted))


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

    total_recs = 0
    stack: list[str] = []

    if base_id in ("clean", "unmodified"):
        image = bytearray(pristine.read_bytes())
        stack.append("base:clean (pristine only)")
        print("  OK base clean (no base layer)")
    else:
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
            image = bytearray(parent_bytes)
        if base_id in catalog:
            lp = _layer_path(catalog[base_id], disc)
            with timer.stage("check_base"):
                n = _check_records(image, lp)
            total_recs += n
            stack.append(f"base:{base_id} ({n} records)")
            print(f"  OK base {base_id} <- {lp.name} ({n} records, src={parent_path})")
        else:
            stack.append(f"base:{base_id} (from {parent_path})")
            print(f"  OK base {base_id} <- {parent_path}")

    for addon_id in addons:
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
        with timer.stage(f"addon {addon_id}"):
            n = _apply_and_check(image, lp)
        total_recs += n
        stack.append(f"addon:{addon_id} ({lp.name}, {n} records)")
        print(f"  OK addon {addon_id} <- {lp.relative_to(meta['builder_dir'])} ({n} records)")

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
    """One addon at a time on each disc, matching a player picking one mod."""
    jobs: list[tuple[str, int, str]] = []
    for base_id in bases:
        discs = discs_for_base(base_id, csr_manifest)
        addon_ids = addons_for_base(modding_manifest, base_id)
        if not addon_ids:
            raise SystemExit(f"No addons in the manifest for base {base_id!r}")
        print(f"Queue {base_id} discs {discs} addons {len(addon_ids)}")
        for addon_id in addon_ids:
            for disc in discs:
                jobs.append((base_id, disc, addon_id))

    print(f"\nVerifying {len(jobs)} stacks, one at a time")
    for base_id, disc, addon_id in jobs:
        pristine = (
            pristine_override.expanduser().resolve()
            if pristine_override
            else default_pristine_arg(disc).resolve()
        )
        if not pristine.is_file():
            raise SystemExit(f"Missing pristine image: {pristine}")
        print(f"\n======== {base_id} disc {disc} {addon_id} ========", flush=True)
        with timer.stage(f"{base_id} d{disc} {addon_id}"):
            verify_stack(
                disc=disc,
                base_id=base_id,
                addons=[addon_id],
                catalog=catalog,
                pristine=pristine,
                csr=csr,
                use_cache=use_cache,
                output=None,
                timer=timer,
                csr_root_arg=csr_root_arg,
            )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify builder base+addon stack on a pristine disc"
    )
    ap.add_argument(
        "bases",
        nargs="*",
        help="all, clean, csr, csr-plus, and/or highwind (every mod on those bases)",
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
        help="Do not write cache/<base>/ when reconstructing a CSR base",
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
        bases = expand_bases(args.bases)
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
