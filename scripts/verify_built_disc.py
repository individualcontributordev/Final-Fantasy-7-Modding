#!/usr/bin/env python3
"""Verify a builder-output disc using APPLIED.txt as the sole config source.

Like verify_builder_config, but the *subject* is the bootable .bin from a
builder zip (not pristine + layers only).

  python scripts/verify_built_disc.py path/to/built.bin
  python scripts/verify_built_disc.py path/to/builder-output-folder/

Requires APPLIED.txt next to the .bin (builder zip always ships it). Disc,
base, and add-ons are read only from that file and mapped to catalog pack ids
via local CSR + Modding manifests. No --disc / --base / --addon flags.

Checks:
  1) Parse APPLIED.txt → catalog ids (fail if Base/Add-on lines do not resolve)
  2) Every ic-layer record for that stack is present on the image
     (payload match; EDC/ECC + base bytes later addons overwrite are ignored)
  3) Optional: RCnt2 FORCE stubs in FIELD/WORLD when those addons are selected

Requires sibling Final-Fantasy-7-CSR (or --csr-root) for base layers + apply helpers.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
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


def _norm_name(s: str) -> str:
	"""Lowercase collapse for matching APPLIED display names to catalog."""
	s = s.lower().replace("—", "-").replace("–", "-")
	s = re.sub(r"\s+", " ", s).strip()
	return s


def _match_base_id(base_label: str, catalog: dict[str, dict]) -> str | None:
	low = base_label.lower()
	if "unmodified" in low or "retail" in low or low in ("clean", "none"):
		return "clean"
	bases = [(pid, meta) for pid, meta in catalog.items() if meta.get("kind") == "base"]
	bn = _norm_name(base_label)
	for pid, meta in bases:
		name = str(meta["entry"].get("name") or "")
		nn = _norm_name(name)
		if bn == nn or bn in nn or nn in bn:
			return pid
	for pid, meta in bases:
		if "highwind" in bn and "highwind" in pid:
			return pid
		if bn.startswith("csr") and pid.startswith("csr-v") and "highwind" not in bn:
			return pid
	return None


def _match_addon_id(label: str, catalog: dict[str, dict]) -> str | None:
	addons_cat = [
		(pid, meta) for pid, meta in catalog.items() if meta.get("kind") == "addon"
	]
	ln = _norm_name(label)
	for pid, meta in addons_cat:
		name = str(meta["entry"].get("name") or "")
		if _norm_name(name) == ln:
			return pid
	cands: list[tuple[int, str]] = []
	for pid, meta in addons_cat:
		name = str(meta["entry"].get("name") or "")
		nn = _norm_name(name)
		if not nn:
			continue
		if nn == ln or nn in ln or ln in nn:
			cands.append((len(nn), pid))
	if cands:
		cands.sort(reverse=True)
		return cands[0][1]
	return None


def _config_from_applied(
	applied_path: Path,
	catalog: dict[str, dict],
) -> tuple[int, str, list[str], str]:
	"""Parse APPLIED.txt only. Returns (disc, base_id, addon_ids, raw_text)."""
	if not applied_path.is_file():
		raise SystemExit(
			f"APPLIED.txt required next to the built image (not found: {applied_path})"
		)
	text = applied_path.read_text(encoding="utf-8", errors="replace")
	lines = text.splitlines()

	disc_m = re.search(r"(?im)^\s*Disc:\s*([123])\s*$", text)
	if not disc_m:
		raise SystemExit(f"{applied_path}: missing Disc: 1|2|3 line")
	disc = int(disc_m.group(1))

	base_m = re.search(r"(?im)^\s*Base:\s*(.+?)\s*$", text)
	if not base_m:
		raise SystemExit(f"{applied_path}: missing Base: line")
	base_label = base_m.group(1).strip()
	base_id = _match_base_id(base_label, catalog)
	if not base_id:
		raise SystemExit(
			f"{applied_path}: could not map Base {base_label!r} to a catalog pack id"
		)

	addon_labels: list[str] = []
	addons_none = False
	in_addons = False
	for line in lines:
		if re.match(r"(?i)^\s*Add-ons:\s*$", line):
			in_addons = True
			continue
		if re.match(r"(?i)^\s*Add-ons:\s*none\s*$", line):
			addons_none = True
			in_addons = False
			continue
		if in_addons:
			if re.match(r"(?i)^\s*EDC/ECC", line) or re.match(r"(?i)^\s*Play:", line):
				in_addons = False
				continue
			if not line.strip():
				if addon_labels:
					in_addons = False
				continue
			m = re.match(r"^\s*-\s+(.+?)\s*$", line)
			if m:
				addon_labels.append(m.group(1).strip())
			else:
				in_addons = False

	if not addons_none and not addon_labels:
		# No Add-ons section at all — treat as none only if file has no "Add-ons"
		if not re.search(r"(?im)^\s*Add-ons:", text):
			raise SystemExit(f"{applied_path}: missing Add-ons: section")
		# "Add-ons:" present but empty list
		addon_ids: list[str] = []
	elif addons_none:
		addon_ids = []
	else:
		addon_ids = []
		unmatched: list[str] = []
		for label in addon_labels:
			pid = _match_addon_id(label, catalog)
			if pid is None:
				unmatched.append(label)
			else:
				addon_ids.append(pid)
		if unmatched:
			raise SystemExit(
				f"{applied_path}: could not map Add-on line(s) to catalog ids: "
				+ "; ".join(repr(u) for u in unmatched)
			)

	return disc, base_id, addon_ids, text


def _print_applied(applied_path: Path, text: str, disc: int, base_id: str, addons: list[str]) -> None:
	print(f"=== APPLIED.txt ({applied_path}) ===")
	print(text.rstrip() or "(empty)")
	print()
	print(f"  resolved disc={disc}")
	print(f"  resolved base={base_id}")
	if addons:
		for a in addons:
			print(f"  resolved addon={a}")
	else:
		print("  resolved addons=(none)")
	print()


# Mode2/2352: user data ends before EDC at sector offset 2072 (builder repairs EDC/ECC after layers).
_SECTOR = 2352
_USER_END = 2072


def _user_payload_matches(image: bytes, off: int, data: bytes) -> int | None:
	"""Compare layer bytes that fall in sector user regions only.

	Returns first absolute mismatch offset, or None if all user bytes match.
	Bytes in EDC/ECC (sector_off >= 2072) are ignored — site builder rewrites those.
	"""
	for i, want in enumerate(data):
		abs_off = off + i
		if abs_off % _SECTOR >= _USER_END:
			continue
		if abs_off >= len(image) or image[abs_off] != want:
			return abs_off
	return None


def _layer_user_offsets(layer_path: Path) -> set[int]:
	"""Absolute offsets in sector user data touched by this layer."""
	layer = json.loads(layer_path.read_text(encoding="utf-8"))
	if layer.get("format") != "ic-layer-v1":
		raise SystemExit(f"{layer_path}: expected ic-layer-v1")
	out: set[int] = set()
	for rec in layer.get("records") or []:
		off = int(rec["offset"])
		data = bytes.fromhex(rec["hex"])
		for i in range(len(data)):
			abs_off = off + i
			if abs_off % _SECTOR < _USER_END:
				out.add(abs_off)
	return out


def _records_present(
	image: bytes,
	layer_path: Path,
	*,
	ignore_user_offsets: set[int] | None = None,
) -> tuple[int, int | None]:
	"""Return (record_count, first_user-payload mismatch offset or None).

	ignore_user_offsets: bytes later packs intentionally overwrite (base must not
	fail because field/world stubs stomped Highwind/CSR payload there).
	"""
	layer = json.loads(layer_path.read_text(encoding="utf-8"))
	if layer.get("format") != "ic-layer-v1":
		raise SystemExit(f"{layer_path}: expected ic-layer-v1")
	ignore = ignore_user_offsets or set()
	first = None
	n = 0
	for rec in layer.get("records") or []:
		n += 1
		off = int(rec["offset"])
		data = bytes.fromhex(rec["hex"])
		# Compare contiguous user-data runs, skipping EDC/ECC and later-addon spans.
		run_start = None
		run = bytearray()
		for i, want in enumerate(data):
			abs_off = off + i
			skip = abs_off % _SECTOR >= _USER_END or abs_off in ignore
			if skip:
				if run:
					bad = _user_payload_matches(image, run_start, bytes(run))
					if bad is not None and first is None:
						first = bad
					run = bytearray()
					run_start = None
				continue
			if run_start is None:
				run_start = abs_off
			run.append(want)
		if run:
			bad = _user_payload_matches(image, run_start, bytes(run))
			if bad is not None and first is None:
				first = bad
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
		description=(
			"Verify builder-output disc. Config comes only from APPLIED.txt "
			"next to the .bin (no --disc/--base/--addon)."
		)
	)
	ap.add_argument("path", type=Path, help="Built .bin or folder containing it (+ APPLIED.txt)")
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
	applied_path = bin_path.parent / "APPLIED.txt"

	disc, base_id, addons, applied_text = _config_from_applied(applied_path, catalog)

	print(f"Image: {bin_path} ({len(image)} bytes)")
	print(f"Config (from APPLIED.txt): base={base_id} addons={addons} disc={disc}")
	print()
	_print_applied(applied_path, applied_text, disc, base_id, addons)

	print("=== Layer records on image ===")
	failed = False
	stack_labels: list[str] = []

	need_base = "clean" if base_id in ("clean", "unmodified") else base_id

	# Later addons intentionally overwrite base bytes (e.g. FIELD.BIN stub on Highwind).
	# Collect addon user offsets first so base check can ignore those spans.
	addon_ignore: set[int] = set()
	addon_metas: list[tuple[str, dict, Path]] = []
	for addon_id in addons:
		if addon_id not in catalog:
			raise SystemExit(f"Unknown addon id {addon_id!r}")
		meta = catalog[addon_id]
		compat = meta["entry"].get("compatibleBases") or []
		if compat and need_base not in compat:
			print(f"  addon {addon_id}: compatibleBases={compat} excludes {need_base!r} — FAIL")
			failed = True
			continue
		lp = _layer_path(meta, disc)
		addon_metas.append((addon_id, meta, lp))
		addon_ignore |= _layer_user_offsets(lp)

	if base_id not in ("clean", "unmodified"):
		if base_id not in catalog:
			raise SystemExit(f"Unknown base id {base_id!r}")
		meta = catalog[base_id]
		lp = _layer_path(meta, disc)
		n, bad = _records_present(image, lp, ignore_user_offsets=addon_ignore)
		ok = bad is None
		extra = f" (ignored {len(addon_ignore)} addon-overwritten user bytes)" if addon_ignore else ""
		print(
			f"  base {base_id}: {n} records — "
			f"{'OK' if ok else f'MISSING payload @ {bad:#x}'}{extra if ok else ''}"
		)
		stack_labels.append(f"base:{base_id}")
		if not ok:
			failed = True
	else:
		print("  base clean: (no base layer)")
		stack_labels.append("base:clean")

	for addon_id, meta, lp in addon_metas:
		n, bad = _records_present(image, lp)
		ok = bad is None
		print(f"  addon {addon_id}: {n} records — {'OK' if ok else f'MISSING payload @ {bad:#x}'}")
		stack_labels.append(f"addon:{addon_id}")
		if not ok:
			failed = True

	want_field_stub = any("field-encounter" in a for a in addons)
	want_world_stub = any("world-encounter" in a for a in addons)
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

	print()
	print("Stack checked:", ", ".join(stack_labels))
	if failed:
		print("FAIL — built disc does not match APPLIED.txt stack")
		return 1
	print("PASS — built disc matches APPLIED.txt stack (layer payloads present)")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
