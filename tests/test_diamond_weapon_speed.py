from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mods" / "diamond-weapon-speed-up" / "scripts"))

from patch_disc import (
    ARRIVAL_CMP_OFFSET,
    OPCODE_EQ,
    OPCODE_GE,
    SPEED_OFFSETS,
    STEP_OFFSET,
    VANILLA_SPEEDS,
    VANILLA_STEP,
    patch_worldscript,
)

EV_SIZE = 0x7800


def vanilla_ev() -> bytes:
    """A WM0.EV-sized buffer carrying only the words this patch touches."""
    data = bytearray(EV_SIZE)
    struct.pack_into("<H", data, STEP_OFFSET, VANILLA_STEP)
    struct.pack_into("<H", data, ARRIVAL_CMP_OFFSET, OPCODE_EQ)
    for offset, speed in VANILLA_SPEEDS.items():
        struct.pack_into("<H", data, offset, speed)
    return bytes(data)


def word(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


class PatchWorldscriptTests(unittest.TestCase):
    def test_scales_step_and_speeds(self) -> None:
        out = patch_worldscript(vanilla_ev(), step=4, speed_mult=4)

        self.assertEqual(word(out, STEP_OFFSET), 4)
        self.assertEqual(word(out, 0x3AA8), 32)
        self.assertEqual(word(out, 0x3AD6), 4)
        self.assertEqual(len(out), EV_SIZE)

    def test_arrival_compare_becomes_ge_when_stepping_over_it(self) -> None:
        out = patch_worldscript(vanilla_ev(), step=4, speed_mult=4)
        self.assertEqual(word(out, ARRIVAL_CMP_OFFSET), OPCODE_GE)

    def test_arrival_compare_stays_eq_at_step_one(self) -> None:
        out = patch_worldscript(vanilla_ev(), step=1, speed_mult=2)
        self.assertEqual(word(out, ARRIVAL_CMP_OFFSET), OPCODE_EQ)

    def test_speed_is_clamped_to_a_byte(self) -> None:
        out = patch_worldscript(vanilla_ev(), step=4, speed_mult=64)
        self.assertEqual(word(out, 0x3AA8), 255)

    def test_rerunning_the_same_patch_is_allowed(self) -> None:
        once = patch_worldscript(vanilla_ev(), step=4, speed_mult=4)
        twice = patch_worldscript(once, step=4, speed_mult=4)
        self.assertEqual(once, twice)

    def test_unexpected_bytes_are_refused(self) -> None:
        data = bytearray(vanilla_ev())
        struct.pack_into("<H", data, SPEED_OFFSETS[0], 0x1234)

        with self.assertRaises(SystemExit) as raised:
            patch_worldscript(bytes(data), step=4, speed_mult=4)

        self.assertIn("0x1234", str(raised.exception))

    def test_short_file_is_refused(self) -> None:
        with self.assertRaises(SystemExit):
            patch_worldscript(b"\x00" * 64, step=4, speed_mult=4)


if __name__ == "__main__":
    unittest.main()
