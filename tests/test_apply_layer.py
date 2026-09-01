from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_layer import apply_layer  # noqa: E402

SECTOR = 2352


class ApplyLayerTests(unittest.TestCase):
	def test_pads_to_modified_size_when_baseline_matches(self) -> None:
		base = bytearray(10 * SECTOR)
		target = 12 * SECTOR
		layer = {
			"format": "ic-layer-v1",
			"stats": {"originalBytes": len(base), "modifiedBytes": target},
			"records": [{"offset": 10 * SECTOR - 4, "hex": "deadbeef"}],
		}

		apply_layer(base, layer)

		self.assertEqual(len(base), target)
		self.assertEqual(base[10 * SECTOR - 4 : 10 * SECTOR], bytes.fromhex("deadbeef"))

	def test_aligns_records_to_a_sector(self) -> None:
		base = bytearray(8 * SECTOR)
		offset = 8 * SECTOR + 100
		layer = {
			"format": "ic-layer-v1",
			"stats": {"originalBytes": len(base), "modifiedBytes": offset + 3},
			"records": [{"offset": offset, "hex": "aabbcc"}],
		}

		apply_layer(base, layer)

		self.assertEqual(base[offset : offset + 3], bytes.fromhex("aabbcc"))
		self.assertEqual(len(base) % SECTOR, 0)

	def test_ignores_size_from_another_baseline(self) -> None:
		base = bytearray(5 * SECTOR)
		layer = {
			"format": "ic-layer-v1",
			"stats": {
				"originalBytes": 99 * SECTOR,
				"modifiedBytes": 200 * SECTOR,
			},
			"records": [{"offset": 10, "hex": "11"}],
		}

		apply_layer(base, layer)

		self.assertEqual(base[10], 0x11)
		self.assertEqual(len(base), 5 * SECTOR)

	def test_rejects_bad_format(self) -> None:
		with self.assertRaises(SystemExit):
			apply_layer(bytearray(SECTOR), {"format": "nope", "records": []})


if __name__ == "__main__":
	unittest.main()
