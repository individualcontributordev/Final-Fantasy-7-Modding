#!/usr/bin/env python3
"""Build fanfare-skip layers for clean / CSR / Highwind.

  python mods/fanfare-skip/scripts/build_on_base.py --against clean --discs 1
  python mods/fanfare-skip/scripts/build_on_base.py --against all --discs 1,2,3
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
_ROOT = _MOD.parent.parent
_SHARED = _ROOT / "scripts"
for pth in (_SHARED, _MOD_SCRIPTS):
	if str(pth) not in sys.path:
		sys.path.insert(0, str(pth))

from apply_layer import apply_layer  # noqa: E402
from bin_diff_to_layer import build_layer  # noqa: E402
from build_battle_x import build as build_battle  # noqa: E402
from psx_mode2_iso import extract_file, find_file, replace_file_padded  # noqa: E402

PRISTINE_DIR = _ROOT / "workspace" / "pristine"
WORK_ROOT = _ROOT / "workspace" / "iso-extract" / "_fanfare_skip"
MANIFEST_PATH = _ROOT / "builder" / "manifest.json"
VERSION_FILE = _MOD / "VERSION"
BATTLE_PATH = "BATTLE/BATTLE.X"
HINT = 'No victory fanfare or win poses — loot and exp still apply.'
DEFAULT_CSR_MANIFEST = (
	"https://individualcontributor.dev/Final-Fantasy-7-CSR/builder/manifest.json"
)

AGAINST = {
	"clean": {
		"base_id": "clean",
		"prefix_stem": "fanfare-skip",
		"on_label": "",
		"compatible": ["clean"],
	},
	"csr": {
		"base_id": "csr-v0.14.1",
		"prefix_stem": "fanfare-skip-on-csr",
		"on_label": " (on CSR)",
		"compatible": ["csr-v0.14.1"],
	},
	"highwind": {
		"base_id": "highwind-v0.2.0",
		"prefix_stem": "fanfare-skip-on-highwind",
		"on_label": " (on Highwind)",
		"compatible": ["highwind-v0.2.0"],
	},
}


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


def read_version() -> str:
	version = VERSION_FILE.read_text(encoding="utf-8").strip().splitlines()[0].strip()
	if not re.fullmatch(r"[0-9]+(\.[0-9]+)*", version):
		raise SystemExit(f"Bad version in VERSION: {version!r}")
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
	elif against == "csr":
		cands = [i for i in ids if i.startswith("csr-v") and "plus" not in i]
		if not cands:
			cands = [i for i in ids if i.startswith("csr")]
	else:
		raise SystemExit(f"unknown against {against}")
	if not cands:
		return AGAINST[against]["base_id"]
	cands.sort()
	return cands[-1]


def resolve_remote_layer_url(
	manifest_url: str, base_id: str, disc: int, manifest: dict
) -> str:
	bases = manifest.get("bases") or []
	base = next((b for b in bases if str(b.get("id")) == base_id), None)
	if base is None:
		raise SystemExit(f"base {base_id} not in remote manifest")
	discs = base.get("discs") or {}
	rel = discs.get(str(disc)) or discs.get(disc)
	if not rel:
		raise SystemExit(f"{base_id} has no layer for disc {disc}")
	return urljoin(manifest_url, str(rel))


def load_layer(path_or_url: str) -> dict:
	if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
		return fetch_json(path_or_url)
	path = Path(path_or_url).expanduser().resolve()
	if not path.is_file():
		raise SystemExit(f"Missing layer file: {path}")
	print(f"  read {path}")
	return json.loads(path.read_text(encoding="utf-8"))


def make_base_image(pristine: Path, layer: dict | None, out_bin: Path) -> None:
	print(f"=== apply base -> {out_bin.name} ===")
	image = bytearray(pristine.read_bytes())
	if layer is not None:
		apply_layer(image, layer)
		print(f"  applied {len(layer.get('records') or [])} records")
	else:
		print("  (clean — no base layer)")
	out_bin.parent.mkdir(parents=True, exist_ok=True)
	out_bin.write_bytes(image)
	print(f"  wrote {out_bin} ({len(image)} bytes)")


def patch_and_inject(base_bin: Path, work_dir: Path) -> Path:
	print(f"=== extract {BATTLE_PATH} ===")
	base_bytes = bytearray(base_bin.read_bytes())
	meta = find_file(base_bytes, BATTLE_PATH)
	battle = extract_file(base_bytes, BATTLE_PATH)
	battle_path = work_dir / "BATTLE.X"
	battle_path.write_bytes(battle)
	print(f"  LBA={meta.lba} size={meta.size} -> {battle_path}")

	print("=== patch BATTLE.X ===")
	battle_new = build_battle(battle_path, work_dir / "BATTLE.X.new", keep_dec=False)
	new_bytes = battle_new.read_bytes()
	print(f"  BATTLE.X.new = {len(new_bytes)} bytes (slot {meta.size})")
	if len(new_bytes) > meta.size:
		raise SystemExit(
			f"patched BATTLE.X ({len(new_bytes)}) larger than slot ({meta.size})"
		)

	print("=== pad-inject BATTLE.X.new ===")
	patched = work_dir / "patched.bin"
	shutil.copy2(base_bin, patched)
	img = bytearray(patched.read_bytes())
	replace_file_padded(img, BATTLE_PATH, new_bytes)
	patched.write_bytes(img)
	print(f"  wrote {patched}")
	return patched


def write_pack_json(
	pack_dir: Path,
	*,
	pack_id: str,
	version: str,
	display: str,
	blurb: str,
	compatible: list[str],
	discs: list[int],
) -> None:
	pack = {
		"id": pack_id,
		"name": display,
		"kind": "mod",
		"version": version,
		"blurb": blurb,
		"hint": HINT,
		"format": "ic-layer-v1",
		"compatibleBases": compatible,
		"discs": {str(d): f"./layers/disc{d}.layer.json" for d in discs},
	}
	pack_dir.mkdir(parents=True, exist_ok=True)
	(pack_dir / "pack.json").write_text(
		json.dumps(pack, indent=2) + "\n", encoding="utf-8"
	)


def update_manifest(
	*,
	pack_id: str,
	version: str,
	display: str,
	blurb: str,
	compatible: list[str],
	discs: list[int],
) -> None:
	data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
	entry = {
		"id": pack_id,
		"name": f"{display} v{version}",
		"kind": "mod",
		"blurb": blurb,
		"hint": HINT,
		"format": "ic-layer-v1",
		"compatibleBases": compatible,
		"discs": {
			str(d): f"./{pack_id}/layers/disc{d}.layer.json" for d in discs
		},
		"enabled": True,
	}
	addons = data.setdefault("addons", [])
	addons[:] = [a for a in addons if str(a.get("id", "")) != pack_id]
	addons.append(entry)
	MANIFEST_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_one(
	*,
	against: str,
	disc: int,
	version: str,
	manifest_url: str,
	csr_manifest: dict | None,
	keep_work: bool,
):
	cfg = dict(AGAINST[against])
	base_id = cfg["base_id"]
	if against != "clean" and csr_manifest is not None:
		base_id = resolve_base_id(against, csr_manifest)
		cfg["base_id"] = base_id
		cfg["compatible"] = [base_id]

	pack_id = f"{cfg['prefix_stem']}-v{version}"
	display = "Fanfare Skip"
	blurb = 'After the last enemy dies, skip the victory fanfare and win poses (like Midgar train fights). Exp, AP, gil, and items still apply; loot/level-up screens still show.'

	pristine = PRISTINE_DIR / f"FINALFANTASY7_D{disc}.bin"
	if not pristine.is_file():
		raise SystemExit(f"Missing pristine: {pristine}")

	work_dir = WORK_ROOT / f"{against}-d{disc}"
	if work_dir.exists():
		shutil.rmtree(work_dir)
	work_dir.mkdir(parents=True)

	layer = None
	if against != "clean":
		assert csr_manifest is not None
		url = resolve_remote_layer_url(manifest_url, base_id, disc, csr_manifest)
		layer = load_layer(url)
		if layer.get("format") != "ic-layer-v1":
			raise SystemExit("base layer must be ic-layer-v1")

	base_bin = work_dir / "base.bin"
	make_base_image(pristine, layer, base_bin)
	patched_bin = patch_and_inject(base_bin, work_dir)

	print("=== diff -> fanfare-skip layer ===")
	out_dir = _ROOT / "builder" / pack_id / "layers"
	out_dir.mkdir(parents=True, exist_ok=True)
	out_path = out_dir / f"disc{disc}.layer.json"
	layer_id = f"{cfg['prefix_stem']}-disc{disc}-v{version}"
	description = f"Fanfare skip BATTLE.X — NTSC-U Disc {disc} (against {base_id})"
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
		raise SystemExit("Empty layer — patch/inject produced no disc changes")

	print("=== verify ===")
	check = bytearray(base_bin.read_bytes())
	apply_layer(check, built)
	if bytes(check) != patched_bin.read_bytes():
		raise SystemExit("VERIFY FAIL — layer apply does not match patched image")
	print("  OK")

	if not keep_work:
		shutil.rmtree(work_dir)
		print(f"  cleaned {work_dir}")

	return out_path, pack_id, display, blurb, cfg["compatible"], base_id


def main() -> int:
	ap = argparse.ArgumentParser(description="Build fanfare-skip builder packs")
	ap.add_argument("--against", default="clean", help="clean | csr | highwind | all")
	ap.add_argument("--discs", default="1,2,3")
	ap.add_argument("--version", default=None)
	ap.add_argument("--manifest-url", default=DEFAULT_CSR_MANIFEST)
	ap.add_argument("--keep-work", action="store_true")
	args = ap.parse_args()

	version = args.version or read_version()
	discs = parse_discs(args.discs)
	against_list = (
		["clean", "csr", "highwind"] if args.against == "all" else [args.against]
	)
	for a in against_list:
		if a not in AGAINST:
			raise SystemExit(f"Unknown --against {a}")

	csr_manifest = None
	if any(a != "clean" for a in against_list):
		csr_manifest = fetch_json(args.manifest_url)

	built: dict[str, dict] = {}
	for against in against_list:
		for disc in discs:
			print(f"\n######## {against} disc {disc} ########")
			_out, pack_id, display, blurb, compatible, base_id = build_one(
				against=against,
				disc=disc,
				version=version,
				manifest_url=args.manifest_url,
				csr_manifest=csr_manifest,
				keep_work=args.keep_work,
			)
			rec = built.setdefault(
				pack_id,
				{
					"display": display,
					"blurb": blurb,
					"compatible": compatible,
					"discs": [],
					"version": version,
				},
			)
			rec["discs"].append(disc)
			if against != "clean":
				rec["compatible"] = [base_id]

	for pack_id, rec in built.items():
		pack_dir = _ROOT / "builder" / pack_id
		write_pack_json(
			pack_dir,
			pack_id=pack_id,
			version=rec["version"],
			display=rec["display"],
			blurb=rec["blurb"],
			compatible=rec["compatible"],
			discs=sorted(set(rec["discs"])),
		)
		update_manifest(
			pack_id=pack_id,
			version=rec["version"],
			display=rec["display"],
			blurb=rec["blurb"],
			compatible=rec["compatible"],
			discs=sorted(set(rec["discs"])),
		)
		print(f"Updated pack + manifest: {pack_id}")

	print("\nAll done.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
