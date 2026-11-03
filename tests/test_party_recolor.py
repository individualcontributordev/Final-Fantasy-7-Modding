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
		self.assertEqual(out[26000:26003], bytes(P.rgb("0F4A50")))

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
		self.assertEqual(list(P.battle_polys(bytes(dec))), [(0, [(72, -50), (76, 0), (80, 50)])])

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
		polys = [(1, [(0, 0), (4, 0), (8, 0)]), (2, [(12, 0), (16, 0), (20, 0)])]
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
		with mock.patch.object(P, "battle_polys", lambda d: iter([(0, [(0, 0), (4, 0), (8, 0)])])):
			out, n = P.recolor_battle(dec, (rule,))
		self.assertEqual((n, out[4:12]), (1, dec[4:12]))

	def test_battle_top_cut_picks_upper_vertices(self) -> None:
		brown = bytes([90, 50, 30, 0])
		corners = [(0, -100), (4, -100), (8, 100), (12, 100)]
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

if __name__ == "__main__":
	unittest.main()
