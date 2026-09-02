from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FANFARE_SCRIPTS = ROOT / "mods" / "fanfare-skip" / "scripts"
sys.path.insert(0, str(FANFARE_SCRIPTS))

from apply_fanfare_skip import apply_patch, load_sites, verify


class FanfareSkipPatchTests(unittest.TestCase):
	def make_retail_payload(self) -> bytearray:
		payload = bytearray(6460)
		for offset, original, _replacement in load_sites():
			payload[offset : offset + len(original)] = original
		return payload

	def test_applies_all_playtested_batres_changes(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory) / "BATRES.X.dec"
			retail = self.make_retail_payload()
			path.write_bytes(retail)

			self.assertEqual(apply_patch(path), 5)
			verify(path)

			patched = path.read_bytes()
			changed = sum(a != b for a, b in zip(retail, patched))
			self.assertEqual(changed, 11)

			# Republishing must be safe when the payload is already patched.
			self.assertEqual(apply_patch(path), 5)
			self.assertEqual(path.read_bytes(), patched)

	def test_rejects_an_unknown_batres_payload(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory) / "BATRES.X.dec"
			payload = self.make_retail_payload()
			offset, _original, _replacement = load_sites()[0]
			payload[offset] ^= 0xFF
			path.write_bytes(payload)

			with self.assertRaises(SystemExit) as error:
				apply_patch(path)

			self.assertIn("unexpected bytes", str(error.exception))


if __name__ == "__main__":
	unittest.main()
