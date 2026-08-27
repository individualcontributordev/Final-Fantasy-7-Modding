#!/usr/bin/env python3
"""Poll DuckStation RAM over its built-in GDB server while you playtest.

Enable in DuckStation: Settings -> Advanced -> "Enable GDB Server" (port
defaults to 19000). Leave the game running (don't attach an actual GDB/IDE
debugger at the same time).

Usage:
    python3 scripts/gdb_ram_watch.py --out watch_log.txt

It pauses the core briefly (~every --interval seconds) to snapshot a memory
range + registers + all DMA channel registers (MADR/BCR/CHCR/busy flag) +
an approximate call-stack backtrace, logs any byte changes, then resumes.
Press Ctrl+C when you hit the freeze/bug: it does one final snapshot and
writes everything to --out (plain text, safe to paste/send back). No need
to set anything else up in DuckStation -- just play until it freezes.
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
    """Read one RSP packet and ACK it with '+' (required by most stubs)."""
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
    sock.sendall(b"+")
    if buf.startswith(b"$"):
        buf = buf[1:-3]
    return buf.decode(errors="replace")


def rsp_call(sock: socket.socket, body: str, timeout=2.0) -> str:
    send_packet(sock, body)
    return read_reply(sock, timeout=timeout)


def halt(sock: socket.socket) -> str:
    """Send Ctrl+C and read the resulting stop-reply packet."""
    sock.sendall(b"\x03")
    return read_reply(sock, timeout=5.0)


def cont_no_wait(sock: socket.socket) -> None:
    """Send 'continue' without blocking for its reply (it won't arrive
    until the target stops, which we trigger later via halt())."""
    send_packet(sock, "c")


def drain_stray(sock: socket.socket) -> None:
    """Discard any bytes sitting in the socket buffer (e.g. a stale stop
    reply from a previous continue, or a manual unpause in the UI)."""
    sock.settimeout(0.05)
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
    except socket.timeout:
        pass
    except OSError:
        pass


def handshake(sock: socket.socket) -> None:
    """Sync the RSP stream: drain anything pending, then confirm the
    stub responds to a basic query before we start polling."""
    drain_stray(sock)
    try:
        rsp_call(sock, "qSupported", timeout=3.0)
    except socket.timeout:
        pass
    drain_stray(sock)


def read_mem(sock: socket.socket, addr: int, length: int) -> bytes:
    reply = rsp_call(sock, f"m{addr:x},{length:x}")
    try:
        return bytes.fromhex(reply)
    except ValueError:
        return b""


# PS1 DMA controller: 7 channels at 0x1F801080 + n*0x10, each with
# MADR (+0x0), BCR (+0x4), CHCR (+0x8); plus shared DPCR/DICR at the end.
DMA_BASE = 0x1F801080
DMA_CHANNELS = ["MDEC_in", "MDEC_out", "GPU", "CDROM", "SPU", "PIO", "OTC"]


def read_dma_regs(sock: socket.socket) -> dict:
    """Snapshot all DMA channel registers plus DPCR/DICR. A channel's CHCR
    busy bit (bit 24) being set means a transfer was in flight at halt
    time -- the most direct evidence of *which* DMA channel is moving data
    right before/as the corruption happens."""
    out = {}
    for i, name in enumerate(DMA_CHANNELS):
        base = DMA_BASE + i * 0x10
        raw = read_mem(sock, base, 0xC)
        if len(raw) == 0xC:
            madr, bcr, chcr = int.from_bytes(raw[0:4], "little"), \
                int.from_bytes(raw[4:8], "little"), \
                int.from_bytes(raw[8:12], "little")
            out[name] = {
                "MADR": hex(madr), "BCR": hex(bcr), "CHCR": hex(chcr),
                "busy": bool(chcr & (1 << 24)),
            }
    ctrl = read_mem(sock, 0x1F8010F0, 8)
    if len(ctrl) == 8:
        out["DPCR"] = hex(int.from_bytes(ctrl[0:4], "little"))
        out["DICR"] = hex(int.from_bytes(ctrl[4:8], "little"))
    return out


def read_stack_backtrace(sock: socket.socket, sp: int, ra: int, depth: int = 24) -> list:
    """Walk words above $sp looking for plausible return addresses (KSEG0
    code range 0x80010000-0x80200000, word-aligned) to reconstruct an
    approximate call stack without needing a symbol table."""
    trace = [hex(ra)] if ra else []
    raw = read_mem(sock, sp, depth * 4)
    for i in range(0, len(raw) - 3, 4):
        word = int.from_bytes(raw[i:i + 4], "little")
        if 0x80010000 <= word <= 0x80200000 and word % 4 == 0:
            trace.append(hex(word))
    return trace


def read_regs(sock: socket.socket) -> dict:
    """Parse a 'g' packet reply into named registers.

    Some stubs (DuckStation included) mark unavailable register bytes with
    'x' fill characters instead of hex digits (per the GDB RSP spec), which
    made bytes.fromhex() on the whole string raise and drop everything.
    Parse 8-hex-char (4-byte) chunks individually so a few 'xx'-filled
    registers don't blank out the ones that *are* available (like pc).
    """
    reply = rsp_call(sock, "g")
    vals = {}
    for i, name in enumerate(GDB_REGS):
        chunk = reply[i * 8:(i + 1) * 8]
        if len(chunk) < 8 or "x" in chunk or "X" in chunk:
            continue
        try:
            word = int.from_bytes(bytes.fromhex(chunk), "little")
        except ValueError:
            continue
        vals[name] = word
    if not vals:
        # Nothing parsed at all -- keep the raw reply so we can see why
        # (error reply like "E01", empty string, unexpected format, etc.)
        vals["_raw_reply"] = reply
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
    handshake(sock)
    print(f"Connected to {args.host}:{args.port}. Watching 0x{args.addr:x}"
          f"-0x{args.addr+args.len:x}. Ctrl+C at the freeze to stop.")

    log = []
    prev = None
    resumed = True  # track whether the emulator should currently be running
    try:
        while True:
            try:
                halt(sock)
                resumed = False
                snap = read_mem(sock, args.addr, args.len)
                regs = read_regs(sock)
                dma = read_dma_regs(sock)
            except socket.timeout:
                # Stub didn't answer (e.g. it was manually unpaused/paused
                # in the UI mid-cycle and the stream desynced). Resync and
                # skip this cycle instead of crashing.
                print("(resync: no reply from stub, retrying)")
                drain_stray(sock)
                resumed = True
                time.sleep(args.interval)
                continue
            ts = time.strftime("%H:%M:%S")
            if snap != prev:
                pc = regs.get("pc")
                sp = regs.get("r29")
                ra = regs.get("r31")
                cause = regs.get("cause")
                raw_dbg = f" raw_regs_reply={regs['_raw_reply']!r}" if "_raw_reply" in regs else ""
                busy = [f"{n}(MADR={r['MADR']},BCR={r['BCR']},CHCR={r['CHCR']})"
                        for n, r in dma.items() if isinstance(r, dict) and r.get("busy")]
                bt = read_stack_backtrace(sock, sp, ra) if sp is not None else []
                line = (f"[{ts}] CHANGE at 0x{args.addr:x} "
                        f"pc={hex(pc) if pc is not None else '?'} "
                        f"cause={hex(cause) if cause is not None else '?'}"
                        f"{raw_dbg}\n"
                        f"  dma_busy: {busy if busy else 'none'}\n"
                        f"  dma_all: {dma}\n"
                        f"  backtrace(approx): {bt}\n"
                        f"  bytes: {snap.hex()}\n")
                print(line.strip())
                log.append(line)
                prev = snap
            cont_no_wait(sock)
            resumed = True
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopping, taking final snapshot...")
        try:
            halt(sock)
            snap = read_mem(sock, args.addr, args.len)
            regs = read_regs(sock)
            dma = read_dma_regs(sock)
            sp = regs.get("r29")
            ra = regs.get("r31")
            bt = read_stack_backtrace(sock, sp, ra) if sp is not None else []
            log.append("\n=== FINAL SNAPSHOT (Ctrl+C) ===\n")
            log.append(f"registers: {regs}\n")
            log.append(f"raw 'g' reply: {rsp_call(sock, 'g')!r}\n")
            log.append(f"dma_all: {dma}\n")
            log.append(f"backtrace(approx): {bt}\n")
            log.append(f"mem 0x{args.addr:x}+0x{args.len:x}: {snap.hex()}\n")
        except socket.timeout:
            log.append("\n=== FINAL SNAPSHOT FAILED (stub not responding) ===\n")
        print("Emulator left paused at the freeze for inspection.")
    finally:
        with open(args.out, "w") as f:
            f.writelines(log)
        print(f"Wrote log to {args.out}")


if __name__ == "__main__":
    main()
