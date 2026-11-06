#!/usr/bin/env python3
"""Let Cloud equip the Masamune weapon (item 0xFF) and wield Sephiroth's sword model.

KERNEL.BIN is 27 concatenated sections: 6-byte header (u16 gzip size, u16 raw
size, u16 type) + gzip member. Section 5 is weapon data, 44 bytes a record; the
u16 at +0x0E is the equip mask (bit 0 Cloud, bit 10 Sephiroth). Masamune is the
last record (127) with mask 0x0400. We add Cloud's bit and rewrite the section
in its original slot, zero-padded, so no later section or ISO size moves.

Battle models (ENEMY6/<name>.LZS) are an offset table of sections: body, animations, one
texture, then 16 self-contained weapon meshes (weapon record +0x09 picks one). SEFIROS.LZS ends
in 16 copies of the Masamune mesh. The model id is only the low nibble of +0x09 (high nibble is
another field), so there is no 17th slot: we overwrite Cloud's Murasame mesh in CLOUD and HICLOUD
with the Masamune and point the Masamune record at that slot. Section count is unchanged; the
file stays within its ISO sectors.
The field script FIELD/BLIN70_1.DAT gives the Masamune (STITM item 255): the scripts and messages
the Makou edit changes (field_edit.json, made by capture_edit.py) are merged into whichever variant of the script the base has, then recompressed to fit the original slot, so FIELD.BIN's table and the
directory entry stay untouched.
Sector EDC/ECC is not recomputed; run repair_mode2_edc afterwards."""

from __future__ import annotations

import gzip
import importlib.util
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from compress_gzipps import _best_gzip_payload, _original_gzip_header10  # noqa: E402
from psx_mode2_iso import extract_file, replace_file_padded, replace_file_within_sectors  # noqa: E402

_spec = importlib.util.spec_from_file_location(
	"lzs_pack", Path(__file__).resolve().parents[2] / "diamond-weapon-speed-up" / "scripts" / "lzs_pack.py"
)
lzs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lzs)

KERNEL = "/INIT/KERNEL.BIN"
WEAPON_SECTION = 5
RECORD = 44
MASAMUNE = 127
MASK_OFF = 0x0E
MODEL_OFF = 0x09
SEPHIROTH, CLOUD = 0x0400, 0x0001
WEAPONS = 16  # weapon meshes at the end of a party battle model
SLOT = 9  # Cloud's Murasame mesh is replaced by the Masamune
SEPH_MODEL = "ENEMY6/SEFIROS.LZS"
CLOUD_MODELS = ("ENEMY6/CLOUD.LZS", "ENEMY6/HICLOUD.LZS")
FIELD = "/FIELD/BLIN70_1.DAT"
EDIT = Path(__file__).resolve().parents[1] / "field_edit.json"  # written by capture_edit.py


def sections(dec: bytes) -> list[bytes]:
	n = struct.unpack_from("<I", dec, 0)[0]
	offs = list(struct.unpack_from(f"<{n}I", dec, 4)) + [len(dec)]
	return [dec[offs[i] : offs[i + 1]] for i in range(n)]


def join(secs: list[bytes]) -> bytes:
	offs, pos = [], 4 * (len(secs) + 1)
	for s in secs:
		offs.append(pos)
		pos += len(s)
	return struct.pack(f"<{len(secs) + 1}I", len(secs), *offs) + b"".join(secs)


def swap_masamune_mesh(cloud: bytes, mesh: bytes) -> bytes | None:
	"""Cloud model with weapon SLOT replaced by `mesh`, or None when already done."""
	secs = sections(cloud)
	if len(secs) < WEAPONS + 1:
		raise SystemExit(f"battle model has only {len(secs)} sections")
	i = len(secs) - WEAPONS + SLOT
	if secs[i] == mesh:
		return None
	secs[i] = mesh
	return join(secs)


def patch_kernel(kernel: bytes) -> bytes | None:
	"""Return the patched KERNEL.BIN, or None when Cloud can already equip it."""
	off = 0
	for _ in range(WEAPON_SECTION):
		off += 6 + struct.unpack_from("<H", kernel, off)[0]
	size, raw_size, _typ = struct.unpack_from("<HHH", kernel, off)
	payload = kernel[off + 6 : off + 6 + size]
	weapons = bytearray(gzip.decompress(payload))
	if len(weapons) != raw_size or len(weapons) != 128 * RECORD:
		raise SystemExit(f"weapon section is {len(weapons)} bytes, expected {128 * RECORD}")

	pos = MASAMUNE * RECORD + MASK_OFF
	mask = struct.unpack_from("<H", weapons, pos)[0]
	if mask & CLOUD:
		return None
	if mask != SEPHIROTH:
		raise SystemExit(f"Masamune equip mask is 0x{mask:04X}, expected 0x{SEPHIROTH:04X}")
	struct.pack_into("<H", weapons, pos, mask | CLOUD)
	m = MASAMUNE * RECORD + MODEL_OFF
	weapons[m] = weapons[m] & 0xF0 | SLOT  # keep the high nibble

	new, label = _best_gzip_payload(bytes(weapons), size, _original_gzip_header10(payload))
	if len(new) > size:
		raise SystemExit(f"recompressed weapon section ({len(new)}) exceeds its slot ({size})")
	print(f"  weapon section: {len(new)}/{size} bytes ({label})")
	# trailing zeros after the gzip trailer keep the header size and later sections in place
	return kernel[: off + 6] + new.ljust(size, b"\0") + kernel[off + 6 + size :]


def _s0(dec: bytes) -> tuple[tuple[int, ...], bytearray, bytes]:
	"""Field script split into (7 section pointers, section 0, the other sections)."""
	h = struct.unpack_from("<7I", dec, 0)
	end = 0x1C + h[1] - h[0]
	return h, bytearray(dec[0x1C:end]), dec[end:]


def _layout(d) -> tuple[int, int, int, int]:
	"""Entity count, AKAO count, script-position table offset, posTexts of a section 0."""
	ns, (ptexts, nakao) = d[2], struct.unpack_from("<HH", d, 4)
	return ns, nakao, 32 + 8 * ns + 4 * nakao, ptexts


def _entity(d, ent: int) -> tuple[int, int, list[int]]:
	"""(start, end, 32 slot pointers relative to start) of an entity's scripts."""
	ns, _, tab, ptexts = _layout(d)
	pos = lambda e, s: struct.unpack_from("<H", d, tab + 64 * e + 2 * s)[0]
	a = pos(ent, 0)
	return a, pos(ent + 1, 0) if ent + 1 < ns else ptexts, [pos(ent, s) - a for s in range(32)]


def _set_entity(d: bytearray, ent: int, block: bytes, slots: list[int]) -> None:
	a, b, _ = _entity(d, ent)
	delta = len(block) - (b - a)
	ns, _, tab, ptexts = _layout(d)
	for i in range(tab, tab + 64 * ns, 2):
		v = struct.unpack_from("<H", d, i)[0]
		if v >= b:
			struct.pack_into("<H", d, i, v + delta)
	struct.pack_into("<H", d, 4, ptexts + delta)
	for i in range(32 + 8 * ns, tab, 4):
		struct.pack_into("<I", d, i, struct.unpack_from("<I", d, i)[0] + delta)
	d[a:b] = block
	for s, r in enumerate(slots):
		struct.pack_into("<H", d, tab + 64 * ent + 2 * s, a + r)


def _texts(d) -> list[bytes]:
	ns, nakao, _, ptexts = _layout(d)
	end = struct.unpack_from("<I", d, 32 + 8 * ns)[0] if nakao else len(d)
	n = struct.unpack_from("<H", d, ptexts)[0]
	offs = list(struct.unpack_from(f"<{n}H", d, ptexts + 2)) + [end - ptexts]
	return [bytes(d[ptexts + offs[i] : ptexts + offs[i + 1]]) for i in range(n)]


def _set_texts(d: bytearray, texts: list[bytes]) -> None:
	ns, nakao, tab, ptexts = _layout(d)
	end = struct.unpack_from("<I", d, 32 + 8 * ns)[0] if nakao else len(d)
	offs, pos = [], 2 + 2 * len(texts)
	for t in texts:
		offs.append(pos)
		pos += len(t)
	new = struct.pack(f"<{len(texts) + 1}H", len(texts), *offs) + b"".join(texts)
	for i in range(32 + 8 * ns, tab, 4):
		struct.pack_into("<I", d, i, struct.unpack_from("<I", d, i)[0] + len(new) - (end - ptexts))
	d[ptexts:end] = new


def capture_edit(base: bytes, edited: bytes) -> dict:
	"""The Makou edit as data: every entity whose scripts changed and every message changed or added,
	diffed `base` (an unedited BLIN70_1 script) -> `edited`. Refuses what apply_edit cannot reproduce exactly."""
	_, db, _ = _s0(base)
	_, de, _ = _s0(edited)
	if _layout(db)[0] != _layout(de)[0]:
		raise SystemExit("the edit changes the entity count; not supported")
	ents = []
	for e in range(_layout(db)[0]):
		(a, b, sb), (c, f, se) = _entity(db, e), _entity(de, e)
		if (bytes(db[a:b]), sb) != (bytes(de[c:f]), se):
			ents.append(dict(entity=e, old=bytes(db[a:b]).hex(), old_slots=sb, new=bytes(de[c:f]).hex(), new_slots=se))
	tb, te = _texts(db), _texts(de)
	if len(te) < len(tb):
		raise SystemExit("the edit removes messages; not supported")
	edit = dict(
		entities=ents,
		old_messages=len(tb),
		messages_set=[[i, tb[i].hex(), te[i].hex()] for i in range(len(tb)) if tb[i] != te[i]],
		messages_added=[t.hex() for t in te[len(tb) :]],
	)
	if apply_edit(base, edit) != edited:
		raise SystemExit("the edit changes something besides entity scripts and messages; not supported")
	return edit


def apply_edit(old: bytes, edit: dict) -> bytes | None:
	"""`old` (any base's BLIN70_1 script) with the captured edit applied, so base changes elsewhere in the
	script are kept; None when it is already applied. Fails loudly when a touched entity or the message
	count differs from what the edit was captured against."""
	h, d, rest = _s0(old)
	changed = False
	for c in edit["entities"]:
		a, b, slots = _entity(d, c["entity"])
		now = (bytes(d[a:b]).hex(), slots)
		if now == (c["new"], c["new_slots"]):
			continue
		if now != (c["old"], c["old_slots"]):
			raise SystemExit(f"{FIELD}: entity {c['entity']} differs from the version the field edit was captured on; re-run capture_edit.py")
		_set_entity(d, c["entity"], bytes.fromhex(c["new"]), c["new_slots"])
		changed = True
	texts, n = _texts(d), edit["old_messages"]
	added = [bytes.fromhex(t) for t in edit["messages_added"]]
	if len(texts) == n + len(added) and texts[n:] == added and all(texts[i].hex() == new for i, _, new in edit["messages_set"]):
		pass
	elif len(texts) == n and all(texts[i].hex() == old for i, old, _ in edit["messages_set"]):
		for i, _, new in edit["messages_set"]:
			texts[i] = bytes.fromhex(new)
		_set_texts(d, texts + added)
		changed = True
	else:
		raise SystemExit(f"{FIELD}: messages differ from the version the field edit was captured on; re-run capture_edit.py")
	if not changed:
		return None
	delta = len(d) - (h[1] - h[0])
	h = h[:1] + tuple(p + delta for p in h[1:])
	return struct.pack("<7I", *h) + bytes(d) + rest


def patch_field(img: bytearray) -> int:
	"""Apply the field edit to the field script; returns 1 if changed."""
	new = apply_edit(lzs.decompress(extract_file(img, FIELD)), json.loads(EDIT.read_text(encoding="utf-8")))
	if new is None:
		return 0
	replace_file_padded(img, FIELD, lzs.compress(new))
	return 1


def apply_patch(img: bytearray) -> int:
	"""Patch img in place; returns the number of patches applied (0 if already patched)."""
	return patch_equip(img) + patch_field(img)


def patch_equip(img: bytearray) -> int:
	kernel = extract_file(img, KERNEL)
	patched = patch_kernel(kernel)
	if patched is None:
		return 0
	mesh = sections(lzs.decompress(extract_file(img, SEPH_MODEL)))[-WEAPONS]
	for path in CLOUD_MODELS:
		new = swap_masamune_mesh(lzs.decompress(extract_file(img, path)), mesh)
		if new is None:
			raise SystemExit(f"{path}: mesh already swapped but KERNEL is not patched")
		replace_file_within_sectors(img, path, lzs.compress(new))
	replace_file_padded(img, KERNEL, patched)
	return 1


def main() -> None:
	if len(sys.argv) != 2:
		raise SystemExit("usage: apply_masamune.py <disc.bin>")
	path = Path(sys.argv[1])
	img = bytearray(path.read_bytes())
	n = apply_patch(img)
	path.write_bytes(img)
	print(f"{'Patched' if n else 'Already patched'} {path}; now run repair_mode2_edc.py")


if __name__ == "__main__":
	main()
