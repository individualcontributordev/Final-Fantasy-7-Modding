#!/usr/bin/env python3
"""Build Encounter-on-<base> layers without CDmage.

Pulls the published CSR base layer from the remote builder manifest (or a local
JSON), applies it onto your local pristine disc, stubs FIELD.BIN, pad-injects,
diffs, and updates builder/manifest.json.

Examples (Git Bash):

  # CSR+ Disc 1 — downloads csr-plus disc1.layer.json from Pages
  python scripts/build_encounter_on_base.py --against csr-plus --discs 1 --version 0.1.0

  # CSR Disc 1
  python scripts/build_encounter_on_base.py --against csr --discs 1 --version 0.1.0

  # Unmodified (no remote layer — stub retail FIELD.BIN directly)
  python scripts/build_encounter_on_base.py --against clean --discs 1 --version 0.1.0

Requires workspace/pristine/FINALFANTASY7_DN.bin. Needs network unless you pass
--base-layer. Temp images go under workspace/iso-extract/_on_base/ (gitignored).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

_SCRIPTS = Path(__file__).resolve().parent
_ROOT = _SCRIPTS.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from build_encounter_layers import (  # noqa: E402
    AGAINST,
    update_manifest,
    write_pack_json,
)
from build_field_encounter_patch import build as build_field_stub  # noqa: E402
from psx_mode2_iso import extract_file, find_file, replace_file_padded  # noqa: E402

PRISTINE_DIR = _ROOT / "workspace" / "pristine"
WORK_ROOT = _ROOT / "workspace" / "iso-extract" / "_on_base"
DEFAULT_CSR_MANIFEST = (
    "https://individualcontributor.dev/Final-Fantasy-7-CSR/builder/manifest.json"
)
FIELD_PATH = "FIELD/FIELD.BIN"


def parse_discs(spec: str) -> list[int]:
    discs: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        disc = int(part)
        if disc not in (1, 2, 3):
            raise SystemExit(f"Disc must be 1, 2, or 3 — got {disc}")
        discs.append(disc)
    if not discs:
        raise SystemExit("Pass at least one disc, e.g. --discs 1")
    return discs


def fetch_json(url: str) -> dict:
    print(f"  GET {url}")
    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as err:
        raise SystemExit(f"Download failed: {url}\n{err}") from err


def resolve_remote_layer_url(manifest_url: str, base_id: str, disc: int) -> str:
    manifest = fetch_json(manifest_url)
    entry = next(
        (b for b in manifest.get("bases") or [] if b.get("id") == base_id),
        None,
    )
    if not entry:
        raise SystemExit(
            f"Base id {base_id!r} not found in {manifest_url}. "
            f"Saw: {[b.get('id') for b in manifest.get('bases') or []]}"
        )
    if entry.get("enabled") is False:
        raise SystemExit(f"Base {base_id} is disabled in remote manifest")
    discs = entry.get("discs") or {}
    rel = discs.get(str(disc))
    if not rel:
        raise SystemExit(f"{base_id} has no layer for disc {disc}")
    return urljoin(manifest_url, rel)


def load_layer(path_or_url: str) -> dict:
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return fetch_json(path_or_url)
    path = Path(path_or_url).expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"Missing layer file: {path}")
    print(f"  read {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def make_base_image(pristine: Path, layer: dict | None, out_bin: Path) -> None:
    print(f"=== apply base → {out_bin.name} ===")
    image = bytearray(pristine.read_bytes())
    if layer is not None:
        apply_layer(image, layer)
        print(f"  applied {len(layer.get('records') or [])} records")
    else:
        print("  (clean — no base layer)")
    out_bin.parent.mkdir(parents=True, exist_ok=True)
    out_bin.write_bytes(image)
    print(f"  wrote {out_bin} ({len(image)} bytes)")


def stub_and_inject(base_bin: Path, work_dir: Path) -> Path:
    """Extract FIELD.BIN from base, stub, pad-inject into a copy. Returns patched path."""
    print("=== extract FIELD/FIELD.BIN ===")
    base_bytes = bytearray(base_bin.read_bytes())
    meta = find_file(base_bytes, FIELD_PATH)
    field = extract_file(base_bytes, FIELD_PATH)
    field_path = work_dir / "FIELD.BIN"
    field_path.write_bytes(field)
    print(f"  LBA={meta.lba} size={meta.size} → {field_path}")

    print("=== stub FIELD.BIN ===")
    field_new = build_field_stub(field_path, work_dir / "FIELD.BIN.new", keep_dec=False)
    new_bytes = field_new.read_bytes()
    print(f"  FIELD.BIN.new = {len(new_bytes)} bytes (slot {meta.size})")

    print("=== pad-inject FIELD.BIN.new ===")
    patched = work_dir / "patched.bin"
    shutil.copy2(base_bin, patched)
    img = bytearray(patched.read_bytes())
    replace_file_padded(img, FIELD_PATH, new_bytes)
    patched.write_bytes(img)
    print(f"  wrote {patched}")
    return patched


def build_one(
    *,
    against: str,
    disc: int,
    version: str,
    pristine_dir: Path,
    manifest_url: str,
    base_layer_arg: str | None,
    keep_work: bool,
) -> Path:
    meta = AGAINST[against]
    pack_id = f"{meta['pack_prefix']}-v{version}"
    pristine = pristine_dir / f"FINALFANTASY7_D{disc}.bin"
    if not pristine.is_file():
        raise SystemExit(f"Missing pristine: {pristine}")

    work_dir = WORK_ROOT / f"{against}-d{disc}"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    layer = None
    if against != "clean":
        if base_layer_arg:
            layer = load_layer(base_layer_arg)
        else:
            url = resolve_remote_layer_url(manifest_url, meta["base_id"], disc)
            layer = load_layer(url)
        if layer.get("format") != "ic-layer-v1":
            raise SystemExit("base layer must be ic-layer-v1")

    base_bin = work_dir / "base.bin"
    make_base_image(pristine, layer, base_bin)
    patched_bin = stub_and_inject(base_bin, work_dir)

    print("=== diff → encounter layer ===")
    out_dir = _ROOT / "builder" / pack_id / "layers"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"disc{disc}.layer.json"
    layer_id = f"{meta['pack_prefix']}-disc{disc}-v{version}"
    description = (
        f"Encounter RCnt2 FORCE stub — NTSC-U Disc {disc} "
        f"(against {meta['base_id']})"
    )
    built = build_layer(
        base_bin,
        patched_bin,
        layer_id=layer_id,
        description=description,
    )
    out_path.write_text(json.dumps(built, indent=2) + "\n", encoding="utf-8")
    stats = built["stats"]
    print(
        f"  wrote {out_path.relative_to(_ROOT)}  "
        f"records={stats['records']} changedBytes={stats['changedBytes']}"
    )
    if stats["records"] == 0 or stats["changedBytes"] == 0:
        raise SystemExit("Empty layer — stub/inject produced no disc changes")

    # Verify: base + layer == patched
    print("=== verify ===")
    check = bytearray(base_bin.read_bytes())
    apply_layer(check, built)
    if bytes(check) != patched_bin.read_bytes():
        raise SystemExit("VERIFY FAIL — layer apply does not match patched image")
    print("  OK")

    if not keep_work:
        shutil.rmtree(work_dir)
        print(f"  cleaned {work_dir}")

    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build Encounter-on-base layers from remote CSR layers + local pristine."
    )
    ap.add_argument("--version", required=True, help="e.g. 0.1.0")
    ap.add_argument("--discs", required=True, help="e.g. 1 or 1,2,3")
    ap.add_argument(
        "--against",
        required=True,
        choices=sorted(AGAINST.keys()),
        help="Builder base this Encounter pack stacks on",
    )
    ap.add_argument(
        "--pristine-dir",
        type=Path,
        default=PRISTINE_DIR,
        help="Folder with FINALFANTASY7_DN.bin (default: workspace/pristine)",
    )
    ap.add_argument(
        "--csr-manifest",
        default=DEFAULT_CSR_MANIFEST,
        help="Remote CSR builder manifest URL (ignored for --against clean)",
    )
    ap.add_argument(
        "--base-layer",
        default=None,
        help="Local path or URL to one disc's base layer JSON (skips manifest lookup)",
    )
    ap.add_argument(
        "--keep-work",
        action="store_true",
        help="Keep workspace/iso-extract/_on_base/<against>-dN/ temps",
    )
    args = ap.parse_args()

    version = args.version.strip()
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)*", version):
        raise SystemExit(f"Weird version '{version}'")

    against = args.against
    meta = AGAINST[against]
    discs = parse_discs(args.discs)
    if args.base_layer and len(discs) != 1:
        raise SystemExit("--base-layer only works with a single --discs value")

    print(f"Against:  {against} ({meta['base_id']})")
    print(f"Version:  {version}")
    print(f"Discs:    {discs}")
    print(f"Pristine: {args.pristine_dir}")

    for disc in discs:
        print(f"\n######## Disc {disc} ########")
        build_one(
            against=against,
            disc=disc,
            version=version,
            pristine_dir=args.pristine_dir.expanduser().resolve(),
            manifest_url=args.csr_manifest,
            base_layer_arg=args.base_layer,
            keep_work=args.keep_work,
        )

    pack_id = f"{meta['pack_prefix']}-v{version}"
    pack_dir = _ROOT / "builder" / pack_id
    # Merge discs already on disk into pack/manifest (re-run safe).
    # Path.stem of disc1.layer.json is "disc1.layer" — parse the filename instead.
    existing: list[int] = []
    layers_dir = pack_dir / "layers"
    if layers_dir.is_dir():
        for p in layers_dir.glob("disc*.layer.json"):
            mid = p.name.removeprefix("disc").removesuffix(".layer.json")
            if mid.isdigit():
                existing.append(int(mid))
    existing = sorted(set(existing))
    if not existing:
        raise SystemExit(f"No disc*.layer.json under {layers_dir}")
    write_pack_json(
        pack_dir,
        pack_id=pack_id,
        version=version,
        display=meta["display"],
        blurb=meta["blurb"],
        compatible_bases=[meta["base_id"]],
        discs=existing,
    )
    update_manifest(
        pack_id=pack_id,
        version=version,
        display=meta["display"],
        blurb=meta["blurb"],
        compatible_bases=[meta["base_id"]],
        discs=existing,
    )
    print(f"\nUpdated builder/{pack_id}/ and manifest (discs={existing})")
    print("Commit JSON under builder/ only. Smoke-test DuckStation New Game on a builder stack.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
