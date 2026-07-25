#!/usr/bin/env python3
"""Search FIELD.BIN.dec for encounter-related address bytes (LE)."""

import struct
import sys
from pathlib import Path

NEEDLES = [
    ("StepID ptr u32 LE", bytes.fromhex("40c50980")),       # 0x8009C540
    ("Offset ptr u32 LE", bytes.fromhex("2cad0980")),       # 0x8009AD2C
    ("Danger ptr u32 LE", bytes.fromhex("3c170880")),       # 0x8007173C
    ("Formation ptr u32 LE", bytes.fromhex("20c10780")),    # 0x80071C20
    ("RNG table ptr u32 LE", bytes.fromhex("38060480")),    # 0x80040638 (if absolute)
    ("StepID low u16 LE", bytes.fromhex("40c5")),           # 0xC540
    ("StepID mid u16 LE", bytes.fromhex("c509")),           # 0x09C5 as half — noisy
    ("lui imm 0x8009 LE half", bytes.fromhex("0980")),     # common in lui 0x8009 — noisy
    ("RNG table head", bytes.fromhex("b1caee6c5a712e55")),
]


def find_all(data: bytes, needle: bytes, limit: int = 20) -> list[int]:
    out: list[int] = []
    start = 0
    while len(out) < limit:
        i = data.find(needle, start)
        if i < 0:
            break
        out.append(i)
        start = i + 1
    return out


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <FIELD.BIN.dec>")
        sys.exit(1)

    path = Path(sys.argv[1]).expanduser().resolve()
    data = path.read_bytes()
    print(f"File: {path} ({len(data)} bytes)\n")

    for name, needle in NEEDLES:
        hits = find_all(data, needle)
        extra = ""
        if len(hits) == 20 and data.find(needle, hits[-1] + 1) >= 0:
            extra = " (truncated at 20)"
        print(f"{name}  [{needle.hex()}]  hits={len(hits)}{extra}")
        for off in hits:
            va = 0x80000000 + off
            print(f"  file 0x{off:X}  va 0x{va:08X}")
        print()


if __name__ == "__main__":
    main()
