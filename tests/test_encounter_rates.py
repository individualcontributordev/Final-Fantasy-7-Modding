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


class EncounterRateStubTests(unittest.TestCase):
	def test_half_uses_half_the_area_threshold(self) -> None:
		for patches, name in (
			(FIELD_PATCHES, "stub-bb7c-rate50.hex"),
			(WORLD_PATCHES, "stub-7db4-rate50.hex"),
		):
			stub = read_stub(patches / name)
			for encounter_value in range(256):
				self.assertEqual(
					threshold_from_stub(stub, encounter_value),
					encounter_value // 2,
				)

	def test_double_saturates_instead_of_wrapping(self) -> None:
		for patches, name in (
			(FIELD_PATCHES, "stub-bb7c-rate200.hex"),
			(WORLD_PATCHES, "stub-7db4-rate200.hex"),
		):
			stub = read_stub(patches / name)
			for encounter_value in range(256):
				self.assertEqual(
					threshold_from_stub(stub, encounter_value),
					min(encounter_value * 2, 255),
				)

	def test_stubs_fit_their_fixed_windows(self) -> None:
		self.assertEqual(len(read_stub(FIELD_PATCHES / "stub-bb7c-rate200.hex")), 88)
		self.assertEqual(len(read_stub(WORLD_PATCHES / "stub-7db4-rate200.hex")), 104)


if __name__ == "__main__":
	unittest.main()
