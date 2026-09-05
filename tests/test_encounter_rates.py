from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELD_PATCHES = ROOT / "mods" / "field-random-encounters" / "patches"
WORLD_PATCHES = ROOT / "mods" / "world-map-random-encounters" / "patches"


def read_stub(path: Path) -> bytes:
	return bytes.fromhex(path.read_text(encoding="utf-8"))


def threshold_from_stub(stub: bytes, encounter_value: int) -> int:
	"""Execute the threshold arithmetic between the RCnt2 load and comparison."""
	words = [
		int.from_bytes(stub[offset : offset + 4], "little")
		for offset in range(0, len(stub), 4)
	]
	registers = [0] * 32
	registers[3] = encounter_value  # v1
	pc = 6

	while pc < len(words):
		word = words[pc]
		opcode = word >> 26
		rs = (word >> 21) & 31
		rt = (word >> 16) & 31
		rd = (word >> 11) & 31
		shift = (word >> 6) & 31
		function = word & 63
		immediate = word & 0xFFFF

		is_encounter_comparison = (
			opcode == 0 and function == 0x2B and rd == 2 and rs == 2 and rt == 3
		)
		if is_encounter_comparison:
			return registers[3]

		if opcode == 0 and function == 0:  # sll
			registers[rd] = (registers[rt] << shift) & 0xFFFFFFFF
		elif opcode == 0 and function == 2:  # srl
			registers[rd] = registers[rt] >> shift
		elif opcode == 0 and function == 0x21:  # addu
			registers[rd] = (registers[rs] + registers[rt]) & 0xFFFFFFFF
		elif opcode == 0 and function == 0x23:  # subu
			registers[rd] = (registers[rs] - registers[rt]) & 0xFFFFFFFF
		elif opcode == 0 and function == 0x25:  # or
			registers[rd] = registers[rs] | registers[rt]
		elif opcode == 0x0B:  # sltiu
			registers[rt] = int(registers[rs] < immediate)
		elif opcode == 0x0C:  # andi
			registers[rt] = registers[rs] & immediate
		elif opcode == 0x0D:  # ori
			registers[rt] = registers[rs] | immediate
		elif opcode == 5:  # bne; every shipped delay slot is nop
			signed_immediate = immediate if immediate < 0x8000 else immediate - 0x10000
			pc = pc + 1 + signed_immediate if registers[rs] != registers[rt] else pc + 2
			continue
		elif word != 0:
			raise AssertionError(f"unsupported instruction {word:#010x}")

		registers[0] = 0
		pc += 1

	raise AssertionError("stub never compares the encounter threshold")


# Each stub compares the lure byte, scaled, against a timer byte. The scale is
# calibrated so the flat roll lands near the unmodified game's rate while
# running: quarter the byte for half as many battles, half for about the same,
# the raw byte for twice as many. Vanilla's own rate is a ramp, so these are
# frequency targets, not a scale applied to vanilla's threshold.
SCALES = {
	50: lambda lure: lure >> 2,
	100: lambda lure: lure >> 1,
	200: lambda lure: lure,
}


class EncounterRateStubTests(unittest.TestCase):
	def test_shipped_stubs_scale_the_lure_byte_as_calibrated(self) -> None:
		for rate, expected in SCALES.items():
			for patches, stem in (
				(FIELD_PATCHES, "stub-bb7c"),
				(WORLD_PATCHES, "stub-7db4"),
			):
				stub = read_stub(patches / f"{stem}-rate{rate}.hex")
				for lure in range(256):
					with self.subTest(rate=rate, stem=stem, lure=lure):
						self.assertEqual(threshold_from_stub(stub, lure), expected(lure))

	def test_thresholds_stay_inside_the_comparison_byte(self) -> None:
		"""A threshold above 255 would beat every timer value and force battles."""
		for rate in SCALES:
			for patches, stem in (
				(FIELD_PATCHES, "stub-bb7c"),
				(WORLD_PATCHES, "stub-7db4"),
			):
				stub = read_stub(patches / f"{stem}-rate{rate}.hex")
				for lure in range(256):
					self.assertLessEqual(threshold_from_stub(stub, lure), 255)

	def test_stubs_fit_their_fixed_windows(self) -> None:
		for rate in (0, *SCALES):
			self.assertEqual(
				len(read_stub(FIELD_PATCHES / f"stub-bb7c-rate{rate}.hex")), 88
			)
			self.assertEqual(
				len(read_stub(WORLD_PATCHES / f"stub-7db4-rate{rate}.hex")), 104
			)


if __name__ == "__main__":
	unittest.main()
