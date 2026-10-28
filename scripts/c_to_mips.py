#!/usr/bin/env python3
"""Compile Ghidra-style C into PS1 (MIPS I) bytes for one function slot.

  python scripts/c_to_mips.py func.c --addr 0x801b0c74 --size 692 -o func.bin [--syms syms.json]
  python scripts/c_to_mips.py --selftest

Output is NOP-padded to --size; it fails (exit 2) if the code is larger.
FUN_/DAT_/PTR_/LAB_<hex8> names resolve to their address; other names come from --syms {name: addr}.
Requires zig (winget install zig.zig, or set FF7_ZIG).
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PRELUDE = """typedef unsigned char undefined, undefined1, byte, uchar;
typedef unsigned short undefined2, ushort;
typedef unsigned int undefined4, uint;
typedef unsigned long long undefined8, ulonglong;
typedef long long longlong;
typedef void code(void);
typedef _Bool bool;
#line 1
"""
AUTO_SYM = re.compile(r"\b(?:FUN|DAT|PTR|LAB|SUB|UNK)_([0-9a-fA-F]{8})\b")
IDENT = re.compile(r"[A-Za-z_]\w*")


def find_zig() -> str:
    z = os.environ.get("FF7_ZIG") or shutil.which("zig")
    if not z:
        hits = glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\zig.zig*\zig-*\zig.exe"))
        z = hits[0] if hits else None
    if not z:
        raise SystemExit("zig not found: winget install zig.zig (or set FF7_ZIG)")
    return z


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(2 if not (r.stderr or r.stdout).strip() else _fail(r))
    return r


def _fail(r):
    sys.stderr.write(r.stderr or r.stdout)
    return 2


def compile_c(source: str, addr: int, size: int, syms: dict[str, int]) -> bytes:
    if addr % 4:
        raise SystemExit("address must be 4-byte aligned")
    zig = find_zig()
    names = set(IDENT.findall(source))
    defs = {}
    for m in AUTO_SYM.finditer(source):
        defs[m.group(0)] = int(m.group(1), 16)
    for n in names & syms.keys():
        defs[n] = syms[n]
    # A symbol at the slot address is the function being replaced; the source defines it.
    defs = {n: a for n, a in defs.items() if a != addr}
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "f.c").write_text(PRELUDE + source, encoding="utf-8")
        run([zig, "cc", "-target", "mipsel-freestanding", "-mcpu=mips1", "-O2", "-fomit-frame-pointer", "-fno-sanitize=all", "-ffreestanding", "-fno-pic",
             "-mno-abicalls", "-G0", "-fno-builtin", "-fno-stack-protector", "-fno-unwind-tables",
             "-fno-asynchronous-unwind-tables", "-w", "-c", str(td / "f.c"), "-o", str(td / "f.o")])
        # One flat section: code first, then its constants/data (all counted against --size).
        (td / "f.ld").write_text(
            f"SECTIONS {{ . = {addr:#x}; .text : {{ *(.text*) *(.rodata*) *(.sdata*) *(.data*) *(.sbss*) *(.bss*) *(COMMON) }} =0 "
            "/DISCARD/ : { *(.MIPS.abiflags) *(.reginfo) *(.pdr) *(.gnu.attributes) *(.mdebug*) *(.comment) *(.eh_frame*) } }")
        link = [zig, "ld.lld", "-m", "elf32ltsmip", "-T", str(td / "f.ld"), "-e", "0",
                str(td / "f.o"), "-o", str(td / "f.elf")]
        link += [f"--defsym={n}={a:#x}" for n, a in defs.items()]
        run(link)
        run([zig, "objcopy", "-O", "binary", "-j", ".text", str(td / "f.elf"), str(td / "f.bin")])
        code = (td / "f.bin").read_bytes().rstrip(b"\0")
        code += b"\0" * (-len(code) % 4)  # trailing zeros are nops; padded back below
    if len(code) > size:
        raise SystemExit(f"compiled code is {len(code)} bytes, slot is {size}")
    return code + b"\0" * (size - len(code))


def selftest() -> None:
    got = compile_c("void f(void){}", 0x80010000, 8, {})
    assert got == bytes.fromhex("0800e00300000000"), got.hex()
    got = compile_c("extern void FUN_80012340(void); void f(void){FUN_80012340();}", 0x80010000, 64, {})
    assert int.from_bytes(got[8:12], "little") >> 26 == 3, got.hex()  # jal FUN_80012340 after the stack adjust
    try:
        compile_c("int f(int a){return a*3+a/7;}", 0x80010000, 4, {})
    except SystemExit as e:
        assert "slot is 4" in str(e), e
    else:
        raise AssertionError("oversize code was accepted")
    print("selftest ok")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", nargs="?", type=Path)
    ap.add_argument("--addr", type=lambda s: int(s, 0))
    ap.add_argument("--size", type=lambda s: int(s, 0))
    ap.add_argument("--syms", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    if not (a.source and a.addr is not None and a.size and a.output):
        ap.error("source, --addr, --size and -o are required")
    syms = {k: int(v, 0) if isinstance(v, str) else v for k, v in json.loads(a.syms.read_text()).items()} if a.syms else {}
    a.output.write_bytes(compile_c(a.source.read_text(encoding="utf-8"), a.addr, a.size, syms))
    return 0


if __name__ == "__main__":
    sys.exit(main())
