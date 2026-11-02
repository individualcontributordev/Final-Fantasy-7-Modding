from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mods" / "cloud-recolor" / "scripts"))

from apply_cloud_recolor import BATTLE_RATIO, COLOR_MAP, recolor_world


class CloudRecolorTests(unittest.TestCase):
	def test_world_recolor_hits_aligned_outfit_slots_only(self) -> None:
		(src, dst), = COLOR_MAP.items()
		dec = bytes(src) + b"\x72" + bytes(range(8)) + bytes(src) + b"\x01"  # slots at 0 and 12; 4+5 is unaligned noise
		noise = b"\x00" + bytes(src) + b"\x00\x00\x00\x00"  # outfit bytes at offset 1: not a slot
		out, n = recolor_world(dec + noise)
		self.assertEqual(n, 2)
		self.assertEqual(out[:3], bytes(dst))
		self.assertEqual(out[12:15], bytes(dst))
		self.assertEqual(out[len(dec) + 1 : len(dec) + 4], bytes(src))

	def test_battle_ratio_maps_outfit_blue_to_crimson(self) -> None:
		(src, dst), = COLOR_MAP.items()
		self.assertEqual(tuple(round(v * k) for v, k in zip(src, BATTLE_RATIO)), dst)


if __name__ == "__main__":
	unittest.main()
