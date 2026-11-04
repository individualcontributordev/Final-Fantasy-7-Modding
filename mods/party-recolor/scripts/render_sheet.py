"""Render an original-vs-recolored contact sheet of every model the party recolor touches.

    python render_sheet.py [out.png] [bin]       (bin defaults to cache/csr-plus/FINALFANTASY7_D1.bin)

Per character: field model (posed from animation 0), Wall Market dress (Cloud, Tifa, Aerith) and world-map model
(WORLD/WM*.BSZ, posed from its first animation) and the battle model's changed parts (ENEMY6, one by one and unposed: the
battle animations are not decoded; textured heads are not drawn). Each pair is original | recolored, run through the mod's own
recolor functions so the sheet cannot drift from them.
"""
from __future__ import annotations

import math
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

_ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(_ROOT / "scripts"), str(Path(__file__).parent)]
import apply_party_recolor as P  # noqa: E402
from psx_mode2_iso import extract_file  # noqa: E402

BG = (40, 44, 52)
TEXT = (230, 230, 230)


def R(axis: int, a: float):
	c, s = math.cos(a), math.sin(a)
	return np.array([[[1, 0, 0], [0, c, -s], [0, s, c]], [[c, 0, s], [0, 1, 0], [-s, 0, c]], [[c, -s, 0], [s, c, 0], [0, 0, 1]]][axis])


class Model:
	"""bones [(length, parent)], parts [(bone, verts, polys)], optional animation 0 (frame pointer)."""

	def __init__(self, dec: bytes, bones_at: int, nb: int, np_: int, to_off=lambda p: p & 0x7FFFFFFF, anims: bool = True):
		self.dec, self.to_off = dec, to_off
		self.bones = [struct.unpack_from("<hB", dec, bones_at + 4 * i) for i in range(nb)]
		first = bones_at + nb * 4
		self.parts = []
		for i in range(np_):
			h = P.PART_HDR.unpack_from(dec, first + i * 32)
			base = to_off(h[19])
			verts = np.array([struct.unpack_from("<hhh", dec, base + 4 + 8 * k) for k in range(h[2])], float).reshape(-1, 3)
			pos, polys = base + h[14], []
			for ci, size, cols in P.KINDS:
				for _ in range(h[ci]):
					quad = ci in (4, 6, 9, 11)
					idx = list(dec[pos : pos + (4 if quad else 3)])
					cs = [tuple(dec[pos + 4 + 4 * k : pos + 7 + 4 * k]) for k in range(cols[0][1])]
					polys.append((idx, cs, quad))
					pos += size
			self.parts.append((h[1], verts, polys))
		a = first + np_ * 32  # some models (world Barret) start with an empty stub animation: take the first real one
		while dec[a + 2] != nb and dec[a + 2 + 16 * 8:a + 3 + 16 * 8] and a < first + np_ * 32 + 16 * 8:
			a += 16
		self.anim = a if anims else None

	def rotations(self, frame: int = 0):
		"""Per-bone (x, y, z) angles of one frame; a flagged axis byte indexes a per-frame stream (Makou BsxFile::readAnimation)."""
		dec = self.dec
		frames, = struct.unpack_from("<H", dec, self.anim)
		off_rot, = struct.unpack_from("<H", dec, self.anim + 10)
		data = self.to_off(struct.unpack_from("<I", dec, self.anim + 12)[0])
		out = []
		for j in range(len(self.bones)):
			rec = data + 4 + 8 * j
			flag = dec[rec]
			out.append([2 * math.pi * (dec[data + off_rot + dec[rec + 1 + k] * frames + frame] if flag >> k & 1 else dec[rec + 1 + k]) / 256 for k in range(3)])
		return out

	def pose(self):
		pos, rot = [None] * len(self.bones), [None] * len(self.bones)
		for j, ((length, parent), a) in enumerate(zip(self.bones, self.rotations())):
			local = R(1, a[1]) @ R(0, a[0]) @ R(2, a[2])
			if parent in (255, j):
				rot[j], pos[j] = local, np.zeros(3)
			else:
				rot[j] = rot[parent] @ local
				pos[j] = pos[parent] + rot[parent] @ np.array([0, 0, length], float)
		return pos, rot

	def posed(self, yaw: float = 0):
		"""(depth, screen points, color) of every polygon of the model standing up."""
		pos, rot = self.pose()
		up = np.array([0, -1.0, 0])  # bones hang along -y in animation 0
		v = np.cross(up, [0, 0, 1.0])
		K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
		M = R(2, math.radians(yaw)) @ (np.eye(3) + K + K @ K / (1 + up[2]))
		return self._polys(lambda b, vs: (M @ (rot[b] @ vs.T)).T + M @ pos[b], lambda p: (p[0], -p[2]), 1)

	def part(self, i: int):
		"""One part in its own coordinates (z hangs down), for models without a skeleton."""
		bone, verts, polys = self.parts[i]
		return self._polys(lambda b, vs: vs, lambda p: (p[0], p[2]), 1, only=i)

	def _polys(self, place, screen, depth, only=None):
		out = []
		for i, (bone, verts, polys) in enumerate(self.parts):
			if only not in (None, i) or not len(verts):
				continue
			w = place(bone, verts)
			for idx, cs, quad in polys:
				if max(idx) >= len(w):
					continue
				col = tuple(int(sum(c[k] for c in cs) / len(cs)) for k in range(3))
				order = [0, 1, 3, 2] if quad else [0, 1, 2]
				out.append((np.mean([w[i][depth] for i in idx]), [screen(w[idx[o]]) for o in order], col))
		return out


def draw(polys, size, ext):
	img = Image.new("RGB", size, BG)
	d = ImageDraw.Draw(img)
	x0, x1, y0, y1 = ext
	sc = min(size[0] * 0.9 / max(x1 - x0, 1), size[1] * 0.9 / max(y1 - y0, 1))
	for _, pts, col in sorted(polys, key=lambda t: -t[0]):
		d.polygon([(size[0] / 2 + (x - (x0 + x1) / 2) * sc, size[1] / 2 + (y - (y0 + y1) / 2) * sc) for x, y in pts], fill=col)
	return img


def extent(polys):
	xs = [x for _, p, _ in polys for x, _ in p]
	ys = [y for _, p, _ in polys for _, y in p]
	return min(xs), max(xs), min(ys), max(ys)


def bcx(dec):
	om = struct.unpack_from("<I", dec, 4)[0]
	return Model(dec, om + P.HDR_SIZE, dec[om + 2], dec[om + 3])


def bsx_dresses(dec):
	"""{(model id, bones, parts, colors): Model} for each model of a field BSX, only the ones the mod has a map for."""
	out = {}
	om = struct.unpack_from("<I", dec, 4)[0]
	for i in range(struct.unpack_from("<I", dec, om + 4)[0]):
		h = om + 16 + 48 * i
		mid, _, skel = struct.unpack_from("<HHI", dec, h)
		nb, npart = dec[h + 23], dec[h + 35]
		colors = sum(1 for _ in P.color_offsets(dec, h + skel + nb * 4, npart))
		if (mid, nb, npart, colors) in P.DRESS:
			out[(mid, nb, npart, colors)] = Model(dec, h + skel, nb, npart)
	return out


BATTLE_CELL = 76, 100


def battle_parts(dec, new):
	"""[(part index, original polys, recolored polys)] for the parts whose colors the recolor changed, each upright in its own coordinates."""
	orig, recol = {}, {}
	for i, corners, p, r in P.battle_polys(dec, True):
		n = 4 if len(corners) == 4 else 3
		idx = [struct.unpack_from("<H", dec, r + 2 * j)[0] for j in range(n)]
		vs = [struct.unpack_from("<hhh", dec, p + 4 + k) for k in idx]
		order = [0, 1, 3, 2] if n == 4 else [0, 1, 2]
		for src, out in ((dec, orig), (new, recol)):
			col = tuple(int(sum(src[o + c] for o, *_ in corners) / n) for c in range(3))
			out.setdefault(i, []).append((sum(v[1] for v in vs) / n, [(vs[o][0], -vs[o][2]) for o in order], col))
	return [(i, orig[i], recol[i]) for i in orig if orig[i] != recol[i]]


def label(d, x, y, text):
	d.text((x, y), text, fill=TEXT)


# character -> (field BCX, Wall Market dress model id, [(world file, model index)])
CHARS = {
	"Cloud": ("CLOUD", 0, [("WM0", 0), ("WM3", 0)]),
	"Barret": ("BALLET", None, [("WM3", 1)]),
	"Tifa": ("TIFA", 3, [("WM1", 0), ("WM3", 2)]),
	"Aerith": ("EARITH", 1, [("WM3", 3)]),
	"Red XIII": ("RED", None, [("WM3", 4)]),
	"Yuffie": ("YUFI", None, [("WM3", 5)]),
	"Cait Sith": ("KETCY", None, [("WM3", 6)]),
	"Vincent": ("VINCENT", None, [("WM3", 7)]),
	"Cid": ("CID", None, [("WM2", 0), ("WM3", 8)]),
}
CELL = 170, 250
battle = {"Cloud": "CLOUD", "Barret": "BARRETT", "Tifa": "TIFA", "Aerith": "EARITH", "Red XIII": "RED13", "Yuffie": "YUFI", "Cait Sith": "KETCY", "Vincent": "VINSENT", "Cid": "CID"}  # battle file name prefixes


def pair(a: Model, b: Model):
	pa, pb = a.posed(), b.posed()
	ext = extent(pa)  # shared so both panels line up
	return draw(pa, CELL, ext), draw(pb, CELL, ext)


def build(img) -> Image.Image:
	world = {}
	for path in P.WORLD_PATHS:
		dec = P.lzs.decompress(extract_file(img, path))
		new = P.recolor_world(dec, path)[0]
		world[path[6:9]] = [[Model(d, a, nb, np_, f) for a, nb, np_, f in P.world_models(d)] for d in (dec, new)]
	dec = P.lzs.decompress(extract_file(img, "FIELD/COLNE_6.BSX"))
	dress = bsx_dresses(dec), bsx_dresses(P.recolor_dress(dec)[0])
	rows = []  # (character, [(caption, original, recolored)])
	for name, (field, dress_id, wm) in CHARS.items():
		d = P.lzs.decompress(extract_file(img, f"FIELD/{field}.BCX"))
		cells = [("Field model", *pair(bcx(d), bcx(P.recolor(d, P.FIELD[field], P.FIELD_ONLY.get(field))[0])))]
		for key, m in dress[0].items():
			if key[0] == dress_id:
				cells.append(("Wall Market dress", *pair(m, dress[1][key])))
		for f, i in wm:
			cells.append((f"World map ({f})", *pair(world[f][0][i], world[f][1][i])))
		parts = []
		for bname in [n for n in P.BATTLE if n.startswith(battle[name])][:1]:
			b = P.lzs.decompress(extract_file(img, f"ENEMY6/{bname}.LZS"))
			new = b
			for fn in ([P.recolor_battle_cloud] if bname == "CLOUD" else []) + [P.battle_fn(bname)]:
				new = fn(new)[0]
			assert len(new) == len(b)
			parts += [(bname, i, *rest) for i, *rest in battle_parts(b, new)]
		rows.append((name, cells, parts))
	w, h = CELL
	bw, bh = BATTLE_CELL
	per = (4 * (2 * w + 16)) // (2 * bw + 8)
	top, bat = 26, lambda n: -(-len(n) // per) * (bh + 18) + 18 if n else 0
	heights = [top + 18 + h + bat(parts) + 14 for _, _, parts in rows]
	sheet = Image.new("RGB", (4 * (2 * w + 16) + 16, sum(heights)), BG)
	d = ImageDraw.Draw(sheet)
	y = 0
	for (name, cells, parts), rh in zip(rows, heights):
		d.text((8, y + 6), f"{name.upper()}   (left: original, right: recolored)", fill=TEXT)
		for c, (cap, a, b) in enumerate(cells):
			x = 8 + c * (2 * w + 16)
			d.text((x, y + top), cap, fill=TEXT)
			sheet.paste(a, (x, y + top + 16))
			sheet.paste(b, (x + w, y + top + 16))
		if parts:
			by = y + top + 18 + h
			d.text((8, by), "Battle model parts (unposed; file, part index)", fill=TEXT)
			for k, (bname, i, a, b) in enumerate(parts):
				x, yy = 8 + k % per * (2 * bw + 8), by + 18 + k // per * (bh + 18)
				ext = extent(a)
				d.text((x, yy), f"{bname} {i}", fill=TEXT)
				sheet.paste(draw(a, BATTLE_CELL, ext), (x, yy + 14))
				sheet.paste(draw(b, BATTLE_CELL, ext), (x + bw, yy + 14))
		y += rh
	return sheet


if __name__ == "__main__":
	out = sys.argv[1] if len(sys.argv) > 1 else "recolor_sheet.png"
	src = Path(sys.argv[2]) if len(sys.argv) > 2 else _ROOT / "cache/csr-plus/FINALFANTASY7_D1.bin"
	build(bytearray(src.read_bytes())).save(out)
	print("wrote", out)
