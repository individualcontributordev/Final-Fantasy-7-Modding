#!/usr/bin/env python3
"""Build Field-encounter-on-<base> layers without CDmage.

  python mods/field-random-encounters/scripts/build_on_base.py --against csr-plus --discs 1
  python mods/field-random-encounters/scripts/build_on_base.py --against clean --density light --discs 1

Omit --density to pick Light / Standard / Dense / All interactively.

Version from mods/field-random-encounters/VERSION unless --version.
Writes packs under builder/ and updates builder/manifest.json.
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

_MOD_SCRIPTS = Path(__file__).resolve().parent
_MOD = _MOD_SCRIPTS.parent
_ROOT = _MOD.parent.parent  # mods/<name> → repo root
_SHARED = _ROOT / "scripts"
# Prefer this mod's scripts over deprecated repo-root shims with the same names.
for p in (_SHARED, _MOD_SCRIPTS):
	if str(p) not in sys.path:
		sys.path.insert(0, str(p))


from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from build_field_bin import build as build_field_stub  # noqa: E402
from density import parse_densities, prompt_densities, rate_label  # noqa: E402
from pack_meta import (  # noqa: E402
	AGAINST,
	VERSION_FILE,
	meta_for,
	update_manifest,
	write_pack_json,
)
from psx_mode2_iso import (  # noqa: E402
	extract_file,
	find_file,
	replace_file_within_sectors,
)

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


def read_default_version() -> str:
	if not VERSION_FILE.is_file():
		raise SystemExit(
			f"Missing {VERSION_FILE.relative_to(_ROOT)} — create it or pass --version"
		)
	version = VERSION_FILE.read_text(encoding="utf-8").strip().splitlines()[0].strip()
	if not re.fullmatch(r"[0-9]+(\.[0-9]+)*", version):
		raise SystemExit(f"Bad version in {VERSION_FILE.name}: {version!r}")
	return version


def fetch_json(url: str) -> dict:
	print(f"  GET {url}")
	try:
		with urllib.request.urlopen(url, timeout=120) as resp:
			return json.loads(resp.read().decode("utf-8"))
	except urllib.error.URLError as err:
		raise SystemExit(f"Download failed: {url}\n{err}") from err


def resolve_base_id(against: str, manifest: dict) -> str:
	if against == "clean":
		return "clean"

	bases = [b for b in (manifest.get("bases") or []) if b.get("enabled") is not False]
	ids = [str(b.get("id", "")) for b in bases]

	if against == "highwind":
		cands = [i for i in ids if i.startswith("highwind-v")]
	elif against == "csr-plus":
		cands = [i for i in ids if i.startswith("csr-plus-v")]
	elif against == "csr":
		cands = [i for i in ids if re.fullmatch(r"csr-v[0-9.]+", i)]
	else:
		raise SystemExit(f"Unknown against: {against}")

	if not cands:
		raise SystemExit(
			f"No enabled base for --against {against} in CSR manifest. Saw: {ids}"
		)
	preferred = AGAINST[against]["base_id"]
	if preferred in cands:
		return preferred
	cands.sort()
	return cands[-1]


def resolve_remote_layer_url(manifest_url: str, base_id: str, disc: int, manifest: dict) -> str:
	entry = next(
		(b for b in manifest.get("bases") or [] if b.get("id") == base_id),
		None,
	)
	if not entry:
		raise SystemExit(f"Base id {base_id!r} not found in CSR manifest")
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


def stub_and_inject(base_bin: Path, work_dir: Path, rate: int) -> Path:
	print("=== extract FIELD/FIELD.BIN ===")
	base_bytes = bytearray(base_bin.read_bytes())
	meta = find_file(base_bytes, FIELD_PATH)
	field = extract_file(base_bytes, FIELD_PATH)
	field_path = work_dir / "FIELD.BIN"
	field_path.write_bytes(field)
	print(f"  LBA={meta.lba} size={meta.size} → {field_path}")

	print(f"=== stub FIELD.BIN (rate {rate}%) ===")
	field_new = build_field_stub(
		field_path, work_dir / "FIELD.BIN.new", keep_dec=False, rate=rate
	)
	new_bytes = field_new.read_bytes()
	print(f"  FIELD.BIN.new = {len(new_bytes)} bytes (slot {meta.size})")

	print("=== inject FIELD.BIN.new (within sector allocation) ===")
	patched = work_dir / "patched.bin"
	shutil.copy2(base_bin, patched)
	img = bytearray(patched.read_bytes())
	replace_file_within_sectors(img, FIELD_PATH, new_bytes)
	patched.write_bytes(img)
	print(f"  wrote {patched}")
	return patched


def build_one(
	*,
	against: str,
	disc: int,
	version: str,
	base_id: str,
	meta: dict,
	pristine_dir: Path,
	manifest_url: str,
	csr_manifest: dict | None,
	base_layer_arg: str | None,
	keep_work: bool,
) -> Path:
	pack_id = f"{meta['pack_prefix']}-v{version}"
	pristine = pristine_dir / f"FINALFANTASY7_D{disc}.bin"
	if not pristine.is_file():
		raise SystemExit(f"Missing pristine: {pristine}")

	work_dir = WORK_ROOT / f"{against}-r{meta['rate']}-d{disc}"
	if work_dir.exists():
		shutil.rmtree(work_dir)
	work_dir.mkdir(parents=True)

	layer = None
	if against != "clean":
		if base_layer_arg:
			layer = load_layer(base_layer_arg)
		else:
			assert csr_manifest is not None
			url = resolve_remote_layer_url(manifest_url, base_id, disc, csr_manifest)
			layer = load_layer(url)
		if layer.get("format") != "ic-layer-v1":
			raise SystemExit("base layer must be ic-layer-v1")

	base_bin = work_dir / "base.bin"
	make_base_image(pristine, layer, base_bin)
	patched_bin = stub_and_inject(base_bin, work_dir, meta["rate"])

	print("=== diff → field encounter layer ===")
	out_dir = _ROOT / "builder" / pack_id / "layers"
	out_dir.mkdir(parents=True, exist_ok=True)
	out_path = out_dir / f"disc{disc}.layer.json"
	layer_id = f"{meta['pack_prefix']}-disc{disc}-v{version}"
	description = (
		f"Field encounters {meta['rate']}% RCnt2 FORCE stub — NTSC-U Disc {disc} "
		f"(against {base_id})"
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
		description="Build Field encounter-on-base layers from remote CSR layers + pristine."
	)
	ap.add_argument(
		"--version",
		default=None,
		help=f"Version (default: {VERSION_FILE.relative_to(_ROOT)})",
	)
	ap.add_argument("--discs", required=True, help="e.g. 1 or 1,2,3")
	ap.add_argument(
		"--against",
		required=True,
		choices=sorted(AGAINST.keys()),
		help="Builder base this pack stacks on",
	)
	ap.add_argument(
		"--density",
		"--rate",
		dest="density",
		default=None,
		metavar="PRESET",
		help=(
			"light / standard / dense / all (or 25 / 50 / 75). "
			"Omit to pick interactively."
		),
	)
	ap.add_argument("--base-id", default=None, help="Override CSR base id")
	ap.add_argument(
		"--pristine-dir",
		type=Path,
		default=PRISTINE_DIR,
		help="Folder with FINALFANTASY7_DN.bin",
	)
	ap.add_argument(
		"--csr-manifest",
		default=DEFAULT_CSR_MANIFEST,
		help="Remote CSR builder manifest URL",
	)
	ap.add_argument(
		"--base-layer",
		default=None,
		help="Local path or URL to one disc's base layer JSON",
	)
	ap.add_argument("--keep-work", action="store_true", help="Keep temp work dirs")
	args = ap.parse_args()

	version = (args.version or read_default_version()).strip()
	if not re.fullmatch(r"[0-9]+(\.[0-9]+)*", version):
		raise SystemExit(f"Weird version '{version}'")

	rates = (
		parse_densities(args.density)
		if args.density is not None
		else prompt_densities(allow_all=True, default="standard")
	)
	discs = parse_discs(args.discs)
	if args.base_layer and len(discs) != 1:
		raise SystemExit("--base-layer only works with a single --discs value")

	against = args.against
	csr_manifest = None
	if against == "clean":
		base_id = "clean"
	elif args.base_id:
		base_id = args.base_id.strip()
	else:
		csr_manifest = fetch_json(args.csr_manifest)
		base_id = resolve_base_id(against, csr_manifest)

	for rate in rates:
		meta = meta_for(against, rate)
		meta["base_id"] = base_id

		print(f"\n######## {rate_label(rate)} on {against} ########")
		print(f"Against:  {against}")
		print(f"Base id:  {base_id}")
		print(f"Density:  {rate_label(rate)}")
		print(f"Version:  {version}")
		print(f"Discs:    {discs}")
		print(f"Pristine: {args.pristine_dir}")

		for disc in discs:
			print(f"\n######## Disc {disc} ########")
			build_one(
				against=against,
				disc=disc,
				version=version,
				base_id=base_id,
				meta=meta,
				pristine_dir=args.pristine_dir.expanduser().resolve(),
				manifest_url=args.csr_manifest,
				csr_manifest=csr_manifest,
				base_layer_arg=args.base_layer,
				keep_work=args.keep_work,
			)

		pack_id = f"{meta['pack_prefix']}-v{version}"
		pack_dir = _ROOT / "builder" / pack_id
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
			compatible_bases=[base_id],
			discs=existing,
			rate=meta["rate"],
			group_label=meta.get("group_label"),
			option_label=meta.get("option_label"),
		)
		update_manifest(
			pack_id=pack_id,
			pack_prefix=meta["pack_prefix"],
			version=version,
			display=meta["display"],
			blurb=meta["blurb"],
			compatible_bases=[base_id],
			discs=existing,
			rate=meta["rate"],
			group_label=meta.get("group_label"),
			option_label=meta.get("option_label"),
		)
		print(f"\nUpdated builder/{pack_id}/ and manifest (discs={existing})")
		print(f"compatibleBases={base_id!r}; exclusiveGroup=field-encounter-rate")

	print("\nCommit JSON under builder/ only.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
