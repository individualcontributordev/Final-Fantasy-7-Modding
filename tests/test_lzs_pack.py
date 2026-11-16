import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import lzs_pack


class LzsPackTests(unittest.TestCase):
    def test_round_trips(self) -> None:
        data = bytes(range(256)) * 20 + b"abcabcabcabc" * 50 + bytes(300)
        self.assertEqual(lzs_pack.decompress(lzs_pack.compress(data)), data)


if __name__ == "__main__":
    unittest.main()
