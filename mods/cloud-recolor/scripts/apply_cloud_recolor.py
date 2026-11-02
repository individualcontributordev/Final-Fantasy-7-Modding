#!/usr/bin/env python3
"""Recolor Cloud's field model: SOLDIER blue outfit -> crimson.

FIELD/CLOUD.BCX is LZS and holds no textures; every polygon carries its own RGBA.
Walk the part headers, remap exact RGB matches, recompress to the same ISO slot.
Face textures (FIELD.TDB), hair, skin, belt and boots are left alone."""

from __future__ import annotations

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

BCX_PATH = "FIELD/CLOUD.BCX"
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

# exact RGB -> RGB; every polygon of that color in the retail model is rewritten
COLOR_MAP = {
	(0x61, 0x49, 0x77): (0x9C, 0x22, 0x3A),  # outfit blue -> crimson
}


def color_offsets(dec: bytes):
	"""Absolute offset of every polygon RGB triple in the decompressed BCX."""
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
						yield pos + off + k * 4
				pos += size


def recolor(dec: bytes) -> tuple[bytes, int]:
	out = bytearray(dec)
	changed = 0
	for o in color_offsets(dec):
		new = COLOR_MAP.get(tuple(dec[o : o + 3]))
		if new:
			out[o : o + 3] = bytes(new)
			changed += 1
	return bytes(out), changed


# --- battle model: ENEMY6/CLOUD.LZS = u32 bone count, 8-byte bones {u16 parent, s16 len, u32 part offset},
# parts: u32 vertex bytes, vertices, 12-byte header (u16 tri count at +8), 20-byte tri records, u32 quad
# count, 24-byte quad records; each record = 8 bytes of vertex indices then one RGBA per vertex.
# Colors are not exact (battle shading), so outfit tones = cool (b >= r, b > g), scaled toward crimson.
BATTLE_PATH = "ENEMY6/CLOUD.LZS"
BATTLE_BODY = 0x1C8  # bone table starts here; parts whose walk does not end at the next part (textured head) are skipped
BATTLE_RATIO = tuple(n / o for n, o in zip(COLOR_MAP[(0x61, 0x49, 0x77)], (0x61, 0x49, 0x77)))

def battle_color_offsets(dec: bytes):
	n = struct.unpack_from("<I", dec, BATTLE_BODY)[0]
	parts = sorted({struct.unpack_from("<I", dec, BATTLE_BODY + 8 + i * 8)[0] for i in range(n)} - {0})
	for i, part in enumerate(parts):
		p = BATTLE_BODY + part
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
		if i + 1 < len(parts) and p != BATTLE_BODY + parts[i + 1]:
			continue
		yield from recs

def recolor_battle(dec: bytes) -> tuple[bytes, int]:
	out = bytearray(dec)
	changed = 0
	for o in battle_color_offsets(dec):
		r, g, b = dec[o : o + 3]
		if b >= r and b > g:
			out[o : o + 3] = bytes(min(255, round(v * k)) for v, k in zip((r, g, b), BATTLE_RATIO))
			changed += 1
	return bytes(out), changed

# --- world map: WORLD/WM0.BSZ and WM3.BSZ embed Cloud's field-style model with 4-aligned RGB+pad slots
WORLD_PATHS = ("WORLD/WM0.BSZ", "WORLD/WM3.BSZ")

def recolor_world(dec: bytes) -> tuple[bytes, int]:
	"""Rewrite every 4-aligned outfit-blue slot (the only 295 hits; hair/skin/boots differ)."""
	(src, dst), = COLOR_MAP.items()
	out = bytearray(dec)
	changed = 0
	for o in range(0, len(dec) - 3, 4):
		if tuple(dec[o : o + 3]) == src:
			out[o : o + 3] = bytes(dst)
			changed += 1
	return bytes(out), changed

def apply_patch(img: bytearray) -> tuple[int, ...]:
	"""Patch the disc image in place; return polygon colors rewritten per model (field, battle, world...)."""
	counts = []
	for path, fn in ((BCX_PATH, recolor), (BATTLE_PATH, recolor_battle), *((w, recolor_world) for w in WORLD_PATHS)):
		new, changed = fn(lzs.decompress(extract_file(img, path)))
		if not changed:
			raise SystemExit(f"{path}: nothing to recolor -- already patched or wrong base?")
		replace_file_padded(img, path, lzs.compress(new))
		counts.append(changed)
	return tuple(counts)


if __name__ == "__main__":
	src, dst = Path(sys.argv[1]), Path(sys.argv[2])
	buf = bytearray(src.read_bytes())
	print("recolored polygon colors (field, battle, WM0, WM3):", apply_patch(buf))
	dst.write_bytes(buf)
