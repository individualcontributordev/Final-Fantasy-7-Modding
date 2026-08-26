#!/usr/bin/env python3
"""Poll DuckStation RAM over its built-in GDB server while you playtest.

Enable in DuckStation: Settings -> Advanced -> "Enable GDB Server" (port
defaults to 19000). Leave the game running (don't attach an actual GDB/IDE
debugger at the same time).

Usage:
    python3 scripts/gdb_ram_watch.py --out watch_log.txt

It pauses the core briefly (~every --interval seconds) to snapshot a memory
range + registers, logs any byte changes, then resumes. Press Ctrl+C when
you hit the freeze/bug: it does one final snapshot and writes everything to
--out (plain text, safe to paste/send back).
"""
import argparse
import socket
import time
import sys

GDB_REGS = ["r%d" % i for i in range(32)] + ["sr", "lo", "hi", "bad", "cause", "pc"]


def checksum(data: bytes) -> int:
    return sum(data) & 0xFF


def send_packet(sock: socket.socket, body: str) -> None:
    pkt = f"${body}#{checksum(body.encode()):02x}".encode()
    sock.sendall(pkt)


def read_reply(sock: socket.socket, timeout=2.0) -> str:
    sock.settimeout(timeout)
    buf = b""
    while True:
        c = sock.recv(1)
        if not c:
            break
        if c == b"+" or c == b"-":
            continue
        buf += c
        if c == b"#":
            buf += sock.recv(2)
            break
    if buf.startswith(b"$"):
        buf = buf[1:-3]
    return buf.decode(errors="replace")


def rsp_call(sock: socket.socket, body: str) -> str:
    send_packet(sock, body)
    return read_reply(sock)


def halt(sock: socket.socket) -> str:
    sock.sendall(b"\x03")
    return read_reply(sock, timeout=3.0)


def read_mem(sock: socket.socket, addr: int, length: int) -> bytes:
    reply = rsp_call(sock, f"m{addr:x},{length:x}")
    try:
        return bytes.fromhex(reply)
    except ValueError:
        return b""


def read_regs(sock: socket.socket) -> dict:
    reply = rsp_call(sock, "g")
    vals = {}
    try:
        raw = bytes.fromhex(reply)
        for i, name in enumerate(GDB_REGS):
            if (i + 1) * 4 <= len(raw):
                word = int.from_bytes(raw[i * 4:(i + 1) * 4], "little")
                vals[name] = word
    except ValueError:
        pass
    return vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=19000)
    ap.add_argument("--addr", type=lambda x: int(x, 0), default=0x0)
    ap.add_argument("--len", type=lambda x: int(x, 0), default=0x800)
    ap.add_argument("--interval", type=float, default=0.25)
    ap.add_argument("--out", default="workspace/iso-extract/ram_watch_log.txt")
    args = ap.parse_args()

    sock = socket.create_connection((args.host, args.port), timeout=5)
    print(f"Connected to {args.host}:{args.port}. Watching 0x{args.addr:x}"
          f"-0x{args.addr+args.len:x}. Ctrl+C at the freeze to stop.")

    log = []
    prev = None
    try:
        while True:
            halt(sock)
            snap = read_mem(sock, args.addr, args.len)
            regs = read_regs(sock)
            ts = time.strftime("%H:%M:%S")
            if snap != prev:
                pc = regs.get("pc")
                cause = regs.get("cause")
                line = (f"[{ts}] CHANGE at 0x{args.addr:x} "
                        f"pc={hex(pc) if pc is not None else '?'} "
                        f"cause={hex(cause) if cause is not None else '?'}\n"
                        f"  bytes: {snap.hex()}\n")
                print(line.strip())
                log.append(line)
                prev = snap
            rsp_call(sock, "c")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopping, taking final snapshot...")
        halt(sock)
        snap = read_mem(sock, args.addr, args.len)
        regs = read_regs(sock)
        log.append("\n=== FINAL SNAPSHOT (Ctrl+C) ===\n")
        log.append(f"registers: {regs}\n")
        log.append(f"mem 0x{args.addr:x}+0x{args.len:x}: {snap.hex()}\n")
    finally:
        with open(args.out, "w") as f:
            f.writelines(log)
        print(f"Wrote log to {args.out}")


if __name__ == "__main__":
    main()
