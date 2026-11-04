#!/usr/bin/env python3
"""Recolor the nine main party members' outfits.

Field (FIELD/<name>.BCX, LZS, no textures): every polygon carries its own RGBA, so walk the
part headers and remap exact RGB matches.
Battle (ENEMY6/<name>.LZS): vertex colors are shaded, so per-part rules repaint every color inside a
hue/sat/value window to the target hue, keeping the shading. Cloud's outfit instead scales his cool colors toward crimson.
World map (WORLD/WM0-3.BSZ): the same field-style models, patched by exact 4-aligned RGB match.
Field/world hair is a flat color too, so it is remapped; battle hair is picked out of its part by hue/darkness."""

from __future__ import annotations

import colorsys
import importlib.util
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import NamedTuple

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))
from psx_mode2_iso import extract_file, replace_file_padded, walk_tree  # noqa: E402

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

def color_offsets(dec: bytes, first: int | None = None, num_parts: int = 0, to_off=lambda p: p & 0x7FFFFFFF):
	"""(bone, absolute offset, height) of every polygon RGB triple in the decompressed BCX (or, with `first` = the
	first part header of a BSX model, in that model); height is the part-local -z of the color's vertex (a flat
	color: the polygon's mean). `to_off` turns a part's vertex pointer into a file offset (world files hold RAM addresses)."""
	if first is None:
		om = struct.unpack_from("<I", dec, 4)[0]
		num_bones, num_parts = dec[om + 2], dec[om + 3]
		first = om + HDR_SIZE + num_bones * 4
	for i in range(num_parts):
		h = PART_HDR.unpack_from(dec, first + i * 32)
		base = to_off(h[19])
		pos = base + h[14]
		for count_idx, size, cols in KINDS:
			nv = 4 if count_idx in (4, 6, 9, 11) else 3
			for _ in range(h[count_idx]):
				zs = [-struct.unpack_from("<h", dec, base + 4 + dec[pos + j] * 8 + 4)[0] for j in range(nv)]
				for off, n in cols:
					for k in range(n):
						yield h[1], pos + off + k * 4, zs[k] if n > 1 else sum(zs) / nv
				pos += size


RAINBOW = "rainbow"  # map target: spread the source color over the bands below
RAINBOW_STEPS = 6  # field hair shades per band step; 8 no longer fits Yuffie's ISO slot
RAINBOW_BANDS = ("E8283C", "F58A1F", "F2D81E", "3CC850", "2AB8E8", "4A5AF0", "A850E0")


def recolor(dec: bytes, color_map: dict, only: dict | None = None, offsets=None) -> tuple[bytes, int]:
	"""`only` limits a source color to the given bones (for colors shared between two bodies in one model); `offsets` replaces
	the BCX color walk (a world-map model)."""
	out = bytearray(dec)
	hits = []
	for bone, o, z in color_offsets(dec) if offsets is None else offsets:
		src = tuple(dec[o : o + 3])
		new = color_map.get(src)
		if isinstance(new, dict):  # per-bone targets: one source color used by several body parts
			new = new.get(bone)
		if new and bone in (only or {}).get(src, (bone,)):
			hits.append((o, new, z))
	zs = [z for _, new, z in hits if new == RAINBOW]
	for o, new, z in hits:
		if new == RAINBOW:  # red at the top down to violet at the bottom, blended between bands; gouraud blends the rest
			t = (max(zs) - z) / max(1, max(zs) - min(zs)) * (len(RAINBOW_BANDS) - 1)
			t = round(t * RAINBOW_STEPS) / RAINBOW_STEPS  # few distinct colors: the LZS must still fit its ISO slot
			a, f = min(int(t), len(RAINBOW_BANDS) - 2), t - min(int(t), len(RAINBOW_BANDS) - 2)
			new = tuple(round(x + (y - x) * f) for x, y in zip(rgb(RAINBOW_BANDS[a]), rgb(RAINBOW_BANDS[a + 1])))
		out[o : o + 3] = bytes(new)
	return bytes(out), len(hits)


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
	"TIFA": {"400000": "26A65B", "221B19": "26A65B", "4C4C4C": "262626", "CCCCCC": "202020", "333333": "1A1A1A", "2F1E12": "B4501E"},  # Tifa: red gloves and boots -> emerald, white top and gray trim -> black, brown hair -> ginger
	"EARITH": {"D59C9C": "B49BD9", "990F0F": "5B2A86", "59350C": "3DBFB0"},  # Aerith: pink/red -> lilac/violet, brown hair -> teal
	"CID": {"1C2841": "2F6B3A", "2B2819": "8250B4", "93866D": "D0D4DC"},  # Cid: blue jacket -> forest green, olive pants -> Piccolo-gi purple, khaki hair -> silver
	"RED": {"96431A": "EDEDF2", "660505": "B9BDC8", "956518": "2A4FB0", "844C31": "0A0A0A", "3F2923": "0A0A0A"},  # Red XIII: fur -> white, dark mane/tail tip -> light gray, leg bracers -> blue, eyes and scar -> black
	"VINCENT": {  # Vincent: red cape -> yellow, black hair -> crimson, black bodysuit -> Crono: blue tunic, khaki hips, teal thighs, green leggings
		"4C0202": "D8B01C", "191919": "A8222E",
		"131313": {1: "C9C27A", 2: "6FA8C0", 10: "6FA8C0", 15: "6FA8C0", 17: "6FA8C0", 19: "6FA8C0", 23: "6FA8C0", 20: "3F7A3A", 24: "3F7A3A"},
	},
	"YUFI": {"0F360F": "7A1F5C", "1C150D": RAINBOW},  # Yuffie: green -> plum, dark hair -> rainbow
	"KETCY": {"4A0311": "0B4A55", "CCCCCC": "F5A0B8"},  # Cait Sith: maroon -> teal, white moogle (cat stays white) -> Majin Buu pink
}
def _target(v):
	return v if v == RAINBOW else {b: rgb(c) for b, c in v.items()} if isinstance(v, dict) else rgb(v)


FIELD = {n: {rgb(k): _target(v) for k, v in m.items()} for n, m in FIELD.items()}

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


SNOW_RIDER = range(13)  # TMD objects 0-12 of MINI/TMD.LZS and TMD2.LZS: Cloud on the snowboard (hair, face, jacket, legs)
_SNOW_HAIR = FIELD["CLOUD"][rgb("FCA834")]

def recolor_snowboard(dec: bytes) -> tuple[bytes, int]:
	"""Snowboard minigame: Gouraud TMD triangles; hair gold -> silver by brightness, blue-purple outfit -> crimson."""
	out = bytearray(dec)
	changed = 0
	for obj in SNOW_RIDER:
		pt, npk = struct.unpack_from("<II", dec, 12 + 28 * obj + 16)
		o = 12 + pt
		for _ in range(npk):
			ilen, mode = dec[o + 1], dec[o + 3]
			o += 4
			for c in range(o, o + 12, 4) if mode == 0x31 else ():
				r, g, b = dec[c : c + 3]
				if obj == 0 and r > g > b and r - b > r // 2:  # only the head object: boots and belts are brown too
					new = (round(v * max(r, g, b) / 255) for v in _SNOW_HAIR)
				elif b >= r and b > g:
					new = (min(255, round(v * k)) for v, k in zip((r, g, b), _CLOUD_RATIO))
				else:
					continue
				out[c : c + 3] = bytes(new)
				changed += 1
			o += ilen * 4
	return bytes(out), changed


class Rule(NamedTuple):
	hue: tuple  # degrees lo, hi; wraps through 0 when lo > hi
	to: tuple  # (target hue, target sat or None to keep it, value add, value gain): v' = min(1, add + v * gain)
	parts: frozenset | None = None  # indices into the offset-sorted part list, None = every part
	sat: tuple = (0, 1)
	val: tuple = (0, 1)
	top: float | None = None  # only vertices in this back fraction of the part's y range (small y)
	up: float | None = None  # only vertices in this top fraction of the part's z range (heads hang from their joint, so small z is up)
	front: float | None = None  # only vertices in this front fraction of the part's y range (large y)


def battle_polys(dec: bytes, geometry: bool = False):
	"""(part index, [(color offset, vertex y, vertex z), ...]) per vertex-colored polygon of every part (`geometry`: plus the part's
	file offset and the record offset, whose first u16s index the 8-byte vertices at part + 4). Plain parts are gouraud
	tris then a u32 quad count and quads; textured parts (heads, Red XIII's tattoos) start with a u16 count of 16-byte
	textured records, and the quad count at the part's end fixes where each block starts."""
	body = struct.unpack_from("<I", dec, 4)[0]
	n = struct.unpack_from("<I", dec, body)[0]
	parts = sorted({struct.unpack_from("<I", dec, body + 8 + i * 8)[0] for i in range(n)} - {0})
	# meshes the bone table never points at (Red XIII's foot) follow the last part back to back
	while True:
		p = body + parts[-1]
		verts = struct.unpack_from("<I", dec, p)[0]
		tris = struct.unpack_from("<H", dec, p + 4 + verts + 8)[0]
		q = p + 4 + verts + 12 + tris * 20
		end = q + 4 + struct.unpack_from("<H", dec, q)[0] * 24
		if end + 8 > len(dec) or struct.unpack_from("<H", dec, p + 4 + verts)[0]:
			break
		nverts = struct.unpack_from("<I", dec, end)[0]
		if nverts % 8 or not 0 < nverts < 4096 or end + 4 + nverts + 4 > len(dec):
			break
		if struct.unpack_from("<HH", dec, end + 4 + nverts) not in ((0, 0x20), (0, 0x25)):
			break
		parts.append(end - body)
	for i, part in enumerate(parts):
		p = body + part
		verts = struct.unpack_from("<I", dec, p)[0]
		start = p + 4 + verts + 12
		tris = struct.unpack_from("<H", dec, start - 4)[0]
		q = start + tris * 20
		quads = struct.unpack_from("<H", dec, q)[0]
		if i + 1 < len(parts) and q + 4 + quads * 24 != body + parts[i + 1]:
			ntex = struct.unpack_from("<H", dec, p + 4 + verts)[0]
			nxt = body + parts[i + 1]
			for quads in range(200):
				q = nxt - quads * 24 - 4
				tri_bytes = q - start - ntex * 16
				if struct.unpack_from("<H", dec, q)[0] == quads and tri_bytes >= 0 and tri_bytes % 20 == 0:
					start, tris = start + ntex * 16, tri_bytes // 20
					break
			else:
				continue
		# vertex index words are byte offsets into the part's 8-byte (x, y, z, pad) vertices
		y = lambda rec, j, p=p: struct.unpack_from("<hh", dec, p + 6 + struct.unpack_from("<H", dec, rec + j * 2)[0])
		# the first color's fourth byte is the GPU command: 0x30 gouraud tri, 0x38 quad (+2 semi-transparent); anything else is
		# a textured record the layout guess swallowed, and recoloring it corrupts the model
		for k in range(tris):
			r = start + k * 20
			if dec[r + 11] in (0x30, 0x32):
				yield (i, [(r + 8 + j * 4, *y(r, j)) for j in range(3)], *((p, r) if geometry else ()))
		for k in range(quads):
			r = q + 4 + k * 24
			if dec[r + 11] in (0x38, 0x3A):
				yield (i, [(r + 8 + j * 4, *y(r, j)) for j in range(4)], *((p, r) if geometry else ()))


def _matches(rule: Rule, part: int, color: bytes, y: int, z: int, span: tuple) -> bool:
	if rule.parts is not None and part not in rule.parts:
		return False
	h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in color))
	deg, (lo, hi) = h * 360, rule.hue
	if not (lo <= deg <= hi if lo <= hi else deg >= lo or deg <= hi):
		return False
	if not (rule.sat[0] <= s <= rule.sat[1] and rule.val[0] <= v <= rule.val[1]):
		return False
	return (
		(rule.top is None or y <= span[0] + rule.top * (span[1] - span[0]))
		and (rule.up is None or z <= span[2] + rule.up * (span[3] - span[2]))
		and (rule.front is None or y >= span[1] - rule.front * (span[1] - span[0]))
	)


def _paint(rule: Rule, color: bytes, y: int, span: tuple) -> bytes:
	h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in color))
	th, ts, add, gain = rule.to
	if th is None:  # rainbow: red at the top of the part down to violet at the bottom
		th = 280 * (y - span[0]) / max(1, span[1] - span[0])
	return bytes(round(c * 255) for c in colorsys.hsv_to_rgb(th / 360, s if ts is None else ts, min(1, add + v * gain)))


def recolor_battle(dec: bytes, rules: tuple) -> tuple[bytes, int]:
	"""First matching rule per vertex color. A polygon whose corners mostly match one rule gets it on every corner, so
	hair and outfits recolor as whole faces instead of speckles."""
	polys = list(battle_polys(dec))
	span = {}
	for part, corners in polys:
		for _, y, z in corners:
			ylo, yhi, zlo, zhi = span.get(part, (y, y, z, z))
			span[part] = (min(ylo, y), max(yhi, y), min(zlo, z), max(zhi, z))
	out = bytearray(dec)
	changed = 0
	for part, corners in polys:
		hits = [next((r for r in rules if _matches(r, part, dec[o : o + 3], y, z, span[part])), None) for o, y, z in corners]
		best = Counter(r for r in hits if r is not None).most_common(1)
		fill = best[0][0] if best and best[0][1] * 2 > len(hits) else None
		for (o, y, _), r in zip(corners, hits):
			if r or fill:
				out[o : o + 3] = _paint(r or fill, dec[o : o + 3], y, span[part])
				changed += 1
	return bytes(out), changed


_F = frozenset
# battle model -> rules by part (see battle_polys). Battle vertex colors are shaded and about half field brightness;
# skin is hue 0-30, so rules pin hue/sat/value windows per part to leave skin, eyes and metal alone.
_BARRETT = (
	Rule((0, 45), (46, 0.68, 0.3, 1.6), _F({2}), val=(0, 0.3), up=0.12),  # dark hair cap on top of the head -> blonde; the lighter skin below its edge stays
	Rule((15, 30), (46, 0.68, 0.3, 1.6), _F({2}), sat=(0.5, 0.7), val=(0, 0.115), front=0.25),  # beard
	Rule((25, 50), (46, 0.68, 0.3, 1.6), _F({2}), sat=(0.25, 0.5), val=(0.1, 0.3), front=0.25),  # beard stubble
	Rule((50, 110), (224, 0.7, 0.12, 1.5), _F({0, 8, 9, 12, 13}), sat=(0.25, 1)),  # olive pants -> navy
	Rule((33, 62), (24, 0.85, 0.05, 2.2), _F({1}), sat=(0.25, 1)),  # khaki vest -> Goku-gi orange
)
# Barret's face texture: CLUT rows at VRAM (0, 480..482); row 481's indices 3 and 4 are the flat near-black patches that paint his beard
_BARRETT_CLUT = struct.pack("<IIIHHHH", 0x10, 8, 108, 0, 480, 16, 3)


def recolor_barrett_beard(dec: bytes) -> tuple[bytes, int]:
	at = dec.find(_BARRETT_CLUT)
	if at < 0:
		return dec, 0
	out = bytearray(dec)
	r, g, b = (round(c * 31) for c in colorsys.hsv_to_rgb(46 / 360, 0.68, 0.6))
	for idx in (3, 4):
		struct.pack_into("<H", out, at + 20 + 32 + idx * 2, r | g << 5 | b << 10)
	return bytes(out), 2


def recolor_barrett(dec: bytes) -> tuple[bytes, int]:
	dec, n = recolor_battle(dec, _BARRETT)
	dec, m = recolor_barrett_beard(dec)
	return dec, n + m


_VINCENT = (
	Rule((0, 360), (354, 0.8, 0.04, 3), _F({1}), sat=(0, 0.35), val=(0, 0.35)),  # black hair -> crimson
	Rule((285, 315), (354, 0.8, 0.04, 3), _F({1}), sat=(0.5, 1), val=(0, 0.07)),
	Rule((285, 359), (48, 0.85, 0.1, 1.8), _F({0, 1, *range(7, 19), 28, 31}), sat=(0.85, 1)),  # cape, collar, headband -> yellow
	Rule((0, 360), (200, 0.5, 0.22, 1), _F({2, 3, 4, 5, 6, 20, 24}), val=(0, 0.3)),  # black vest and thighs -> Crono's teal-blue tunic
	Rule((0, 360), (58, 0.45, 0.3, 1), _F({19}), val=(0, 0.3)),  # black hips -> khaki
	Rule((0, 360), (115, 0.5, 0.2, 1), _F({21, 25}), sat=(0, 0.25), val=(0, 0.3)),  # lower legs -> green leggings, brown boots kept
	Rule((200, 300), (115, 0.5, 0.2, 1), _F({21, 25}), val=(0, 0.3)),
)
_MOOGLE = _F({0, 1, 2, 3, 4, 5, 6, 10, 13, 25, 27})
_RED_WHITE = (230, 0.03, 0.3, 0.5)
_RED_CLUT = struct.pack("<IIIHHHH", 0x10, 8, 76, 0, 480, 16, 2)


def recolor_red13_legs(dec: bytes) -> tuple[bytes, int]:
	"""Leg texture: the thigh triangles (parts 12, 21, 32) sample texels u 128-207, v 0-79
	of the 4bpp image, where palette index 3 is dark maroon; the head's tattoo bars sit below v 80 and stay. Index 3 -> 2 (black)."""
	at = dec.find(_RED_CLUT)
	if at < 0:
		return dec, 0
	img = at + 8 + 76 + 12  # TIM: header, CLUT block, image block header
	w = struct.unpack_from("<H", dec, img - 4)[0] * 2  # bytes per row
	out, n = bytearray(dec), 0
	for v in range(80):
		for u in range(128, 208):
			o = img + v * w + u // 2
			if (out[o] >> 4 if u & 1 else out[o] & 15) == 3:
				out[o] = out[o] & 15 | 2 << 4 if u & 1 else out[o] & 0xF0 | 2
				n += 1
	return bytes(out), n


def recolor_red13_face(dec: bytes) -> tuple[bytes, int]:
	"""Head texture: the scar (u 66-124, v 112-147) and the eyes (u 2-56, v 105-157) have every opaque texel set to palette index 2 (black)."""
	at = dec.find(_RED_CLUT)
	if at < 0:
		return dec, 0
	img = at + 8 + 76 + 12
	w = struct.unpack_from("<H", dec, img - 4)[0] * 2
	out, n = bytearray(dec), 0
	for (u0, u1), (v0, v1) in (((66, 125), (112, 148)), ((2, 57), (105, 158))):
		for v in range(v0, v1):
			for u in range(u0, u1):
				o = img + v * w + u // 2
				if (out[o] >> 4 if u & 1 else out[o] & 15) not in (0, 2):
					out[o] = out[o] & 15 | 2 << 4 if u & 1 else out[o] & 0xF0 | 2
					n += 1
	return bytes(out), n


def recolor_red13(dec: bytes) -> tuple[bytes, int]:
	dec, n = recolor_battle(dec, BATTLE["RED13"])
	dec, m = recolor_red13_legs(dec)
	dec, k = recolor_red13_face(dec)
	return dec, n + m + k


BATTLE = {
	"CLOUD": (Rule((28, 60), (215, 0.1, 0, 1), _F({2}), sat=(0.55, 1)),),  # blond hair -> silver
	"BARRETT": _BARRETT, "BARRETT2": _BARRETT, "BARRETT3": _BARRETT, "BARRETT4": _BARRETT,
	"TIFA": (
		Rule((0, 45), (20, 0.9, 0.15, 1.8), _F({1}), sat=(0.25, 1), val=(0, 0.22)),  # brown hair -> ginger
		Rule((10, 45), (20, 0.9, 0.15, 1.8), _F({1}), sat=(0.25, 1), val=(0, 0.3)),  # dark patches; the red-brown neck is hue < 10
		Rule((0, 360), (20, 0.9, 0.15, 1.8), _F({2, 3, 4, 6})),  # ponytail
		Rule((0, 360), (0, 0, 0.02, 0.4), _F({0}), sat=(0, 0.37)),  # white tank top -> black
		Rule((0, 360), (150, 0.85, 0, 1.6), _F({5})),  # hair tie
		Rule((0, 360), (0, 0, 0, 0.5), _F({7, 8, 13})),  # sleeves and skirt -> black
		Rule((0, 50), (150, 0.85, 0, 1.6), _F({11, 12, 16, 17}), sat=(0.45, 1)),  # boots -> emerald, gray soles kept
		Rule((280, 35), (150, 0.85, 0, 1.6), _F({10, 15, 18, 19, 20}), sat=(0.9, 1)),  # glove red on fists and forearms
		Rule((280, 20), (150, 0.85, 0, 1.6), _F({10, 15, 18, 19, 20}), sat=(0.55, 1), val=(0, 0.35)),  # dark glove leather
		Rule((280, 359), (150, 0.85, 0, 1.6), _F({10, 15, 19, 20, 22}), sat=(0.15, 1)),  # glove maroon
		Rule((315, 359), (150, 0.85, 0, 1.6), _F({18}), sat=(0.4, 1)),
	),
	"EARITH": (
		Rule((20, 45), (173, 0.7, 0.03, 1.8), _F({2}), sat=(0.6, 1)),  # brown hair -> Bulma teal; face skin is hue < 19
		Rule((20, 45), (173, 0.7, 0.03, 1.8), _F({2}), sat=(0.3, 1), val=(0, 0.3)),  # hair shading
		Rule((0, 19), (173, 0.7, 0.03, 1.8), _F({2}), sat=(0.64, 1), val=(0, 0.15)),  # near-black hair at the back
		Rule((340, 12), (266, None, 0, 1), _F({2}), sat=(0.3, 1), top=0.1),  # ribbons on the back of the head -> lilac
		Rule((15, 45), (173, 0.7, 0.03, 1.8), _F({3, 4, 5, 6}), sat=(0.55, 1)),  # braid
		Rule((320, 8), (272, None, 0, 1), sat=(0.7, 1)),  # jacket red -> violet
		Rule((320, 352), (266, None, 0, 1), sat=(0.25, 0.7)),  # dress pink -> lilac
	),
	"CID": (
		Rule((35, 62), (220, 0.08, 0.05, 0.95), _F({2}), sat=(0.3, 1)),  # blond hair -> silver
		Rule((170, 250), (131, None, 0, 1), _F({1, 3, 4, 6, 7, 8, 9}), sat=(0.2, 1)),  # blue jacket -> green
		Rule((35, 70), (270, 0.55, 0, 2), _F({0, 11, 12, 15, 16}), sat=(0.25, 1)),  # olive pants -> light Piccolo purple
	),
	"VINSENT": _VINCENT, "VINSENT2": _VINCENT, "VINSENT3": _VINCENT,
	"YUFI": (
		Rule((30, 125), (None, 0.85, 0.35, 1), _F({2}), val=(0, 0.25)),  # dark hair -> rainbow bands by height
		Rule((55, 150), (320, None, 0, 1), sat=(0.35, 1)),  # green -> plum
	),
	"RED13": (
		Rule((340, 10), (225, 0.08, 0.25, 0.6), _F({3}), sat=(0.8, 1)),  # red mane -> light gray
		Rule((330, 45), _RED_WHITE, _F({3}), sat=(0.3, 1), val=(0.08, 1)),  # face fur -> white, eyes/nose stay dark
		Rule((330, 38), _RED_WHITE, _F(set(range(40)) - {3, 29, 30, 31}), sat=(0.2, 1)),  # body fur
		Rule((330, 70), (195, 0.3, 0.2, 0.8), _F({29, 30, 31}), sat=(0.2, 1)),  # tail flame -> pale ice blue
		Rule((30, 70), (225, 0.8, 0.1, 0.9), _F({13, 18, 21, 23, 32, 34}), sat=(0.4, 1)),  # gold leg bracers -> blue
	),
	"KETCY": (
		Rule((240, 30), (343, 0.38, 0, 1), _MOOGLE, sat=(0, 0.6)),  # moogle -> Buu pink, cat untouched
		Rule((0, 360), (343, 0.38, 0, 1), _MOOGLE, sat=(0, 0.2)),
		Rule((340, 15), (189, None, 0, 1), _F({7, 17, 18, 23, 24}), sat=(0.6, 1)),  # cat's red cape and boots -> teal
	),
}


WORLD_PATHS = ("WORLD/WM0.BSZ", "WORLD/WM1.BSZ", "WORLD/WM2.BSZ", "WORLD/WM3.BSZ")
# Cait Sith's white is plain gray, Vincent's hair black is Tifa's world-map skirt, Barret's 1E1E1E is generic dark: all would hit other data
WORLD_MAP = {k: v for m in FIELD.values() for k, v in m.items() if v != RAINBOW and k not in (rgb("CCCCCC"), rgb("191919"), rgb("1E1E1E"), rgb("131313"), rgb("4C4C4C"), rgb("333333"))}
# Tifa's black outfit on her WM1 model (WM3 uses WORLD_ONLY spans)
WORLD_FILE = {("WORLD/WM1.BSZ", rgb("4C4C4C")): rgb("262626"), ("WORLD/WM1.BSZ", rgb("CCCCCC")): rgb("202020"), ("WORLD/WM1.BSZ", rgb("333333")): rgb("1A1A1A")}
# Tifa's red also appears as 6 stray slots elsewhere in WM3; her model sits in 26000..40000
WORLD_SPAN = {("WORLD/WM3.BSZ", rgb("400000")): (26000, 40000)}
# These colors recolor only inside the owning model's WM3 spans, as ((new color, spans), ...): Barret hair, Vincent hair and
# bodysuit (torso/arms/thighs blue, hips khaki, shins green; spans follow the field bone order), Cait's moogle bones (cat sits in 72800..75216)
WORLD_ONLY = {
	rgb("1E1E1E"): ((rgb("E6C34A"), ((21900, 22800),)),),
	rgb("191919"): ((rgb("A8222E"), ((78100, 81200),)),),
	rgb("4C4C4C"): ((rgb("262626"), ((26000, 40000),)),),
	rgb("333333"): ((rgb("1A1A1A"), ((26000, 40000),)),),
	rgb("131313"): ((rgb("C9C27A"), ((76100, 76500), (83300, 83500))), (rgb("3F7A3A"), ((83900, 84100), (84900, 85100))), (rgb("6FA8C0"), ((76500, 83300), (83500, 83900), (84100, 84900)))),
	rgb("CCCCCC"): ((rgb("F5A0B8"), ((67400, 70600), (75216, 76100))), (rgb("202020"), ((26000, 40000),))),
}


def world_models(dec: bytes):
	"""(skeleton offset, bones, parts, pointer -> offset) per model of a WORLD/WM*.BSZ: BCX-style 36-byte headers from
	offset 24, each pointing (by RAM address) at its skeleton."""
	k = struct.unpack_from("<I", dec, 16)[0] - 24  # RAM address of file offset 0
	return [(struct.unpack_from("<I", dec, h + 28)[0] - k, dec[h + 2], dec[h + 3], lambda p: p - k)
		for h in (24 + 36 * i for i in range(struct.unpack_from("<I", dec, 12)[0]))]


# Yuffie's WM3 model gets the field hair gradient (the whole-file color map can't: her hair color is plain dark)
WORLD_HAIR = ("WORLD/WM3.BSZ", 5, {rgb("1C150D"): RAINBOW})


def recolor_world(dec: bytes, path: str) -> tuple[bytes, int]:
	out = bytearray(dec)
	changed = 0
	for o in range(0, len(dec) - 3, 4):
		src = tuple(dec[o : o + 3])
		dst = WORLD_MAP.get(src) or WORLD_FILE.get((path, src))
		if dst is None:
			for new, spans in WORLD_ONLY.get(src, ()) if path == "WORLD/WM3.BSZ" else ():
				if any(lo <= o < hi for lo, hi in spans):
					out[o : o + 3] = bytes(new)
					changed += 1
					break
			continue
		lo, hi = WORLD_SPAN.get((path, src), (0, len(dec)))
		if lo <= o < hi:
			out[o : o + 3] = bytes(dst)
			changed += 1
	if path == WORLD_HAIR[0] and len(models := world_models(dec)) > WORLD_HAIR[1]:
		at, nb, np_, to_off = models[WORLD_HAIR[1]]
		hair, n = recolor(bytes(out), WORLD_HAIR[2], offsets=list(color_offsets(dec, at + nb * 4, np_, to_off)))
		out, changed = bytearray(hair), changed + n
	return bytes(out), changed


# Wall Market / Don Corneo dress models live inside the field BSX files. Several BSX hold other outfits of the same
# characters with identical (model id, bones, parts), so the polygon-color count picks out the dress.
# (id, bones, parts, colors) -> hair back to the party theme; dress and trim in yellow / magenta-pink / ivory, which neither
# the original dresses (blue, red, purple) nor the party recolors (crimson, lilac, black + emerald) use
DRESS = {
	(0, 22, 16, 1340): {"FCA834": "C7D3E6", "614977": "F2C230", "FC3434": "FFF4D6", "BD2727": "C99A1A"},  # Cloud
	(1, 24, 17, 1883): {"59350C": "3DBFB0", "990F0F": "D6338F", "B90101": "9E1F68", "D59C9C": "FFD9A8", "49D545": "FFE9C7"},  # Aerith
	(3, 25, 16, 1744): {"2F1E12": "B4501E", "5B2EEB": "F4EFE6", "4A0BFF": "B9B4A8", "6F1EEB": "DAD4C6", "D0A500": "9AA0AE"},  # Tifa
}
DRESS = {k: {rgb(a): rgb(b) for a, b in m.items()} for k, m in DRESS.items()}

CLOUD_IDS = (0, 33)

def recolor_dress(dec: bytes) -> tuple[bytes, int]:
	out = bytearray(dec)
	changed = 0
	om = struct.unpack_from("<I", dec, 4)[0]
	for i in range(struct.unpack_from("<I", dec, om + 4)[0]):
		h = om + 16 + 48 * i
		model_id, _, skeleton = struct.unpack_from("<HHI", dec, h)
		num_bones, num_parts = dec[h + 23], dec[h + 35]
		first = h + skeleton + num_bones * 4
		offs = [o for _, o, _ in color_offsets(dec, first, num_parts)]
		# other Cloud variants (id 0 field, 33 world-map/rootmap) get his normal recolor
		cmap = DRESS.get((model_id, num_bones, num_parts, len(offs))) or (FIELD["CLOUD"] if model_id in CLOUD_IDS else None)
		for o in offs if cmap else ():
			new = cmap.get(tuple(dec[o : o + 3]))
			if new:
				out[o : o + 3] = bytes(new)
				changed += 1
	return bytes(out), changed

def battle_fn(name: str):
	rules = BATTLE[name]
	return recolor_barrett if rules is _BARRETT else recolor_red13 if name == "RED13" else lambda d: recolor_battle(d, rules)


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
	counts["battle CLOUD outfit"] = _patch(img, "ENEMY6/CLOUD.LZS", recolor_battle_cloud)
	for name in BATTLE:
		counts[f"battle {name}"] = _patch(img, f"ENEMY6/{name}.LZS", battle_fn(name))
	# HICLOUD: high-res Cloud with the same part layout as CLOUD.LZS
	counts["battle HICLOUD outfit"] = _patch(img, "ENEMY6/HICLOUD.LZS", recolor_battle_cloud)
	counts["battle HICLOUD hair"] = _patch(img, "ENEMY6/HICLOUD.LZS", battle_fn("CLOUD"))
	for name in ("TMD", "TMD2"):
		counts[f"snowboard {name}"] = _patch(img, f"MINI/{name}.LZS", recolor_snowboard)
	for path in WORLD_PATHS:
		counts[path] = _patch(img, path, lambda d, p=path: recolor_world(d, p))
	for path, node in walk_tree(img).items():
		if path.startswith("/FIELD/") and path.endswith(".BSX") and node.size > 2048:  # 2048 B: unused stubs and WM* world-map files
			if n := _patch(img, path[1:], recolor_dress, required=False):
				counts["dress " + path[7:-4]] = n
	return counts


if __name__ == "__main__":
	src, dst = Path(sys.argv[1]), Path(sys.argv[2])
	buf = bytearray(src.read_bytes())
	for k, v in apply_patch(buf).items():
		print(f"{k:16}{v}")
	dst.write_bytes(buf)
