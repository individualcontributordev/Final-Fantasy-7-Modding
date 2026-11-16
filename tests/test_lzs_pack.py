import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import lzs_pack


class LzsPackTests(unittest.TestCase):
    def test_round_trips(self) -> None:
        data = bytes(range(256)) * 20 + b"abcabcabcabc" * 50 + bytes(300)
        self.assertEqual(lzs_pack.decompress(lzs_pack.compress(data)), data)

    def test_never_references_before_the_start(self) -> None:
        for data in (bytes(500), b"\0\0\0\1" * 300, bytes(range(256)) * 20 + bytes(300)):
            lzs_pack.decompress(lzs_pack.compress(data))  # the decoder tolerates only retail's short reach

    def test_decoder_rejects_pre_start_reference(self) -> None:
        stream = bytes((0b11111110,)) + b"abcdefg" + bytes((0, 0))  # 7 literals, then a reference 4078 bytes before the start
        stream = len(stream).to_bytes(4, "little") + stream
        with self.assertRaises(ValueError):
            lzs_pack.decompress(stream)


if __name__ == "__main__":
    unittest.main()
