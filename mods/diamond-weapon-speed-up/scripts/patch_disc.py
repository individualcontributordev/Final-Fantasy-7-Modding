#!/usr/bin/env python3
"""Speed up Diamond Weapon's world-map approach in a Disc 2 image.

Replaces CDmage for this edit. WORLD/WM0.EV is rewritten in place at its
existing LBA, because FF7 reads world scripts from a hardcoded LBA table in
the executable rather than through the ISO9660 directory -- a relocated file
looks correct to every extraction tool and is never read by the game.

  python patch_disc.py FINALFANTASY7_D2.bin -o D2_fast.bin --pristine D2_orig.bin

The approach is paced by Savemap word 0x390, which diamond_weapon:function_2
advances once per frame; emergence height, facing, and the arrival trigger are
all derived from it. --step scales that, --speed-mult scales the horizontal
glide so the two stay in proportion."""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

_MOD_SCRIPTS = Path(__file__).resolve().parent
_ROOT = _MOD_SCRIPTS.parents[2]
_SHARED = _ROOT / "scripts"
for _p in (_SHARED, _MOD_SCRIPTS):
	if str(_p) not in sys.path:
		sys.path.insert(0, str(_p))

from psx_mode2_iso import extract_file, find_file, replace_file_padded  # noqa: E402
from repair_mode2_edc import repair  # noqa: E402

EV_PATH = "WORLD/WM0.EV"

# Byte offsets inside WM0.EV, read off diamond_weapon:function_2.
STEP_OFFSET = 0x3C0E  # PUSH_CONSTANT operand: frames of progress per frame
ARRIVAL_CMP_OFFSET = 0x3B78  # compare against 0xFC4 that ends the approach
SPEED_OFFSETS = (0x3AA8, 0x3AD6, 0x3B1A, 0x3B46)

VANILLA_STEP = 0x0001
VANILLA_SPEEDS = {0x3AA8: 8, 0x3AD6: 1, 0x3B1A: 8, 0x3B46: 8}

OPCODE_EQ = 0x0070
OPCODE_GE = 0x0063

MAX_SPEED = 255


def _read_word(data: bytes | bytearray, offset: int) -> int:
	return struct.unpack_from("<H", data, offset)[0]


def _write_word(data: bytearray, offset: int, value: int) -> None:
	struct.pack_into("<H", data, offset, value)


def _apply(
	data: bytearray,
	offset: int,
	new_value: int,
	accepted: tuple[int, ...],
	label: str,
) -> None:
	"""Write one word, refusing any site that does not already look expected.

	``accepted`` holds both the vanilla value and the value this script would
	have written, so re-running on an already-patched image is safe while a
	wrong offset or a different build still fails loudly.
	"""
	current = _read_word(data, offset)
	if current not in accepted:
		expected = ", ".join(f"0x{v:X}" for v in accepted)
		raise SystemExit(
			f"{label} @ 0x{offset:X}: found 0x{current:X}, expected one of "
			f"{expected}. This is not the WM0.EV this patch was written for."
		)
	_write_word(data, offset, new_value)
	print(f"  {label} @ 0x{offset:X}: 0x{current:X} -> 0x{new_value:X}")


def patch_worldscript(ev: bytes, *, step: int, speed_mult: int) -> bytes:
	"""Return WM0.EV with a faster Diamond Weapon approach."""
	if not 1 <= step <= 0xFF:
		raise SystemExit("--step must be 1-255")
	if speed_mult < 1:
		raise SystemExit("--speed-mult must be 1 or more")
	if len(ev) <= STEP_OFFSET + 2:
		raise SystemExit(f"WM0.EV is only {len(ev)} bytes -- wrong file")

	data = bytearray(ev)

	for offset in SPEED_OFFSETS:
		vanilla = VANILLA_SPEEDS[offset]
		target = min(vanilla * speed_mult, MAX_SPEED)
		_apply(data, offset, target, (vanilla, target), "SET_SPEED")

	# Arrival is tested with EQ against an exact frame count, so any step
	# above 1 can jump the counter straight over it, skipping the landing
	# animation and the flag it sets. GE keeps the trigger reachable.
	arrival_opcode = OPCODE_EQ if step == 1 else OPCODE_GE
	_apply(
		data,
		ARRIVAL_CMP_OFFSET,
		arrival_opcode,
		(OPCODE_EQ, OPCODE_GE),
		"arrival compare",
	)

	_apply(data, STEP_OFFSET, step, (VANILLA_STEP, step), "counter step")
	return bytes(data)


def verify(image: bytes, *, step: int, expect_lba: int) -> None:
	"""Read the file back through the ISO directory and confirm it never moved."""
	meta = find_file(image, EV_PATH)
	if meta.lba != expect_lba:
		raise SystemExit(
			f"{EV_PATH} moved from LBA {expect_lba} to {meta.lba}. The game reads "
			"this file by hardcoded LBA and would still load the old sectors."
		)
	written = extract_file(image, EV_PATH)
	got = _read_word(written, STEP_OFFSET)
	if got != step:
		raise SystemExit(f"verify failed: counter step reads 0x{got:X}, wanted 0x{step:X}")
	print(f"  verified: {EV_PATH} at LBA {meta.lba}, counter step {step}")


def main() -> int:
	ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	ap.add_argument("image", type=Path, help="Disc 2 BIN (MODE2/2352)")
	ap.add_argument(
		"-o",
		"--output",
		type=Path,
		default=None,
		help="Output BIN (default: <image>.fast.bin; may equal the input)",
	)
	ap.add_argument("--step", type=int, default=4, help="Progress per frame (default 4)")
	ap.add_argument(
		"--speed-mult",
		type=int,
		default=4,
		help="Multiply each vanilla SET_SPEED (default 4)",
	)
	ap.add_argument(
		"--pristine",
		type=Path,
		default=None,
		help="Unmodified Disc 2 BIN; repairs MODE2 Form 1 footers when given",
	)
	args = ap.parse_args()

	image_path = args.image.expanduser()
	out_path = (args.output or image_path.with_suffix(".fast.bin")).expanduser()

	image = bytearray(image_path.read_bytes())
	print(f"read {image_path} ({len(image)} bytes)")

	meta = find_file(image, EV_PATH)
	print(f"=== {EV_PATH}: LBA {meta.lba}, {meta.size} bytes ===")

	patched_ev = patch_worldscript(
		extract_file(image, EV_PATH), step=args.step, speed_mult=args.speed_mult
	)
	replace_file_padded(image, EV_PATH, patched_ev)

	out_path.parent.mkdir(parents=True, exist_ok=True)
	out_path.write_bytes(bytes(image))
	print(f"wrote {out_path}")

	if args.pristine is not None:
		print("=== repair MODE2 Form 1 footers ===")
		stats = repair(args.pristine.expanduser(), out_path, out_path)
		for key, value in stats.items():
			print(f"  {key}: {value}")

	print("=== verify ===")
	verify(out_path.read_bytes(), step=args.step, expect_lba=meta.lba)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
