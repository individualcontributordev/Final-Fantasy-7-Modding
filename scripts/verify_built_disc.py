#!/usr/bin/env python3
"""Verify a builder-output disc against a specific base+addon configuration.

Like verify_builder_config, but the *subject* is the bootable .bin from a
builder zip (not pristine + layers only).

  # Prefer: let the script read zip folder name + APPLIED.txt
  python scripts/verify_built_disc.py path/to/built.bin
  python scripts/verify_built_disc.py path/to/builder-output-folder/

  # Optional overrides (must match the zip if given):
  python scripts/verify_built_disc.py path/to/built.bin \
    --disc 1 --base clean \
    --addon field-encounter-25-v0.1.2 \
    --addon world-encounter-25-v0.1.0

Config is inferred from (first hit wins per field, CLI always wins):
  1) --disc / --base / --addon flags
  2) Builder output name: ff7-builder-d1+baseId+addonId+...
  3) APPLIED.txt next to the .bin (Disc / Base / Add-ons display names → catalog ids)

Checks:
  1) APPLIED.txt (if present) mentions expected pack names/ids
  2) Every ic-layer record for the selected base+addons is present on the image
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


_BUILDER_STAMP_RE = re.compile(
	r"(?:^|[/\\])ff7-builder-(?:d(?P<disc>[123])\+)?(?P<body>[^/\\]+?)(?:\.(?:bin|cue|zip))?$",
	re.IGNORECASE,
)


def _parse_builder_stamp(name: str, catalog: dict[str, dict]) -> dict:
	"""Parse ff7-builder-dN+base+addon… into disc/base/addons using catalog ids."""
	m = _BUILDER_STAMP_RE.search(name.replace("\\", "/"))
	if not m:
		return {}
	out: dict = {}
	if m.group("disc"):
		out["disc"] = int(m.group("disc"))
	parts = [p for p in m.group("body").split("+") if p]
	if not parts:
		return out
	# First segment is base (clean | csr-v… | highwind-v…); rest are addons.
	base = parts[0]
	if base in ("clean", "unmodified") or base in catalog:
		out["base"] = "clean" if base == "unmodified" else base
		addons = parts[1:]
	else:
		# Unusual stamp without known base — treat all known addon ids only.
		addons = parts
	known = [a for a in addons if a in catalog]
	unknown = [a for a in addons if a not in catalog]
	if unknown:
		print(
			f"Note: stamp has unknown pack id(s) (not in local manifests): {unknown}",
			file=sys.stderr,
		)
	if known:
		out["addons"] = known
	return out


def _norm_name(s: str) -> str:
	"""Lowercase collapse for matching APPLIED display names to catalog."""
	s = s.lower().replace("—", "-").replace("–", "-")
	s = re.sub(r"\s+", " ", s).strip()
	return s


def _parse_applied_text(text: str, catalog: dict[str, dict]) -> dict:
	"""Map APPLIED.txt display lines to catalog pack ids."""
	out: dict = {}
	lines = text.splitlines()
	disc_m = re.search(r"(?im)^\s*Disc:\s*([123])\s*$", text)
	if disc_m:
		out["disc"] = int(disc_m.group(1))

	base_m = re.search(r"(?im)^\s*Base:\s*(.+?)\s*$", text)
	if base_m:
		base_label = base_m.group(1).strip()
		low = base_label.lower()
		if "unmodified" in low or "retail" in low or low in ("clean", "none"):
			out["base"] = "clean"
		else:
			# Prefer exact/near name match against base catalog entries.
			bases = [
				(pid, meta)
				for pid, meta in catalog.items()
				if meta.get("kind") == "base"
			]
			bn = _norm_name(base_label)
			picked = None
			for pid, meta in bases:
				name = str(meta["entry"].get("name") or "")
				nn = _norm_name(name)
				if bn == nn or bn in nn or nn in bn:
					picked = pid
					break
				if "highwind" in bn and "highwind" in pid:
					picked = pid
					break
				if bn.startswith("csr") and pid.startswith("csr-v") and "highwind" not in bn:
					picked = pid
					break
			if picked:
				out["base"] = picked

	# Collect "- Name" lines under Add-ons:
	addon_labels: list[str] = []
	in_addons = False
	for line in lines:
		if re.match(r"(?i)^\s*Add-ons:\s*$", line):
			in_addons = True
			continue
		if re.match(r"(?i)^\s*Add-ons:\s*none\s*$", line):
			out["addons"] = []
			in_addons = False
			continue
		if in_addons:
			if re.match(r"(?i)^\s*EDC/ECC", line) or re.match(r"(?i)^\s*Play:", line):
				in_addons = False
				continue
			if not line.strip():
				# blank after list ends section
				if addon_labels:
					in_addons = False
				continue
			m = re.match(r"^\s*-\s+(.+?)\s*$", line)
			if m:
				addon_labels.append(m.group(1).strip())
			else:
				in_addons = False

	if addon_labels:
		addons_cat = [
			(pid, meta)
			for pid, meta in catalog.items()
			if meta.get("kind") == "addon"
		]
		resolved: list[str] = []
		for label in addon_labels:
			ln = _norm_name(label)
			best = None
			# Exact normalized name match first.
			for pid, meta in addons_cat:
				name = str(meta["entry"].get("name") or "")
				if _norm_name(name) == ln:
					best = pid
					break
			if best is None:
				# Longest catalog name contained in label or vice versa.
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
					best = cands[0][1]
			if best is None:
				print(
					f"Note: APPLIED add-on line not matched to catalog: {label!r}",
					file=sys.stderr,
				)
			else:
				resolved.append(best)
		if resolved:
			out["addons"] = resolved
	return out


def _infer_config(
	bin_path: Path,
	catalog: dict[str, dict],
	*,
	cli_disc: int | None,
	cli_base: str | None,
	cli_addons: list[str] | None,
) -> tuple[int, str, list[str], list[str]]:
	"""Resolve disc/base/addons. Returns (disc, base, addons, sources)."""
	sources: list[str] = []
	stamp = _parse_builder_stamp(bin_path.name, catalog)
	if not stamp.get("addons") and not stamp.get("base"):
		# Also try parent folder (zip extract dir often named like the bin).
		stamp = {**_parse_builder_stamp(bin_path.parent.name, catalog), **stamp}

	applied_path = bin_path.parent / "APPLIED.txt"
	applied: dict = {}
	if applied_path.is_file():
		applied = _parse_applied_text(
			applied_path.read_text(encoding="utf-8", errors="replace"),
			catalog,
		)

	# Disc
	disc = cli_disc
	if disc is not None:
		sources.append("disc:cli")
	elif stamp.get("disc") is not None:
		disc = int(stamp["disc"])
		sources.append("disc:stamp")
	elif applied.get("disc") is not None:
		disc = int(applied["disc"])
		sources.append("disc:APPLIED")
	else:
		raise SystemExit(
			"Could not infer --disc (pass --disc 1|2|3, or use ff7-builder-dN+… name / APPLIED.txt)"
		)

	# Base
	base = (cli_base or "").strip() or None
	if base:
		sources.append("base:cli")
	elif stamp.get("base"):
		base = str(stamp["base"])
		sources.append("base:stamp")
	elif applied.get("base"):
		base = str(applied["base"])
		sources.append("base:APPLIED")
	else:
		raise SystemExit(
			"Could not infer --base (pass --base, or use builder stamp name / APPLIED.txt)"
		)

	# Addons: CLI wins entirely if any --addon given; else stamp; else APPLIED.
	if cli_addons:
		addons = list(cli_addons)
		sources.append("addons:cli")
	elif stamp.get("addons") is not None:
		addons = list(stamp["addons"])
		sources.append("addons:stamp")
	elif applied.get("addons") is not None:
		addons = list(applied["addons"])
		sources.append("addons:APPLIED")
	else:
		addons = []
		sources.append("addons:(none)")

	# If stamp and APPLIED both had addons and CLI did not, prefer stamp (exact ids)
	# but warn when APPLIED resolved a different set.
	if (
		not cli_addons
		and stamp.get("addons") is not None
		and applied.get("addons") is not None
		and list(stamp["addons"]) != list(applied["addons"])
	):
		print(
			"Note: stamp addons differ from APPLIED-resolved ids; using stamp "
			f"(stamp={stamp['addons']}, APPLIED={applied['addons']})",
			file=sys.stderr,
		)

	return disc, base, addons, sources


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
			"Verify builder-output disc matches a base+addon config. "
			"Disc/base/addons are inferred from the .bin name and APPLIED.txt when flags are omitted."
		)
	)
	ap.add_argument("path", type=Path, help="Built .bin or folder containing it")
	ap.add_argument(
		"--disc",
		type=int,
		default=None,
		choices=(1, 2, 3),
		help="Disc number (optional if stamp/APPLIED has it)",
	)
	ap.add_argument(
		"--base",
		default=None,
		help="Base id: clean | csr-v… | highwind-v… (optional if stamp/APPLIED has it)",
	)
	ap.add_argument(
		"--addon",
		action="append",
		default=None,
		dest="addons",
		help="Addon id (repeatable). If omitted, inferred from stamp then APPLIED.txt",
	)
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

	disc, base_id, addons, sources = _infer_config(
		bin_path,
		catalog,
		cli_disc=args.disc,
		cli_base=args.base,
		cli_addons=args.addons,
	)

	print(f"Image: {bin_path} ({len(image)} bytes)")
	print(f"Config: base={base_id} addons={addons} disc={disc}")
	print(f"Inferred from: {', '.join(sources)}")
	print()

	expected_ids = [base_id, *addons]
	applied = bin_path.parent / "APPLIED.txt"
	applied_missing: list[str] = []
	if applied.is_file():
		applied_missing = _print_applied(applied, expected_ids)
	else:
		print("=== APPLIED.txt ===\n(not found next to image)\n")

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
