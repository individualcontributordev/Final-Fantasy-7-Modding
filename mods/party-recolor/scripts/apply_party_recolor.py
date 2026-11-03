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
	"EARITH": {"D59C9C": "B49BD9", "990F0F": "5B2A86", "59350C": "3DBFB0"},  # Aerith: pink/red -> lilac/violet, brown hair -> teal
	"CID": {"1C2841": "2F6B3A", "2B2819": "3A2A5C", "93866D": "D0D4DC"},  # Cid: blue jacket -> forest green, olive pants -> dark purple, khaki hair -> silver
	"RED": {"96431A": "EDEDF2", "660505": "B9BDC8"},  # Red XIII: fur -> white, dark mane/tail tip -> light gray
	"VINCENT": {"4C0202": "0D4D3A", "191919": "A8222E"},  # Vincent: red cape -> emerald, black hair -> crimson
	"YUFI": {"0F360F": "7A1F5C", "1C150D": "1B5E55"},  # Yuffie: green -> plum, dark hair -> teal
	"KETCY": {"4A0311": "0B4A55", "CCCCCC": "F5A0B8"},  # Cait Sith: maroon -> teal, white moogle (cat stays white) -> Majin Buu pink
}
FIELD = {n: {rgb(k): rgb(v) for k, v in m.items()} for n, m in FIELD.items()}

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


class Rule(NamedTuple):
	hue: tuple  # degrees lo, hi; wraps through 0 when lo > hi
	to: tuple  # (target hue, target sat or None to keep it, value add, value gain): v' = min(1, add + v * gain)
	parts: frozenset | None = None  # indices into the offset-sorted part list, None = every part
	sat: tuple = (0, 1)
	val: tuple = (0, 1)
	top: float | None = None  # only vertices in this top fraction of the part's height


def battle_polys(dec: bytes):
	"""(part index, [(color offset, vertex y), ...]) per vertex-colored polygon of every part. Plain parts are gouraud
	tris then a u32 quad count and quads; textured parts (heads, Red XIII's tattoos) start with a u16 count of 16-byte
	textured records, and the quad count at the part's end fixes where each block starts."""
	body = struct.unpack_from("<I", dec, 4)[0]
	n = struct.unpack_from("<I", dec, body)[0]
	parts = sorted({struct.unpack_from("<I", dec, body + 8 + i * 8)[0] for i in range(n)} - {0})
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
		y = lambda rec, j, p=p: struct.unpack_from("<h", dec, p + 6 + struct.unpack_from("<H", dec, rec + j * 2)[0])[0]
		# the first color's fourth byte is the GPU command: 0x30 gouraud tri, 0x38 quad (+2 semi-transparent); anything else is
		# a textured record the layout guess swallowed, and recoloring it corrupts the model
		for k in range(tris):
			r = start + k * 20
			if dec[r + 11] in (0x30, 0x32):
				yield i, [(r + 8 + j * 4, y(r, j)) for j in range(3)]
		for k in range(quads):
			r = q + 4 + k * 24
			if dec[r + 11] in (0x38, 0x3A):
				yield i, [(r + 8 + j * 4, y(r, j)) for j in range(4)]


def _matches(rule: Rule, part: int, color: bytes, y: int, span: tuple) -> bool:
	if rule.parts is not None and part not in rule.parts:
		return False
	h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in color))
	deg, (lo, hi) = h * 360, rule.hue
	if not (lo <= deg <= hi if lo <= hi else deg >= lo or deg <= hi):
		return False
	if not (rule.sat[0] <= s <= rule.sat[1] and rule.val[0] <= v <= rule.val[1]):
		return False
	return rule.top is None or y <= span[0] + rule.top * (span[1] - span[0])  # y grows downward


def _paint(rule: Rule, color: bytes) -> bytes:
	h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in color))
	th, ts, add, gain = rule.to
	return bytes(round(c * 255) for c in colorsys.hsv_to_rgb(th / 360, s if ts is None else ts, min(1, add + v * gain)))


def recolor_battle(dec: bytes, rules: tuple) -> tuple[bytes, int]:
	"""First matching rule per vertex color. A polygon whose corners mostly match one rule gets it on every corner, so
	hair and outfits recolor as whole faces instead of speckles."""
	polys = list(battle_polys(dec))
	span = {}
	for part, corners in polys:
		for _, y in corners:
			lo, hi = span.get(part, (y, y))
			span[part] = (min(lo, y), max(hi, y))
	out = bytearray(dec)
	changed = 0
	for part, corners in polys:
		hits = [next((r for r in rules if _matches(r, part, dec[o : o + 3], y, span[part])), None) for o, y in corners]
		best = Counter(r for r in hits if r is not None).most_common(1)
		fill = best[0][0] if best and best[0][1] * 2 > len(hits) else None
		for (o, _), r in zip(corners, hits):
			if r or fill:
				out[o : o + 3] = _paint(r or fill, dec[o : o + 3])
				changed += 1
	return bytes(out), changed


_F = frozenset
# battle model -> rules by part (see battle_polys). Battle vertex colors are shaded and about half field brightness;
# skin is hue 0-30, so rules pin hue/sat/value windows per part to leave skin, eyes and metal alone.
_BARRETT = (
	Rule((0, 40), (46, 0.68, 0.25, 1.6), _F({2}), top=0.42),  # the buzz cut is skin-toned: top of the head -> blonde
	Rule((0, 45), (46, 0.68, 0.3, 1.6), _F({2}), sat=(0.85, 1), val=(0, 0.12)),  # near-black red-brown hair at the back and sides
	Rule((15, 30), (46, 0.68, 0.3, 1.6), _F({2}), sat=(0.5, 0.7), val=(0, 0.115)),  # beard
	Rule((25, 50), (46, 0.68, 0.3, 1.6), _F({2}), sat=(0.25, 0.5), val=(0.1, 0.3)),  # beard stubble
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
	Rule((285, 359), (162, None, 0, 1), _F({0, 1, *range(7, 19), 28, 31}), sat=(0.85, 1)),  # cape, collar, headband -> emerald
)
_MOOGLE = _F({0, 1, 2, 3, 4, 5, 6, 10, 13, 25, 27})
_RED_WHITE = (230, 0.03, 0.3, 0.5)
BATTLE = {
	"CLOUD": (Rule((28, 60), (215, 0.1, 0, 1), _F({2}), sat=(0.55, 1)),),  # blond hair -> silver
	"BARRETT": _BARRETT, "BARRETT2": _BARRETT, "BARRETT3": _BARRETT, "BARRETT4": _BARRETT,
	"TIFA": (
		Rule((0, 45), (278, 0.62, 0.15, 1.8), _F({1}), sat=(0.25, 1), val=(0, 0.22)),  # brown hair -> plum
		Rule((0, 360), (278, 0.62, 0.15, 1.8), _F({2, 3, 4, 6})),  # ponytail
		Rule((0, 50), (186, 0.85, 0, 1), _F({11, 12, 16, 17}), sat=(0.45, 1)),  # boots -> teal, gray soles kept
		Rule((280, 35), (186, 0.85, 0, 1), _F({10, 15, 18, 19, 20}), sat=(0.9, 1)),  # glove red on fists and forearms
		Rule((280, 20), (186, 0.85, 0, 1), _F({10, 15, 18, 19, 20}), sat=(0.55, 1), val=(0, 0.35)),  # dark glove leather
		Rule((280, 359), (186, 0.85, 0, 1), _F({10, 15, 19, 20}), sat=(0.15, 1)),  # glove maroon
		Rule((315, 359), (186, 0.85, 0, 1), _F({18}), sat=(0.4, 1)),
	),
	"EARITH": (
		Rule((15, 45), (173, 0.7, 0.03, 1.8), _F({2}), sat=(0.6, 1)),  # brown hair -> Bulma teal
		Rule((0, 45), (173, 0.7, 0.03, 1.8), _F({2}), sat=(0.55, 1), val=(0, 0.2)),
		Rule((15, 45), (173, 0.7, 0.03, 1.8), _F({3, 4, 5, 6}), sat=(0.55, 1)),  # braid
		Rule((320, 8), (272, None, 0, 1), sat=(0.7, 1)),  # jacket red -> violet
		Rule((320, 352), (266, None, 0, 1), sat=(0.25, 0.7)),  # dress pink -> lilac
	),
	"CID": (
		Rule((35, 62), (220, 0.08, 0.05, 0.95), _F({2}), sat=(0.3, 1)),  # blond hair -> silver
		Rule((170, 250), (131, None, 0, 1), _F({1, 3, 4, 6, 7, 8, 9}), sat=(0.2, 1)),  # blue jacket -> green
		Rule((35, 70), (259, None, 0, 1), _F({0, 11, 12, 15, 16}), sat=(0.25, 1)),  # olive pants -> purple
	),
	"VINSENT": _VINCENT, "VINSENT2": _VINCENT, "VINSENT3": _VINCENT,
	"YUFI": (
		Rule((30, 125), (172, 0.7, 0.02, 1.4), _F({2}), val=(0, 0.25)),  # dark hair -> teal
		Rule((55, 150), (320, None, 0, 1), sat=(0.35, 1)),  # green -> plum
	),
	"RED13": (
		Rule((340, 10), (225, 0.08, 0.25, 0.6), _F({3}), sat=(0.8, 1)),  # red mane -> light gray
		Rule((330, 45), _RED_WHITE, _F({3}), sat=(0.3, 1), val=(0.08, 1)),  # face fur -> white, eyes/nose stay dark
		Rule((330, 38), _RED_WHITE, _F(set(range(36)) - {3, 29, 30, 31}), sat=(0.2, 1)),  # body fur; the tail flame stays fire
	),
	"KETCY": (
		Rule((240, 30), (343, 0.38, 0, 1), _MOOGLE, sat=(0, 0.6)),  # moogle -> Buu pink, cat untouched
		Rule((0, 360), (343, 0.38, 0, 1), _MOOGLE, sat=(0, 0.2)),
		Rule((340, 15), (189, None, 0, 1), _F({7, 17, 18, 23, 24}), sat=(0.6, 1)),  # cat's red cape and boots -> teal
	),
}


WORLD_PATHS = ("WORLD/WM0.BSZ", "WORLD/WM1.BSZ", "WORLD/WM2.BSZ", "WORLD/WM3.BSZ")
# Cait Sith's white is plain gray, Vincent's hair black is Tifa's world-map skirt, Barret's 1E1E1E is generic dark: all would hit other data
WORLD_MAP = {k: v for m in FIELD.values() for k, v in m.items() if k not in (rgb("CCCCCC"), rgb("191919"), rgb("1E1E1E"))}
# Tifa's red also appears as 6 stray slots elsewhere in WM3; her model sits in 26000..40000
WORLD_SPAN = {("WORLD/WM3.BSZ", rgb("400000")): (26000, 40000)}
# Those three colors recolor only inside the owning model's WM3 span: Barret hair, Vincent hair, Cait's moogle bones (cat sits in 72800..75216)
WORLD_ONLY = {
	rgb("1E1E1E"): (rgb("E6C34A"), ((21900, 22800),)),
	rgb("191919"): (rgb("A8222E"), ((78100, 81200),)),
	rgb("CCCCCC"): (rgb("F5A0B8"), ((67400, 70600), (75216, 76100))),
}


def recolor_world(dec: bytes, path: str) -> tuple[bytes, int]:
	out = bytearray(dec)
	changed = 0
	for o in range(0, len(dec) - 3, 4):
		src = tuple(dec[o : o + 3])
		dst = WORLD_MAP.get(src)
		if dst is None:
			only = WORLD_ONLY.get(src)
			if only and path == "WORLD/WM3.BSZ" and any(lo <= o < hi for lo, hi in only[1]):
				out[o : o + 3] = bytes(only[0])
				changed += 1
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
	counts["battle CLOUD outfit"] = _patch(img, "ENEMY6/CLOUD.LZS", recolor_battle_cloud)
	for name, rules in BATTLE.items():
		fn = recolor_barrett if rules is _BARRETT else lambda d, r=rules: recolor_battle(d, r)
		counts[f"battle {name}"] = _patch(img, f"ENEMY6/{name}.LZS", fn)
	for path in WORLD_PATHS:
		counts[path] = _patch(img, path, lambda d, p=path: recolor_world(d, p))
	return counts


if __name__ == "__main__":
	src, dst = Path(sys.argv[1]), Path(sys.argv[2])
	buf = bytearray(src.read_bytes())
	for k, v in apply_patch(buf).items():
		print(f"{k:16}{v}")
	dst.write_bytes(buf)
