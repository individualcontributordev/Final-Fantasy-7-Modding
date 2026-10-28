#!/usr/bin/env python3
"""Compile frame_counter.c and write patches/frame-counter-sites.txt (same format as new-game-plus).

Hook: the epilogue of the SCUS DrawOTag wrapper (0x8004439c, `lw ra,0x14(sp)`) jumps to a stub in
dead libcd/libgpu debug strings at 0x800104b4, which calls the compiled hook and then finishes the original epilogue.
Needs zig (see scripts/c_to_mips.py)."""
import struct
import sys
from pathlib import Path

_MOD = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_MOD.parent.parent / "scripts"))
from c_to_mips import compile_c  # noqa: E402
from psx_mode2_iso import extract_file  # noqa: E402

scus = extract_file((_MOD.parent.parent / 'workspace' / 'pristine' / 'FINALFANTASY7_D1.BIN').read_bytes(), '/SCUS_941.63')

RAM, HDR = 0x80010000, 0x800  # SCUS_941.63 load address, PSX-EXE header size
HOOK_AT, STUB, HOOK, SLOT = 0x8004439C, 0x800104B4, 0x800105A8, 0x278
CACHE = 0x800104DC  # must match frame_counter.c; the tile slots start at 0x80010834


def off(addr: int) -> int:
	return addr - RAM + HDR


def j(op: int, addr: int) -> int:
	return op | (addr >> 2) & 0x3FFFFFF


code = compile_c((_MOD / "scripts" / "frame_counter.c").read_text(encoding="utf-8"), HOOK, SLOT, {})
# The compiled hook may use $gp as a scratch register without saving it; the game's libs need theirs, so the stub preserves it.
stub = struct.pack("<10I", 0x27BDFFF8, 0xAFBC0000, j(0x0C000000, HOOK), 0, 0x8FBC0000, 0x27BD0008, 0x8FBF0014, 0x8FB00010, j(0x08000000, 0x800443A4), 0)
assert STUB + len(stub) == CACHE
# The two "CD001" strings (PVD check) sit inside the buffer run: copy them next to the stub and repoint their addiu.
CD001 = [(0x80010978, 0x8003FF10, 0x800104E0), (0x80010AAC, 0x80040864, 0x800104E8)]
moves = []
for old, ref, new in CD001:
	lo = scus[off(ref):off(ref) + 4]
	assert int.from_bytes(lo, "little") & 0xFFFF == old & 0xFFFF
	moves += [(new, scus[off(new):off(new) + 8], scus[off(old):off(old) + 8]),
		(ref, lo, (int.from_bytes(lo, "little") & 0xFFFF0000 | new & 0xFFFF).to_bytes(4, "little"))]
rows = moves + [
	(HOOK_AT, bytes.fromhex("1400bf8f"), struct.pack("<I", j(0x08000000, STUB))),
	(STUB, scus[off(STUB):off(STUB) + len(stub)], stub),
	(CACHE, scus[off(CACHE):off(CACHE) + 4], bytes(4)),  # cache word starts empty
	(HOOK, scus[off(HOOK):off(HOOK) + SLOT], code),
]
out = [
	"# Path  Offset  Expected  Replacement",
	"# Frame counter: hook at 0x8004439c (DrawOTag wrapper epilogue) -> stub 0x800104b4 -> hook 0x800105a8.",
	"# Code and the runtime tile slots overwrite libcd/libgpu debug strings, which retail never prints (the switch tables are live and skipped; the CD001 strings are moved). Regenerate with build_sites.py.",
]
out += [f"/SCUS_941.63 {off(a):X} {e.hex()} {n.hex()}" for a, e, n in rows]
(_MOD / "patches" / "frame-counter-sites.txt").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print(f"hook {len(code.rstrip(bytes(1)))} bytes; wrote {len(rows)} sites")
