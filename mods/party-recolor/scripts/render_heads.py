#!/usr/bin/env python3
"""Front and side views of every party member's battle-model head, original next to recolor.

    python render_heads.py OUT.png [BIN]

BIN defaults to the CSR+ disc 1. The head is the textured part with the most vertices. Textured
triangles use the model's own 4bpp TIM; vertex-colored polygons use the colors the recolor changes.
The recolor never touches the texture, so skin, eyes and mouth look identical in both columns."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

_ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(_ROOT / "scripts"), str(Path(__file__).resolve().parent)]

import apply_party_recolor as P  # noqa: E402
from psx_mode2_iso import extract_file  # noqa: E402

BG, TEXT = (40, 44, 52), (230, 230, 230)
NAMES = {"Cloud": "CLOUD", "Barret": "BARRETT", "Tifa": "TIFA", "Aerith": "EARITH", "Red XIII": "RED13",
	"Yuffie": "YUFI", "Cait Sith": "KETCY", "Vincent": "VINSENT", "Cid": "CID"}
CELL, SC = 190, 3  # cell size; supersampling for the flat polygons


def tim(dec):
	"""(palettes, 4bpp pixel array) of the model's TIM; palette rows start at VRAM y 480."""
	for o in range(len(dec) - 20):
		if dec[o:o + 8] != b"\x10\0\0\0\x08\0\0\0":
			continue
		cl = struct.unpack_from("<I", dec, o + 8)[0]  # false hits fail the image-size check
		if 12 <= cl < 2000 and o + 8 + cl + 12 <= len(dec):
			ib = o + 8 + cl
			isz, _, _, w, h = struct.unpack_from("<IHHHH", dec, ib)
			if isz == w * h * 2 + 12:
				break
	cw, ch = struct.unpack_from("<HH", dec, o + 16)
	pal = np.frombuffer(dec, "<u2", cw * ch, o + 20).reshape(ch, cw)
	words = np.frombuffer(dec, "<u2", w * h, ib + 12).reshape(h, w)
	return pal, np.stack([(words >> (4 * k)) & 15 for k in range(4)], -1).reshape(h, w * 4)


def head_polys(dec, pal, tex):
	"""[(depth axes, vertices, color or texel sampler)] in model space for the largest textured part."""
	body = struct.unpack_from("<I", dec, 4)[0]
	n = struct.unpack_from("<I", dec, body)[0]
	parts = sorted({struct.unpack_from("<I", dec, body + 8 + i * 8)[0] for i in range(n)} - {0})
	best = None
	for i, off in enumerate(parts):
		p = body + off
		v = struct.unpack_from("<I", dec, p)[0]
		if struct.unpack_from("<H", dec, p + 4 + v)[0] and (best is None or v > best[1]):
			best = (i, v, p)
	i, v, p = best
	vert = lambda k: struct.unpack_from("<hhh", dec, p + 4 + k)
	ntex = struct.unpack_from("<H", dec, p + 4 + v)[0]
	out = []
	for r in range(p + 4 + v + 12, p + 4 + v + 12 + ntex * 16, 16):
		idx = struct.unpack_from("<3H", dec, r + 8)
		if any(k % 8 or k >= v for k in idx) or dec[r + 3] != 0x78:  # the 11th "record" is a count, not a polygon
			continue
		uv = [dec[r], dec[r + 1]], [dec[r + 4], dec[r + 5]], [dec[r + 6], dec[r + 7]]
		row = (struct.unpack_from("<H", dec, r + 2)[0] >> 6) - 480
		out.append(([vert(k) for k in idx], (uv, pal[row])))
	for _, corners, pp, r in P.battle_polys(dec, True):
		if pp != p:
			continue
		nv = len(corners)
		vs = [vert(struct.unpack_from("<H", dec, r + 2 * j)[0]) for j in range(nv)]
		col = tuple(int(sum(dec[o + c] for o, *_ in corners) / nv) for c in range(3))
		out.append((vs if nv == 3 else [vs[0], vs[1], vs[3], vs[2]], col))
	return out


def view(polys, ax, ay, ad, fx, sign):
	"""Painter's-order render: screen x = fx * v[ax], screen y = v[ay] (the head hangs from its joint at -z, so +z is down), larger sign * v[ad] is nearer."""
	pts = [np.array([[fx * v[ax], v[ay]] for v in vs], float) for vs, _ in polys]
	allp = np.concatenate(pts)
	lo, hi = allp.min(0), allp.max(0)
	s = (CELL - 16) * SC / max(*(hi - lo))
	big = Image.new("RGB", (CELL * SC, CELL * SC), BG)
	draw = ImageDraw.Draw(big)
	px = big.load()
	off = (CELL * SC - (hi - lo) * s) / 2
	for (vs, paint), pt in sorted(zip(polys, pts), key=lambda t: sign * sum(v[ad] for v in t[0][0])):
		xy = (pt - lo) * s + off
		if isinstance(paint, tuple) and len(paint) == 3:
			draw.polygon([tuple(q) for q in xy], fill=paint)
			continue
		uv, pal = paint
		a, b, c = xy
		d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
		if abs(d) < 1e-6:
			continue
		for y in range(int(xy[:, 1].min()), int(xy[:, 1].max()) + 1):
			for x in range(int(xy[:, 0].min()), int(xy[:, 0].max()) + 1):
				l1 = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / d
				l2 = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / d
				l3 = 1 - l1 - l2
				if min(l1, l2, l3) < -0.02:
					continue
				u = int(round(l1 * uv[0][0] + l2 * uv[1][0] + l3 * uv[2][0]))
				w = int(round(l1 * uv[0][1] + l2 * uv[1][1] + l3 * uv[2][1]))
				ci = pal[TEX[min(max(w, 0), TEX.shape[0] - 1), min(max(u, 0), TEX.shape[1] - 1)]]
				if ci and 0 <= x < big.width and 0 <= y < big.height:
					px[x, y] = ((ci & 31) * 255 // 31, (ci >> 5 & 31) * 255 // 31, (ci >> 10 & 31) * 255 // 31)
	return big.resize((CELL, CELL), Image.LANCZOS)


def build(img):
	global TEX
	sheet = Image.new("RGB", (CELL * 4 + 90, CELL * len(NAMES) + 24), BG)
	d = ImageDraw.Draw(sheet)
	for c, t in enumerate(("original front", "original side", "recolor front", "recolor side")):
		d.text((90 + c * CELL + 6, 6), t, fill=TEXT)
	for row, (who, fn) in enumerate(NAMES.items()):
		dec = P.lzs.decompress(extract_file(img, f"ENEMY6/{fn}.LZS"))
		new = P.battle_fn(fn)(dec)[0]
		pal, TEX = tim(dec)
		y = 24 + row * CELL
		d.text((6, y + CELL // 2), who, fill=TEXT)
		for k, m in enumerate((dec, new)):
			polys = head_polys(m, pal, TEX)
			sheet.paste(view(polys, 0, 2, 1, -1, 1), (90 + 2 * k * CELL, y))  # front: face at +y, 180 deg turn keeps it unmirrored
			sheet.paste(view(polys, 1, 2, 0, 1, -1), (90 + (2 * k + 1) * CELL, y))  # side: face points right, viewed from -x
	return sheet


if __name__ == "__main__":
	src = Path(sys.argv[2]) if len(sys.argv) > 2 else _ROOT / "cache" / "csr-plus" / "FINALFANTASY7_D1.bin"
	build(bytearray(src.read_bytes())).save(sys.argv[1])
