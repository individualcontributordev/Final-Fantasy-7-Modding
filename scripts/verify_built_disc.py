#!/usr/bin/env python3
"""Verify a builder-output disc against a specific base+addon configuration.

Like verify_builder_config, but the *subject* is the bootable .bin from a
builder zip (not pristine + layers only).

  python scripts/verify_built_disc.py path/to/built.bin \
    --disc 1 --base clean \
    --addon field-encounter-25-v0.1.2 \
    --addon world-encounter-25-v0.1.0

Checks:
  1) APPLIED.txt (if present) mentions expected pack names/ids
  2) Every ic-layer record for the selected base+addons is present on the image
     (payload match; EDC footers may differ after builder repair)
  3) Optional: RCnt2 FORCE stubs in FIELD/WORLD when those addons are selected

Requires sibling Final-Fantasy-7-CSR (or --csr-root) for base layers + apply helpers.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
_MODDING = _SCRIPTS.parent
_DEFAULT_CSR = _MODDING.parent / "Final-Fantasy-7-CSR"

GZIPPS_HEADER_SIZE = 8
RCNT2_STUB_PREFIX = bytes.fromhex("801f013c2011228c")
FIELD_STUB_OFF = 0xBB7C
WORLD_STUB_OFF = 0x17DB4


def _setup_csr(csr_root: Path) -> None:
	csr_scripts = csr_root / "scripts"
	if not (csr_scripts / "apply_layer.py").is_file():
		raise SystemExit(f"CSR scripts not found under {csr_root}")
	sys.path.insert(0, str(csr_scripts))
	sys.path.insert(0, str(_SCRIPTS))


def _load_manifest(path: Path) -> tuple[Path, dict]:
	path = path.expanduser().resolve()
	return path.parent, json.loads(path.read_text(encoding="utf-8"))


def _index_packs(builder_dir: Path, data: dict) -> dict[str, dict]:
	out: dict[str, dict] = {}
	for key in ("bases", "addons"):
		for entry in data.get(key) or []:
			pid = entry.get("id")
			if pid:
				out[str(pid)] = {"entry": entry, "builder_dir": builder_dir, "kind": key[:-1]}
	return out


def _layer_path(meta: dict, disc: int) -> Path:
	discs = meta["entry"].get("discs") or {}
	rel = discs.get(str(disc)) or discs.get(disc)
	if not rel:
		raise SystemExit(f"{meta['entry'].get('id')}: no layer for disc {disc}")
	return (meta["builder_dir"] / str(rel).lstrip("./")).resolve()


def _resolve_bin(path: Path) -> Path:
	path = path.expanduser().resolve()
	if path.is_file() and path.suffix.lower() == ".bin":
		return path
	if path.is_dir():
		bins = sorted(path.glob("*.bin")) + sorted(path.glob("*.BIN"))
		if not bins:
			raise SystemExit(f"No .bin in directory: {path}")
		if len(bins) > 1:
			print(f"Note: multiple .bin files; using {bins[0].name}", file=sys.stderr)
		return bins[0]
	raise SystemExit(f"Not a .bin or directory: {path}")


def _applied_mentions(pid: str, low: str) -> bool:
	"""APPLIED.txt uses display names; match ids + common builder wording."""
	token = pid.lower()
	stem = token.rsplit("-v", 1)[0]
	if token in low or stem in low:
		return True
	if pid in ("clean", "unmodified"):
		return "unmodified" in low or "clean" in low or "retail" in low
	if "highwind" in token:
		return "highwind" in low
	if token.startswith("csr-v") or stem == "csr":
		return "csr" in low and "csr+" not in low.replace("csr+ scene", "")
	if "csr-plus-scene" in token or "csr-plus" in token:
		return "csr+" in low or "csr+ scene" in low or stem.replace("csr-plus-scene-", "") in low
	# field-encounter-25 / field-encounter-on-csr-25 / ...
	if "field-encounter" in token:
		if "field" not in low or "encounter" not in low:
			return False
		if "-25" in token or token.endswith("25"):
			return "light" in low or "25%" in low or "25" in low
		if "-50" in token:
			return "standard" in low or "50%" in low
		if "-75" in token:
			return "dense" in low or "75%" in low
		return True
	if "world-encounter" in token:
		if "world" not in low or "encounter" not in low:
			return False
		if "-25" in token or token.endswith("25"):
			return "light" in low or "25%" in low or "25" in low
		if "-50" in token:
			return "standard" in low or "50%" in low
		if "-75" in token:
			return "dense" in low or "75%" in low
		return True
	return False


def _print_applied(applied: Path, expected_ids: list[str]) -> list[str]:
	print(f"=== APPLIED.txt ({applied}) ===")
	text = applied.read_text(encoding="utf-8", errors="replace")
	print(text.rstrip() or "(empty)")
	print()
	low = text.lower()
	missing = []
	for pid in expected_ids:
		ok = _applied_mentions(pid, low)
		print(f"  expect mention of {pid!r}: {'yes' if ok else 'NO'}")
		if not ok:
			missing.append(pid)
	print()
	return missing


def _records_present(image: bytes, layer_path: Path) -> tuple[int, int | None]:
	"""Return (record_count, first_mismatch_offset or None)."""
	layer = json.loads(layer_path.read_text(encoding="utf-8"))
	if layer.get("format") != "ic-layer-v1":
		raise SystemExit(f"{layer_path}: expected ic-layer-v1")
	first = None
	n = 0
	for rec in layer.get("records") or []:
		n += 1
		off = int(rec["offset"])
		data = bytes.fromhex(rec["hex"])
		got = image[off : off + len(data)]
		if got != data:
			if first is None:
				first = off
	return n, first


def _decompress_gzipps(blob: bytes) -> bytes:
	if len(blob) <= GZIPPS_HEADER_SIZE:
		raise ValueError("file too small for GZIPPS")
	return gzip.decompress(blob[GZIPPS_HEADER_SIZE:])


def _stub_check(image: bytes, iso_path: str, stub_off: int) -> str:
	from psx_mode2_iso import extract_file  # noqa: WPS433

	blob = extract_file(image, iso_path)
	dec = _decompress_gzipps(blob)
	ok = dec[stub_off : stub_off + len(RCNT2_STUB_PREFIX)] == RCNT2_STUB_PREFIX
	return f"{iso_path}: stub@{stub_off:#x}={'YES' if ok else 'NO'}"


def main() -> int:
	ap = argparse.ArgumentParser(
		description="Verify builder-output disc matches a base+addon config"
	)
	ap.add_argument("path", type=Path, help="Built .bin or folder containing it")
	ap.add_argument("--disc", type=int, required=True, choices=(1, 2, 3))
	ap.add_argument("--base", required=True, help="Base id: clean | csr-v… | highwind-v…")
	ap.add_argument("--addon", action="append", default=[], dest="addons")
	ap.add_argument(
		"--csr-root",
		type=Path,
		default=_DEFAULT_CSR,
		help=f"Final-Fantasy-7-CSR root (default: {_DEFAULT_CSR})",
	)
	ap.add_argument(
		"--skip-stub-check",
		action="store_true",
		help="Skip FIELD/WORLD RCnt2 stub probes",
	)
	ap.add_argument(
		"--allow-applied-gap",
		action="store_true",
		help="Do not fail if APPLIED.txt lacks an expected id string",
	)
	args = ap.parse_args()

	csr_root = args.csr_root.expanduser().resolve()
	_setup_csr(csr_root)

	catalog: dict[str, dict] = {}
	for man in (
		csr_root / "builder" / "manifest.json",
		_MODDING / "builder" / "manifest.json",
	):
		if not man.is_file():
			raise SystemExit(f"Missing manifest: {man}")
		bdir, data = _load_manifest(man)
		catalog.update(_index_packs(bdir, data))

	bin_path = _resolve_bin(args.path)
	image = bin_path.read_bytes()
	print(f"Image: {bin_path} ({len(image)} bytes)")
	print(f"Config: base={args.base} addons={args.addons} disc={args.disc}")
	print()

	expected_ids = [args.base, *args.addons]
	applied = bin_path.parent / "APPLIED.txt"
	applied_missing: list[str] = []
	if applied.is_file():
		applied_missing = _print_applied(applied, expected_ids)
	else:
		print("=== APPLIED.txt ===\n(not found next to image)\n")

	print("=== Layer records on image ===")
	failed = False
	stack_labels: list[str] = []

	base_id = args.base.strip()
	if base_id not in ("clean", "unmodified"):
		if base_id not in catalog:
			raise SystemExit(f"Unknown base id {base_id!r}")
		meta = catalog[base_id]
		lp = _layer_path(meta, args.disc)
		n, bad = _records_present(image, lp)
		ok = bad is None
		print(f"  base {base_id}: {n} records — {'OK' if ok else f'MISSING payload @ {bad:#x}'}")
		stack_labels.append(f"base:{base_id}")
		if not ok:
			failed = True
	else:
		print("  base clean: (no base layer)")
		stack_labels.append("base:clean")

	need_base = "clean" if base_id in ("clean", "unmodified") else base_id
	for addon_id in args.addons:
		if addon_id not in catalog:
			raise SystemExit(f"Unknown addon id {addon_id!r}")
		meta = catalog[addon_id]
		compat = meta["entry"].get("compatibleBases") or []
		if compat and need_base not in compat:
			print(f"  addon {addon_id}: compatibleBases={compat} excludes {need_base!r} — FAIL")
			failed = True
			continue
		lp = _layer_path(meta, args.disc)
		n, bad = _records_present(image, lp)
		ok = bad is None
		print(f"  addon {addon_id}: {n} records — {'OK' if ok else f'MISSING payload @ {bad:#x}'}")
		stack_labels.append(f"addon:{addon_id}")
		if not ok:
			failed = True

	want_field_stub = any("field-encounter" in a for a in args.addons)
	want_world_stub = any("world-encounter" in a for a in args.addons)
	if not args.skip_stub_check and (want_field_stub or want_world_stub):
		print()
		print("=== Engine stubs (when encounter addons selected) ===")
		try:
			if want_field_stub:
				line = _stub_check(image, "FIELD/FIELD.BIN", FIELD_STUB_OFF)
				print(f"  {line}")
				if line.endswith("=NO"):
					failed = True
			if want_world_stub:
				line = _stub_check(image, "WORLD/WORLD.BIN", WORLD_STUB_OFF)
				print(f"  {line}")
				if line.endswith("=NO"):
					failed = True
		except Exception as exc:
			print(f"  stub check ERROR: {exc}", file=sys.stderr)
			failed = True

	if applied_missing and not args.allow_applied_gap:
		print()
		print(f"APPLIED.txt missing expected ids: {applied_missing}")
		failed = True

	print()
	print("Stack checked:", ", ".join(stack_labels))
	if failed:
		print("FAIL — built disc does not match this builder config")
		return 1
	print("PASS — built disc matches base+addon config (layer payloads present)")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
