#!/usr/bin/env python3
"""Speed up Diamond Weapon's world-map approach in a Disc 1 image.

Replaces CDmage for this edit. The game never reads WORLD/WM0.EV: it loads the
world script from inside the LZS bundles WORLD/WM1.TXZ, WM2.TXZ and WM2S.TXZ.
Each bundle is decompressed, the same words are patched in its embedded copy of
the script, and it is recompressed into the original slot. WM0.EV is patched
too so the loose file and the bundles agree. Files stay at their existing LBA,
because FF7 reads them from a hardcoded LBA table in the executable rather than
through the ISO9660 directory.

  python patch_disc.py FINALFANTASY7_D2.bin -o D2_fast.bin --pristine D2_orig.bin

The approach is paced by Savemap word 0x390, which the Diamond Weapon world
script advances once per frame; emergence height, facing, and the arrival
trigger are all derived from it. The first leg (counter < 0xAF0) is underground
and most of the wait, so it is shortened with --leg1-frames. --step and
--speed-mult optionally scale the visible legs too, but the turn toward Midgar
is frame-count dependent, so they distort the path."""

from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

_MOD_SCRIPTS = Path(__file__).resolve().parent
_ROOT = _MOD_SCRIPTS.parents[2]
_SHARED = _ROOT / "scripts"
for _p in (_SHARED, _MOD_SCRIPTS):
	if str(_p) not in sys.path:
		sys.path.insert(0, str(_p))

import lzs_pack  # noqa: E402
from psx_mode2_iso import extract_file, find_file, replace_file_padded  # noqa: E402
from repair_mode2_edc import repair  # noqa: E402

EV_PATH = "WORLD/WM0.EV"
TXZ_PATHS = ("WORLD/WM1.TXZ", "WORLD/WM2.TXZ", "WORLD/WM2S.TXZ")
# Bytes of WM0.EV just before the first patched operand. The embedded script
# differs from the loose file in its jump operands, so match only this window.
ANCHOR_START, ANCHOR_END = 0x39A0, 0x39CA

# Byte offsets inside WM0.EV, read off the Diamond Weapon world script.
STEP_OFFSET = 0x3C0E  # PUSH_CONSTANT operand: frames of progress per frame
ARRIVAL_CMP_OFFSET = 0x3B78  # compare against 0xFC4 that ends the approach
# 0x39CC is the glide in function_26, the cutscene that starts the march.
SPEED_OFFSETS = (0x39CC, 0x3AA8, 0x3AD6, 0x3B1A, 0x3B46)

# Leg 1 (counter < 0xAF0) is underground and ~70% of the approach. It is sped up
# by starting the counter late and gliding proportionally faster, so the visible
# turn keeps its vanilla frame timing and the path stays the same.
LEG1_END = 0xAF0
LEG1_SPEED_OFFSET = 0x3AA8
VANILLA_LEG1_SPEED = 8
# `savemap[0x390] = 0` sits at a different offset in WM0.EV and the bundled
# copies (the bundles are 8 bytes shorter by then), so it is found by pattern.
COUNTER_SEARCH_END = 0x4560
COUNTER_INIT_RE = re.compile(rb"\x1c\x01\x90\x03\x10\x01(..)\xe0\x00", re.DOTALL)

# After the turn (counter 0xB45..0xFC4) the speed is constant, so that stretch is
# halved by rescaling its compare constants and doubling speed: same distance in
# half the counts. Emergence height is (c - E) >> 1, so halving the span needs >> 0.
POST_SPEED_OFFSETS = (0x3B1A, 0x3B46)
TURN_END = 0xB45
# offset -> vanilla value; each is a threshold, rescaled relative to TURN_END
POST_THRESHOLDS = {0x3AFA: 0xE66, 0x3B0A: 0xE65, 0x3B32: 0xFC4, 0x3B52: 0xE66,
	0x3B76: 0xFC4, 0x3BEE: 0xFC5, 0x3BFE: 0xFC5}
EMERGE_SHIFT_OFFSET = 0x3B10
# Vanilla end-of-approach values; --final-trim lowers them to stop Diamond short of Midgar.
FINAL_END = (0xFC4, 0xFC5)

VANILLA_STEP = 0x0001
VANILLA_SPEEDS = {0x39CC: 4, 0x3AA8: 8, 0x3AD6: 1, 0x3B1A: 8, 0x3B46: 8}

OPCODE_EQ = 0x0070
OPCODE_GE = 0x0063

# Speed words above 127 read as negative in the engine (Diamond walked backwards).
MAX_SPEED = 127


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


def patch_worldscript(
	ev: bytes, *, step: int, speed_mult: int, leg1_frames: int = 0, post_turn_mult: int = 1,
	leg1_speed: int = 0, final_trim: int = 0,
) -> bytes:
	"""Return WM0.EV with a faster Diamond Weapon approach."""
	if not 1 <= step <= 0xFF:
		raise SystemExit("--step must be 1-255")
	if speed_mult < 1:
		raise SystemExit("--speed-mult must be 1 or more")
	if post_turn_mult not in (1, 2):
		raise SystemExit("--post-turn-mult must be 1 or 2")
	if not 0 <= leg1_frames <= LEG1_END:
		raise SystemExit(f"--leg1-frames must be 0-{LEG1_END}")
	if not 0 <= leg1_speed <= MAX_SPEED:
		raise SystemExit(f"--leg1-speed must be 0-{MAX_SPEED}")
	if not 0 <= final_trim < 175:
		raise SystemExit("--final-trim must be 0-174")
	if len(ev) < COUNTER_SEARCH_END:
		raise SystemExit(f"WM0.EV is only {len(ev)} bytes -- wrong file")

	data = bytearray(ev)

	for offset in SPEED_OFFSETS:
		if leg1_frames and offset == LEG1_SPEED_OFFSET:
			continue
		vanilla = VANILLA_SPEEDS[offset]
		k = post_turn_mult if offset in POST_SPEED_OFFSETS else 1
		target = min(vanilla * speed_mult * k, MAX_SPEED)
		accepted = (vanilla, target)
		_apply(data, offset, target, accepted, "SET_SPEED")

	for offset, vanilla in POST_THRESHOLDS.items():
		# the emergence base is one below its threshold, so scale the threshold
		target = TURN_END + (vanilla + (offset == 0x3B0A) - TURN_END) // post_turn_mult - (offset == 0x3B0A)
		if vanilla in FINAL_END:
			target -= final_trim
		_apply(data, offset, target, (vanilla, target), "post-turn threshold")
	_apply(data, EMERGE_SHIFT_OFFSET, 2 - post_turn_mult, (1, 0), "emergence shift")

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

	if leg1_frames:
		# Default: same distance as vanilla (speed x frames), covered in leg1_frames frames.
		speed = leg1_speed or VANILLA_LEG1_SPEED * LEG1_END // leg1_frames
		if speed > MAX_SPEED:
			raise SystemExit(f"--leg1-frames must be at least {VANILLA_LEG1_SPEED * LEG1_END // (MAX_SPEED + 1) + 1}")
		_apply(data, LEG1_SPEED_OFFSET, speed, (VANILLA_LEG1_SPEED, speed), "leg 1 speed")
		start = LEG1_END - leg1_frames * step
		if start < 0:
			raise SystemExit(f"--leg1-frames x --step must be at most {LEG1_END}; the counter cannot start negative")
		inits = [m.start(1) for m in COUNTER_INIT_RE.finditer(data, STEP_OFFSET)]
		if len(inits) != 1:
			raise SystemExit(f"counter init found {len(inits)} times, expected 1")
		_apply(data, inits[0], start, (0, start), "counter start")
	return bytes(data)


def patch_bundle(
	bundle: bytes, ev: bytes, *, step: int, speed_mult: int, leg1_frames: int = 0,
	post_turn_mult: int = 1, leg1_speed: int = 0, final_trim: int = 0,
) -> bytes:
	"""Return the LZS bundle with its embedded Diamond script patched."""
	data = bytearray(lzs_pack.decompress(bundle))
	anchor = ev[ANCHOR_START:ANCHOR_END]
	if data.count(anchor) != 1:
		raise SystemExit(f"world script anchor found {data.count(anchor)} times in bundle, expected 1")
	base = data.find(anchor) - ANCHOR_START
	size = COUNTER_SEARCH_END
	data[base : base + size] = patch_worldscript(
		bytes(data[base : base + size]),
		step=step,
		speed_mult=speed_mult,
		leg1_frames=leg1_frames,
		post_turn_mult=post_turn_mult,
		leg1_speed=leg1_speed,
		final_trim=final_trim,
	)
	packed = lzs_pack.compress(bytes(data))
	if lzs_pack.decompress(packed) != bytes(data):
		raise SystemExit("LZS round trip failed")
	return packed


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
	for path in TXZ_PATHS:
		data = lzs_pack.decompress(extract_file(image, path))
		base = data.find(written[ANCHOR_START:ANCHOR_END]) - ANCHOR_START
		got = _read_word(data, base + STEP_OFFSET)
		if got != step:
			raise SystemExit(f"verify failed: {path} counter step reads 0x{got:X}, wanted 0x{step:X}")
	print(f"  verified: {EV_PATH} at LBA {meta.lba} and {len(TXZ_PATHS)} bundles, counter step {step}")


def main() -> int:
	ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	ap.add_argument("image", type=Path, help="Disc 1 or 2 BIN (MODE2/2352)")
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
		help="Multiply each vanilla SET_SPEED (default 4, matching --step)",
	)
	ap.add_argument(
		"--leg1-frames",
		type=int,
		default=700,
		help="Frames for the underground first leg, vanilla 2800 (default 700 = speed 32 at --step 4; 0 = vanilla)",
	)
	ap.add_argument(
		"--leg1-speed", type=int, default=48,
		help="Fixed leg 1 speed; distance = speed x frames (default 48, as shipped in csr-plus 0.3.9; 0 = keep vanilla distance)",
	)
	ap.add_argument(
		"--final-trim", type=int, default=100,
		help="Counter units cut from the end of the approach; at post-turn speed 64 each unit is 16 world units shorter (default 100, as shipped in csr-plus 0.3.9)",
	)
	ap.add_argument(
		"--post-turn-mult",
		type=int,
		default=2,
		help="Run the stretch after the turn this many times faster, same distance (1 or 2, default 2)",
	)
	ap.add_argument(
		"--pristine",
		type=Path,
		default=None,
		help="Unmodified BIN of the same disc; repairs MODE2 Form 1 footers when given",
	)
	args = ap.parse_args()

	image_path = args.image.expanduser()
	out_path = (args.output or image_path.with_suffix(".fast.bin")).expanduser()

	image = bytearray(image_path.read_bytes())
	print(f"read {image_path} ({len(image)} bytes)")

	meta = find_file(image, EV_PATH)
	print(f"=== {EV_PATH}: LBA {meta.lba}, {meta.size} bytes ===")

	ev = extract_file(image, EV_PATH)
	patched_ev = patch_worldscript(
		ev, step=args.step, speed_mult=args.speed_mult, leg1_frames=args.leg1_frames,
		post_turn_mult=args.post_turn_mult, leg1_speed=args.leg1_speed,
		final_trim=args.final_trim,
	)
	replace_file_padded(image, EV_PATH, patched_ev)
	for path in TXZ_PATHS:
		print(f"=== {path} ===")
		bundle = extract_file(image, path)
		replace_file_padded(
			image,
			path,
			patch_bundle(
				bundle,
				ev,
				step=args.step,
				speed_mult=args.speed_mult,
				leg1_frames=args.leg1_frames,
				post_turn_mult=args.post_turn_mult,
				leg1_speed=args.leg1_speed,
				final_trim=args.final_trim,
			),
		)

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
