#!/usr/bin/env python3
"""Recolor the nine main party members' outfits.

Field (FIELD/<name>.BCX, LZS, no textures): every polygon carries its own RGBA, so walk the
part headers and remap exact RGB matches.
Battle (ENEMY6/<name>.LZS): vertex colors are shaded, so rotate the hue of every
color inside the outfit's hue band, keeping saturation and value. Cloud instead scales his
cool colors toward crimson.
World map (WORLD/WM0-3.BSZ): the same field-style models, patched by exact 4-aligned RGB match.
Field/world hair is a flat color too, so it is remapped; battle heads are textured, so battle hair, skin, metal
and faces are left alone."""

from __future__ import annotations

import colorsys
import importlib.util
import struct
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))
from psx_mode2_iso import extract_file, replace_file_padded  # noqa: E402

_spec = importlib.util.spec_from_file_location(
	"lzs_pack", _ROOT / "mods" / "diamond-weapon-speed-up" / "scripts" / "lzs_pack.py"
)
lzs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lzs)


HDR_SIZE = 36  # BcxModelHeader
PART_HDR = struct.Struct("<14B5HII")
# (count index in part header, record size, [(color offset, colors per record)]), file order
KINDS = (
	(4, 24, ((4, 4),)),  # textured quad, gouraud
	(5, 20, ((4, 3),)),  # textured tri, gouraud
	(6, 12, ((4, 1),)),  # textured quad, flat
	(7, 12, ((4, 1),)),  # textured tri, flat
	(8, 8, ((4, 1),)),  # flat tri
	(9, 8, ((4, 1),)),  # flat quad
	(10, 16, ((4, 3),)),  # gouraud tri
	(11, 20, ((4, 4),)),  # gouraud quad
)

def color_offsets(dec: bytes):
	"""(bone, absolute offset) of every polygon RGB triple in the decompressed BCX."""
	om = struct.unpack_from("<I", dec, 4)[0]
	num_bones, num_parts = dec[om + 2], dec[om + 3]
	first = om + HDR_SIZE + num_bones * 4
	for i in range(num_parts):
		h = PART_HDR.unpack_from(dec, first + i * 32)
		pos = (h[19] & 0x7FFFFFFF) + h[14]
		for count_idx, size, cols in KINDS:
			for _ in range(h[count_idx]):
				for off, n in cols:
					for k in range(n):
						yield h[1], pos + off + k * 4
				pos += size


def recolor(dec: bytes, color_map: dict, only: dict | None = None) -> tuple[bytes, int]:
	"""`only` limits a source color to the given bones (for colors shared between two bodies in one model)."""
	out = bytearray(dec)
	changed = 0
	for bone, o in color_offsets(dec):
		src = tuple(dec[o : o + 3])
		new = color_map.get(src)
		if new and bone in (only or {}).get(src, (bone,)):
			out[o : o + 3] = bytes(new)
			changed += 1
	return bytes(out), changed


# battle: header u32 at offset 4 = bone table; per bone a part: u32 vertex bytes, vertices, 12-byte header
# (u16 tri count at +8), 20-byte tri records, u32 quad count, 24-byte quad records; each record = 8 bytes of
# vertex indices then one RGBA per vertex.
def battle_color_offsets(dec: bytes):
	body = struct.unpack_from("<I", dec, 4)[0]  # header word 1: bone table ; parts whose walk does not end at the next part (textured head) are skipped
	n = struct.unpack_from("<I", dec, body)[0]
	parts = sorted({struct.unpack_from("<I", dec, body + 8 + i * 8)[0] for i in range(n)} - {0})
	for i, part in enumerate(parts):
		p = body + part
		verts = struct.unpack_from("<I", dec, p)[0]
		tris = struct.unpack_from("<H", dec, p + 4 + verts + 8)[0]
		p += 4 + verts + 12
		recs = []
		for _ in range(tris):
			recs += [p + 8 + k * 4 for k in range(3)]
			p += 20
		quads = struct.unpack_from("<H", dec, p)[0]
		p += 4
		for _ in range(quads):
			recs += [p + 8 + k * 4 for k in range(4)]
			p += 24
		# the textured head has a different layout: the walk misses the next part, so skip it
		if i + 1 < len(parts) and p != body + parts[i + 1]:
			continue
		yield from recs


def rgb(h: str) -> tuple[int, int, int]:
	return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


# Cait Sith's cat and moogle share CCCCCC: recolor it on the moogle's bones only
FIELD_ONLY = {"KETCY": {rgb("CCCCCC"): {1, 4, 7, 24, 25, 27, 28}}}

# field BCX name -> {outfit RGB: new RGB}
FIELD = {
	"CLOUD": {"614977": "9C223A", "FCA834": "C7D3E6"},  # Cloud: SOLDIER blue -> crimson, blond -> silver
	"BALLET": {"656526": "2A3F7A", "6E5747": "F26B1D", "1E1E1E": "E6C34A"},  # Barret: olive pants -> navy, brown vest -> Goku-gi orange, black hair -> blonde
	"TIFA": {"400000": "0F4A50", "2F1E12": "3F1F52"},  # Tifa: red gloves/boots -> teal, brown hair -> plum
	"EARITH": {"D59C9C": "B49BD9", "990F0F": "5B2A86", "59350C": "3DBFB0"},  # Aerith: pink/red -> lilac/violet, brown hair -> blonde
	"CID": {"1C2841": "2F6B3A", "2B2819": "3A2A5C", "93866D": "D0D4DC"},  # Cid: blue jacket -> forest green, olive pants -> dark purple, khaki hair -> silver
	"RED": {"96431A": "EDEDF2", "660505": "B9BDC8"},  # Red XIII: fur -> white, dark mane/tail tip -> light gray
	"VINCENT": {"4C0202": "0D4D3A", "191919": "A8222E"},  # Vincent: red cape -> emerald, black hair -> crimson
	"YUFI": {"0F360F": "7A1F5C", "1C150D": "1B5E55"},  # Yuffie: green -> plum, dark hair -> teal
	"KETCY": {"4A0311": "0B4A55", "CCCCCC": "F5A0B8"},  # Cait Sith: maroon -> teal, white moogle (cat stays white) -> Majin Buu pink
}
FIELD = {n: {rgb(k): rgb(v) for k, v in m.items()} for n, m in FIELD.items()}

# battle model -> (hue band lo, hi in degrees, wraps through 0 if lo > hi; min saturation; hue shift in degrees)
BATTLE = {
	"BARRETT": ((55, 105, 0.4, 165),), "BARRETT2": ((55, 105, 0.4, 165),),
	"BARRETT3": ((55, 105, 0.4, 165),), "BARRETT4": ((55, 105, 0.4, 165),),
	"TIFA": ((345, 8, 0.6, 185),),
	"EARITH": ((350, 10, 0.2, 270),),
	"CID": ((200, 245, 0.3, 275), (40, 62, 0.35, 230)),  # jacket -> green, pants -> purple
	"VINSENT": ((345, 12, 0.6, 155),), "VINSENT2": ((345, 12, 0.6, 155),), "VINSENT3": ((345, 12, 0.6, 155),),
	"YUFI": ((55, 150, 0.35, 200),),
	"KETCY": ((345, 8, 0.6, 200),),
}


# Cloud's battle colors are not exact either: outfit tones are the cool ones (b >= r, b > g), scaled
# by the ratio that maps his outfit blue to crimson
_CLOUD_RATIO = tuple(n / o for n, o in zip(FIELD["CLOUD"][rgb("614977")], rgb("614977")))


def recolor_battle_cloud(dec: bytes) -> tuple[bytes, int]:
	out = bytearray(dec)
	changed = 0
	for o in battle_color_offsets(dec):
		r, g, b = dec[o : o + 3]
		if b >= r and b > g:
			out[o : o + 3] = bytes(min(255, round(v * k)) for v, k in zip((r, g, b), _CLOUD_RATIO))
			changed += 1
	return bytes(out), changed


def recolor_battle(dec: bytes, bands: tuple) -> tuple[bytes, int]:
	out = bytearray(dec)
	changed = 0
	for o in battle_color_offsets(dec):
		h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in dec[o : o + 3]))
		deg = h * 360
		for lo, hi, min_sat, shift in bands:
			if s >= min_sat and (lo <= deg <= hi if lo <= hi else deg >= lo or deg <= hi):
				new = colorsys.hsv_to_rgb(((deg + shift) % 360) / 360, s, v)
				out[o : o + 3] = bytes(round(c * 255) for c in new)
				changed += 1
				break
	return bytes(out), changed


# Cait Sith's moogle is near-white pink (hue ~300, sat < 0.2): force a Buu-pink tint, keep the shading in value
def recolor_battle_moogle(dec: bytes) -> tuple[bytes, int]:
	out = bytearray(dec)
	changed = 0
	for o in battle_color_offsets(dec):
		h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in dec[o : o + 3]))
		if v >= 0.45 and s <= 0.2 and 270 <= h * 360 <= 345:
			out[o : o + 3] = bytes(round(c * 255) for c in colorsys.hsv_to_rgb(344 / 360, 0.4, v))
			changed += 1
	return bytes(out), changed


# Red XIII's fur is dark-shaded red: desaturate to gray and lift the value so it reads white, keeping some shading
def recolor_battle_white(dec: bytes) -> tuple[bytes, int]:
	out = bytearray(dec)
	changed = 0
	for o in battle_color_offsets(dec):
		h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in dec[o : o + 3]))
		deg = h * 360
		if s >= 0.5 and (deg >= 345 or deg <= 28):
			out[o : o + 3] = bytes(round(c * 255) for c in colorsys.hsv_to_rgb(0, 0, min(1, 0.45 + v * 0.9)))
			changed += 1
	return bytes(out), changed


WORLD_PATHS = ("WORLD/WM0.BSZ", "WORLD/WM1.BSZ", "WORLD/WM2.BSZ", "WORLD/WM3.BSZ")
# Cait Sith's white is plain gray, Vincent's hair black is Tifa's world-map skirt, Barret's 1E1E1E is generic dark: all would hit other data
WORLD_MAP = {k: v for m in FIELD.values() for k, v in m.items() if k not in (rgb("CCCCCC"), rgb("191919"), rgb("1E1E1E"))}
# Tifa's red also appears as 6 stray slots elsewhere in WM3; her model sits in 26000..40000
WORLD_SPAN = {("WORLD/WM3.BSZ", rgb("400000")): (26000, 40000)}


def recolor_world(dec: bytes, path: str) -> tuple[bytes, int]:
	out = bytearray(dec)
	changed = 0
	for o in range(0, len(dec) - 3, 4):
		src = tuple(dec[o : o + 3])
		dst = WORLD_MAP.get(src)
		if dst is None:
			continue
		lo, hi = WORLD_SPAN.get((path, src), (0, len(dec)))
		if lo <= o < hi:
			out[o : o + 3] = bytes(dst)
			changed += 1
	return bytes(out), changed


def _patch(img: bytearray, path: str, fn, *, required: bool = True) -> int:
	new, changed = fn(lzs.decompress(extract_file(img, path)))
	if not changed:
		if required:
			raise SystemExit(f"{path}: nothing to recolor -- already patched or wrong base?")
		return 0
	replace_file_padded(img, path, lzs.compress(new))
	return changed


def apply_patch(img: bytearray) -> dict[str, int]:
	"""Patch the disc image in place; return recolored color count per file."""
	counts = {}
	for name, cmap in FIELD.items():
		counts[f"field {name}"] = _patch(img, f"FIELD/{name}.BCX", lambda d, m=cmap, n=name: recolor(d, m, FIELD_ONLY.get(n)))
	counts["battle CLOUD"] = _patch(img, "ENEMY6/CLOUD.LZS", recolor_battle_cloud)
	for name, band in BATTLE.items():
		counts[f"battle {name}"] = _patch(img, f"ENEMY6/{name}.LZS", lambda d, b=band: recolor_battle(d, b))
	counts["battle KETCY moogle"] = _patch(img, "ENEMY6/KETCY.LZS", recolor_battle_moogle)
	counts["battle RED13"] = _patch(img, "ENEMY6/RED13.LZS", recolor_battle_white)
	for path in WORLD_PATHS:
		counts[path] = _patch(img, path, lambda d, p=path: recolor_world(d, p))
	return counts


if __name__ == "__main__":
	src, dst = Path(sys.argv[1]), Path(sys.argv[2])
	buf = bytearray(src.read_bytes())
	for k, v in apply_patch(buf).items():
		print(f"{k:16}{v}")
	dst.write_bytes(buf)
