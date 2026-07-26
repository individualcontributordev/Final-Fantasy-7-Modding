#!/usr/bin/env python3
"""Apply RCnt2 FORCE stub at FIELD.BIN.dec offset 0xBB7C.

Canonical bytes live in:
  workspace/patches/2026-07-25-force-stub-rcnt2/stub-bb7c.hex
  workspace/patches/2026-07-25-force-stub-rcnt2/jal-bbd4.hex

Packaging (Makou + stub → one PPF): docs/06-packaging-combined-ppf.md

Rate: P(FORCE) ≈ (g_enemy_lure * 3/4) / 256  (slightly under raw lure/256)
"""
import sys
from pathlib import Path

OFFSET = 0xBB7C
JAL_OFFSET = 0xBBD4

_REPO = Path(__file__).resolve().parents[1]
_PATCH_DIR = _REPO / "workspace" / "patches" / "2026-07-25-force-stub-rcnt2"

_FALLBACK_STUB = (
    "80 1f 01 3c 20 11 22 8c 00 00 00 00 06 80 01 3c"
    "19 2f 23 90 ff 00 42 30 82 08 03 00 23 18 61 00"
    "2b 10 43 00 23 10 02 00 07 80 01 3c 3c 17 22 a4"
    + (" 00 00 00 00" * 10)
)


def _load_hex(name: str, fallback: str) -> bytes:
    path = _PATCH_DIR / name
    text = path.read_text() if path.is_file() else fallback
    return bytes.fromhex(text.replace("\n", " "))


STUB = _load_hex("stub-bb7c.hex", _FALLBACK_STUB)
JAL = _load_hex("jal-bbd4.hex", "72 ae 02 0c")


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <FIELD.BIN.dec or .dec.patched>", file=sys.stderr)
        sys.exit(1)
    if len(STUB) != 88:
        raise SystemExit(f"stub must be 88 bytes, got {len(STUB)}")
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
