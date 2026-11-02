from __future__ import annotations

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

	def test_battle_rotates_hue_inside_band_only(self) -> None:
		# olive (hue ~63) is inside Barret's band, skin (hue ~20) is not
		dec = bytes([100, 100, 20, 0, 200, 140, 120, 0])
		with mock.patch.object(P, "battle_color_offsets", lambda d: [0, 4]):
			out, n = P.recolor_battle(dec, P.BATTLE["BARRETT"])
		self.assertEqual(n, 1)
		r, g, b = out[:3]
		self.assertGreater(b, r)  # olive -> blue
		self.assertEqual(out[4:7], dec[4:7])


if __name__ == "__main__":
	unittest.main()
