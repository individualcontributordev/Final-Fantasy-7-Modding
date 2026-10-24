from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mods" / "diamond-weapon-speed-up" / "scripts"))

import lzs_pack
from patch_disc import (
    ANCHOR_END,
    ANCHOR_START,
    ARRIVAL_CMP_OFFSET,
    OPCODE_EQ,
    OPCODE_GE,
    SPEED_OFFSETS,
    STEP_OFFSET,
    VANILLA_SPEEDS,
    VANILLA_STEP,
    LEG1_END,
    LEG1_SPEED_OFFSET,
    EMERGE_SHIFT_OFFSET,
    POST_THRESHOLDS,
    patch_bundle,
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
    for offset, value in POST_THRESHOLDS.items():
        struct.pack_into("<H", data, offset, value)
    struct.pack_into("<H", data, EMERGE_SHIFT_OFFSET, 1)
    # `savemap[0x390] = 0`, as the script writes it a little past the step site
    data[0x4548:0x4552] = bytes.fromhex("1c01900310010000e000")
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
        self.assertEqual(word(out, 0x3AA8), 127)

    def test_rerunning_the_same_patch_is_allowed(self) -> None:
        once = patch_worldscript(vanilla_ev(), step=4, speed_mult=4)
        twice = patch_worldscript(once, step=4, speed_mult=4)
        self.assertEqual(once, twice)

    def test_leg1_is_shortened_at_equal_distance(self) -> None:
        out = patch_worldscript(vanilla_ev(), step=1, speed_mult=1, leg1_frames=700)

        self.assertEqual(word(out, 0x454E), LEG1_END - 700)
        self.assertEqual(word(out, LEG1_SPEED_OFFSET), 32)
        self.assertEqual(word(out, 0x3AD6), 1)

    def test_leg1_speed_never_exceeds_signed_byte(self) -> None:
        with self.assertRaises(SystemExit):
            patch_worldscript(vanilla_ev(), step=1, speed_mult=1, leg1_frames=100)

    def test_post_turn_stretch_is_halved_at_equal_distance(self) -> None:
        out = patch_worldscript(vanilla_ev(), step=1, speed_mult=1, post_turn_mult=2)

        self.assertEqual(word(out, 0x3B1A), 16)
        self.assertEqual(word(out, 0x3AFA), 0xCD5)
        self.assertEqual(word(out, 0x3B0A), 0xCD4)
        self.assertEqual(word(out, 0x3B76), 0xD84)
        self.assertEqual(word(out, EMERGE_SHIFT_OFFSET), 0)

    def test_final_trim_shortens_only_the_approach_end(self) -> None:
        out = patch_worldscript(vanilla_ev(), step=1, speed_mult=1, post_turn_mult=2, final_trim=100)

        self.assertEqual(word(out, 0x3B76), 0xD84 - 100)
        self.assertEqual(word(out, 0x3B32), 0xD84 - 100)
        self.assertEqual(word(out, 0x3AFA), 0xCD5)

    def test_unexpected_bytes_are_refused(self) -> None:
        data = bytearray(vanilla_ev())
        struct.pack_into("<H", data, SPEED_OFFSETS[0], 0x1234)

        with self.assertRaises(SystemExit) as raised:
            patch_worldscript(bytes(data), step=4, speed_mult=4)

        self.assertIn("0x1234", str(raised.exception))

    def test_short_file_is_refused(self) -> None:
        with self.assertRaises(SystemExit):
            patch_worldscript(b"\x00" * 64, step=4, speed_mult=4)


class BundleTests(unittest.TestCase):
    def test_lzs_round_trips(self) -> None:
        data = bytes(range(256)) * 20 + b"abcabcabcabc" * 50 + bytes(300)
        self.assertEqual(lzs_pack.decompress(lzs_pack.compress(data)), data)

    def test_bundle_script_is_patched_wherever_it_sits(self) -> None:
        ev = bytearray(vanilla_ev())
        for i in range(ANCHOR_START, ANCHOR_END):
            ev[i] = (i * 7) & 0xFF
        bundle = lzs_pack.compress(b"U" * 1000 + bytes(ev) + b"\xaa" * 500)

        out = lzs_pack.decompress(patch_bundle(bundle, bytes(ev), step=4, speed_mult=4))

        self.assertEqual(word(out, 1000 + STEP_OFFSET), 4)
        self.assertEqual(word(out, 1000 + 0x39CC), 16)

    def test_missing_anchor_is_refused(self) -> None:
        bundle = lzs_pack.compress(b"\x00" * 4000)
        with self.assertRaises(SystemExit):
            patch_bundle(bundle, bytes(range(256)) * 80, step=4, speed_mult=4)


if __name__ == "__main__":
    unittest.main()
