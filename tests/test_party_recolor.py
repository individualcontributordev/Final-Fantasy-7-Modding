from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mods" / "party-recolor" / "scripts"))

import apply_party_recolor as P


class PartyRecolorTests(unittest.TestCase):
	def test_world_span_limits_tifa_red_to_her_model(self) -> None:
		red = bytes(P.rgb("400000")) + b"\x00"
		dec = bytearray(40000 + 8)
		dec[0:4] = red  # outside 26000..40000: stray slot, left alone
		dec[26000:26004] = red
		out, n = P.recolor_world(bytes(dec), "WORLD/WM3.BSZ")
		self.assertEqual(n, 1)
		self.assertEqual(out[:3], bytes(P.rgb("400000")))
		self.assertEqual(out[26000:26003], bytes(P.rgb("26A65B")))

	def test_world_models_follow_header_pointers(self) -> None:
		dec = bytearray(24 + 36 * 2)
		struct.pack_into("<II", dec, 12, 2, 0x8010_0018)  # model count, RAM address of file offset 24
		for i, (ptr, nb, np_) in enumerate(((0x8010_0018 + 100, 22, 15), (0x8010_0018 + 200, 25, 16))):
			dec[24 + 36 * i + 2:24 + 36 * i + 4] = bytes((nb, np_))
			struct.pack_into("<I", dec, 24 + 36 * i + 28, ptr)
		(at0, nb0, np0, to_off), (at1, nb1, np1, _) = P.world_models(bytes(dec))
		self.assertEqual(((at0, nb0, np0), (at1, nb1, np1)), ((124, 22, 15), (224, 25, 16)))
		self.assertEqual(to_off(0x8010_0018 + 50), 74)

	def test_world_hair_and_moogle_only_inside_their_spans(self) -> None:
		for src, dst, inside, outside in (("1E1E1E", "E6C34A", 22000, 100), ("191919", "A8222E", 78200, 100), ("CCCCCC", "F5A0B8", 67500, 72800)):
			dec = bytearray(82000)
			for o in (inside, outside):
				dec[o:o + 3] = bytes(P.rgb(src))
			out, n = P.recolor_world(bytes(dec), "WORLD/WM3.BSZ")
			self.assertEqual((n, out[inside:inside + 3], out[outside:outside + 3]), (1, bytes(P.rgb(dst)), bytes(P.rgb(src))), src)

	def test_world_ignores_unaligned_match(self) -> None:
		dec = b"\x00" + bytes(P.rgb("656526")) + b"\x00\x00\x00\x00"
		self.assertEqual(P.recolor_world(dec, "WORLD/WM1.BSZ")[1], 0)

	def test_cloud_world_slots_use_field_color_map(self) -> None:
		src, dst = P.rgb("614977"), P.rgb("9C223A")
		out, n = P.recolor_world(bytes(src) + b"\x00", "WORLD/WM0.BSZ")
		self.assertEqual((n, out[:3]), (1, bytes(dst)))

	def test_cloud_battle_ratio_maps_outfit_blue_to_crimson(self) -> None:
		src, dst = P.rgb("614977"), P.rgb("9C223A")
		with mock.patch.object(P, "battle_color_offsets", lambda d: [0, 4]):
			out, n = P.recolor_battle_cloud(bytes(src) + b"\x00" + bytes([200, 100, 50, 0]))
		self.assertEqual((n, out[:3], out[4:7]), (1, bytes(dst), bytes([200, 100, 50])))

	def test_battle_polys_reads_plain_part(self) -> None:
		dec = bytearray(100)
		struct.pack_into("<I", dec, 4, 8)  # body at 8
		struct.pack_into("<II", dec, 8, 1, 0)  # one bone
		struct.pack_into("<I", dec, 16, 16)  # its part at body + 16 = 24
		struct.pack_into("<I", dec, 24, 24)  # 3 vertices
		for k, y in enumerate((-50, 0, 50)):
			struct.pack_into("<hhh", dec, 28 + k * 8, 0, y, 0)
		struct.pack_into("<H", dec, 60, 1)  # one gouraud tri, records at 64
		struct.pack_into("<HHH", dec, 64, 0, 8, 16)
		dec[75] = 0x30  # gouraud command byte
		self.assertEqual(list(P.battle_polys(bytes(dec))), [(0, [(72, -50, 0), (76, 0, 0), (80, 50, 0)])])

	def test_battle_polys_skips_textured_record_misread_as_triangle(self) -> None:
		dec = bytearray(100)
		struct.pack_into("<I", dec, 4, 8)
		struct.pack_into("<II", dec, 8, 1, 0)
		struct.pack_into("<I", dec, 16, 16)
		struct.pack_into("<I", dec, 24, 24)
		struct.pack_into("<H", dec, 60, 1)  # one "triangle" whose command byte (+11) is a textured sprite, 0x67
		dec[75] = 0x67
		self.assertEqual(list(P.battle_polys(bytes(dec))), [])

	def test_battle_rule_stays_in_its_parts_and_keeps_skin(self) -> None:
		hair, skin = bytes([60, 40, 10]), bytes([200, 140, 120])
		dec = hair + b"\x00" + hair + b"\x00" + skin + b"\x00" + hair + b"\x00" * 9
		polys = [(1, [(0, 0, 0), (4, 0, 0), (8, 0, 0)]), (2, [(12, 0, 0), (16, 0, 0), (20, 0, 0)])]
		rule = P.Rule((15, 45), (173, 0.7, 0, 1), frozenset({1}), sat=(0.6, 1))
		with mock.patch.object(P, "battle_polys", lambda d: iter(polys)):
			out, n = P.recolor_battle(dec, (rule,))
		self.assertEqual(n, 3)  # 2 of 3 corners match, so the skin corner follows the polygon
		self.assertEqual(out[12:15], hair)  # part 2 untouched
		self.assertGreater(out[1], out[0])  # teal: green over red

	def test_battle_minority_match_recolors_only_that_corner(self) -> None:
		hair, skin = bytes([60, 40, 10]), bytes([200, 140, 120])
		dec = hair + b"\x00" + skin + b"\x00" + skin + b"\x00"
		rule = P.Rule((15, 45), (173, 0.7, 0, 1), sat=(0.6, 1))
		with mock.patch.object(P, "battle_polys", lambda d: iter([(0, [(0, 0, 0), (4, 0, 0), (8, 0, 0)])])):
			out, n = P.recolor_battle(dec, (rule,))
		self.assertEqual((n, out[4:12]), (1, dec[4:12]))

	def test_battle_top_cut_picks_upper_vertices(self) -> None:
		brown = bytes([60, 33, 20, 0])
		corners = [(0, 0, -100), (4, 0, -100), (8, 0, 100), (12, 0, 100)]
		with mock.patch.object(P, "battle_polys", lambda d: iter([(2, corners)])):
			out, n = P.recolor_battle(brown * 4, P.BATTLE["BARRETT"][:1])
		self.assertEqual((n, out[8:16]), (2, brown * 2))
		self.assertGreater(out[1], out[2])  # blonde: yellow, not brown-red

	def test_barrett_beard_palette_row_goes_blonde(self) -> None:
		dec = b"xx" + P._BARRETT_CLUT + bytes(20 - 16) + bytes(96)
		out, n = P.recolor_barrett_beard(dec)
		row1 = 2 + 20 + 32
		self.assertEqual((n, out[row1 : row1 + 6]), (2, bytes(6)))  # indices 0-2 untouched
		self.assertNotEqual(out[row1 + 6 : row1 + 10], bytes(4))
		self.assertEqual(P.recolor_barrett_beard(b"none"), (b"none", 0))

	def test_red13_face_texture_blackens_scar_and_eyes_only(self) -> None:
		w = 52 * 2
		dec = bytearray(b"xx" + P._RED_CLUT + bytes(64) + struct.pack("<IHHHH", 12 + w * 170, 320, 0, 52, 170) + b"D" * (w * 170))
		img = 2 + 8 + 76 + 12
		out, n = P.recolor_red13_face(bytes(dec))
		self.assertEqual(out[img + 120 * w + 40], 0x22)  # scar: both nibbles 4 -> 2
		self.assertEqual(out[img + 120 * w + 10], 0x22)  # eye
		self.assertEqual(out[img + 100 * w + 40], 0x44)  # above both
		self.assertEqual(n, 59 * 36 + 55 * 53)

	def test_dress_pass_recolors_other_cloud_models_but_not_zack(self) -> None:
		src = bytes(P.rgb("614977"))
		for model_id, expect in ((0, bytes(P.rgb("9C223A"))), (33, bytes(P.rgb("9C223A"))), (9, src)):
			dec = bytearray(300)
			struct.pack_into("<I", dec, 4, 100)  # models table
			struct.pack_into("<I", dec, 104, 1)  # one model
			h = 116
			struct.pack_into("<HHI", dec, h, model_id, 0, 8)  # skeleton 8 bytes in, 0 bones
			dec[h + 35] = 1
			dec[h + 8:h + 11] = src
			with mock.patch.object(P, "color_offsets", lambda d, f, n: [(0, h + 8, 0)]):
				out, n = P.recolor_dress(bytes(dec))
			self.assertEqual(out[h + 8:h + 11], expect, model_id)

	def test_bike_intro_cloud_hair_silver_outfit_crimson_boots_sword_skin_kept(self) -> None:
		colors = {7: (255, 172, 54), 5: (111, 84, 137), 25: (77, 57, 16), 17: (113, 114, 142), 16: (200, 140, 120)}  # hair, jacket, boots, sword, skin
		dec = bytearray(300)
		struct.pack_into("<I", dec, 4, 100)
		struct.pack_into("<I", dec, 104, 1)
		h = 116
		struct.pack_into("<HHI", dec, h, 0, 0, 8)
		dec[h + 35] = 19
		cols = [(part, h + 8 + 4 * i, 0) for i, part in enumerate(colors)]
		for (part, o, _), c in zip(cols, colors.values()):
			dec[o : o + 3] = bytes(c)
		with mock.patch.object(P, "color_offsets", lambda d, f, n: cols), mock.patch.dict(P.BIKE_INTRO, {(0, 0, 19, 5): P.BIKE_INTRO[(0, 30, 19, 621)]}):
			out, n = P.recolor_dress(bytes(dec))
			self.assertEqual(n, 2)
			by_part = {part: out[o : o + 3] for part, o, _ in cols}
			self.assertEqual(by_part[7], bytes(P.rgb("C7D3E6")))
			self.assertEqual(by_part[5], bytes((round(111 * 156 / 97), round(84 * 34 / 73), round(137 * 58 / 119))))
			for part in (25, 17, 16):
				self.assertEqual(by_part[part], bytes(colors[part]), part)
			self.assertEqual(P.recolor_dress(out)[1], 0)  # second run must find nothing

	def test_snowboard_rider_hair_silver_outfit_crimson_boots_kept(self) -> None:
		dec = bytearray(12 + 28 * 13 + 64 * 13)
		colors = {0: (255, 172, 54), 6: (111, 84, 137), 5: (77, 57, 16)}  # hair, outfit, brown boots
		for obj in range(13):
			pt = 12 + 28 * 13 + 64 * obj - 12  # primitive block, relative to byte 12
			struct.pack_into("<6I", dec, 12 + 28 * obj, 0, 0, 0, 0, pt, 1)
			dec[12 + pt : 12 + pt + 4] = bytes((5, 5, 0, 0x31))
			dec[12 + pt + 4 : 12 + pt + 7] = bytes(colors.get(obj, (1, 1, 1)))
		out, n = P.recolor_snowboard(bytes(dec))
		pix = lambda obj: out[12 + 28 * 13 + 64 * obj + 4 : 12 + 28 * 13 + 64 * obj + 7]
		self.assertEqual(n, 2)
		self.assertEqual(pix(0), bytes(P.rgb("C7D3E6")))
		self.assertEqual(pix(6), bytes((round(111 * 156 / 97), round(84 * 34 / 73), round(137 * 58 / 119))))
		self.assertEqual(pix(5), bytes((77, 57, 16)))

	def test_bike_cloud_hair_silver_outfit_crimson_other_meshes_kept(self) -> None:
		dat = bytearray(0x2600)
		for i, mesh in enumerate((0x1B58, 0x1DB0, 0x24AC)):  # outfit, hair, skin blobs
			struct.pack_into("<I", dat, 4 * i, P.BIKE_BASE + mesh)
			dat[mesh + 8 : mesh + 12] = bytes((0, 1, 2, 0))
			color = (111, 84, 137) if i != 1 else (255, 172, 54)
			dat[mesh + 12 : mesh + 24] = bytes((*color, 0x30) * 3)
		out, n = P.recolor_bike(bytes(dat))
		self.assertEqual(n, 6)
		self.assertEqual(out[0x1B58 + 12 : 0x1B58 + 15], bytes((round(111 * 156 / 97), round(84 * 34 / 73), round(137 * 58 / 119))))
		self.assertEqual(out[0x1DB0 + 12 : 0x1DB0 + 15], bytes(P.rgb("C7D3E6")))
		self.assertEqual(out[0x24AC + 12 : 0x24AC + 24], dat[0x24AC + 12 : 0x24AC + 24])
		self.assertEqual(P.recolor_bike(out)[1], 0)  # second run must find nothing


if __name__ == "__main__":
	unittest.main()
