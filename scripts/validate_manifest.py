#!/usr/bin/env python3
"""Validate the local builder manifest and its published layer files.

Default path is ``builder/manifest.json``. Each add-on must have a unique id
and a ``discs`` map whose paths exist next to the manifest. ``autoIncludeWhen``
ids must name another add-on in this file (unless they start with DISABLED-).
Prints every error and returns nonzero. Does not fetch the network or rewrite
files."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "builder" / "manifest.json"


def validate(manifest_path: Path) -> list[str]:
    """Return a list of error strings; empty list means the manifest is valid."""
    errors: list[str] = []

    try:
        text = manifest_path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"cannot read {manifest_path}: {e}"]

    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as e:
        return [f"invalid JSON in {manifest_path}: {e}"]

    builder_dir = manifest_path.parent
    addons = manifest.get("addons") or []
    if not isinstance(addons, list):
        errors.append("'addons' is not a list")
        addons = []

    addon_ids: set[str] = set()
    for i, addon in enumerate(addons):
        if not isinstance(addon, dict):
            errors.append(f"addons[{i}] is not an object")
            continue
        aid = addon.get("id")
        if not aid:
            errors.append(f"addons[{i}] missing 'id'")
            continue
        if aid in addon_ids:
            errors.append(f"duplicate addon id: {aid}")
        addon_ids.add(aid)

        # Referenced layer files (discs: {"1": "./pack/layers/disc1.layer.json", ...})
        discs = addon.get("discs") or {}
        if not isinstance(discs, dict):
            errors.append(f"{aid}: 'discs' is not an object")
            discs = {}
        for disc_num, rel in discs.items():
            if not rel:
                errors.append(f"{aid}: discs[{disc_num!r}] is empty")
                continue
            layer_path = (builder_dir / str(rel).lstrip("./")).resolve()
            if not layer_path.is_file():
                errors.append(
                    f"{aid}: discs[{disc_num!r}] -> {rel!r} does not exist "
                    f"(resolved {layer_path})"
                )

        # Enabled add-ons may auto-include another pack. Skip DISABLED-*
        # sentinels; any other selected id must exist in this manifest.
        aiw = addon.get("autoIncludeWhen") or {}
        if isinstance(aiw, dict) and addon.get("enabled", True):
            parent = aiw.get("addonSelected")
            if (
                parent
                and not str(parent).startswith("DISABLED-")
                and parent not in addon_ids
                and not any(
                    a.get("id") == parent for a in addons if isinstance(a, dict)
                )
            ):
                errors.append(
                    f"{aid}: autoIncludeWhen.addonSelected={parent!r} "
                    f"does not match any addon id in manifest"
                )

    return errors


def main(argv: list[str]) -> int:
    manifest_path = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_MANIFEST
    errors = validate(manifest_path)
    if errors:
        print(f"INVALID: {manifest_path} ({len(errors)} error(s))", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK: {manifest_path} is valid ({manifest_path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
