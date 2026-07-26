#!/usr/bin/env python3
"""Apply RCnt2 FORCE stub at FIELD.BIN.dec offset 0xBB7C."""
import sys
from pathlib import Path

OFFSET = 0xBB7C
JAL_OFFSET = 0xBBD4
STUB = bytes.fromhex(
    "80 1f 01 3c 20 11 22 8c 00 00 00 00 06 80 01 3c"
    "19 2f 23 90 ff 00 42 30 2b 10 43 00 23 10 02 00"
    "07 80 01 3c 3c 17 22 a4"
    + (" 00 00 00 00" * 12)
)
JAL = bytes.fromhex("72 ae 02 0c")

def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <FIELD.BIN.dec or .dec.patched>", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1])
    data = bytearray(path.read_bytes())
    if len(data) < JAL_OFFSET + 4:
        raise SystemExit(f"file too small: {len(data)}")
    data[OFFSET : OFFSET + len(STUB)] = STUB
    data[JAL_OFFSET : JAL_OFFSET + 4] = JAL
    path.write_bytes(data)
    print(f"Patched {path} @ 0x{OFFSET:X} ({len(STUB)} bytes); jal @ 0x{JAL_OFFSET:X}")
    print("Head:", data[OFFSET : OFFSET + 8].hex(" "))

if __name__ == "__main__":
    main()
