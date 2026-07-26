#!/usr/bin/env python3
"""Create (and optionally verify) PPF 3.0 patches — same format as RomPatcher.js.

Compatible with https://github.com/marcrobledo/RomPatcher.js (creator mode → PPF).

Example:
  python scripts/make_ppf.py \\
    workspace/iso-extract/ff7_disc1_pristine.bin \\
    workspace/iso-extract/ff7_disc1_final.bin \\
    -o workspace/iso-extract/my-mod.ppf \\
    -d "FF7 disc1 Makou + encounter stub"

  # Optional: verify patch applies cleanly
  python scripts/make_ppf.py ... --verify

Does not commit or distribute game images — output .ppf only.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

CHUNK = 1024 * 1024
MAX_RECORD = 0xFF


def _pack_u64_le(offset: int) -> bytes:
    """PPF3 stores offset as two u32 LE (lo, hi), matching RomPatcher.js."""
    return struct.pack("<II", offset & 0xFFFFFFFF, (offset >> 32) & 0xFFFFFFFF)


def create_ppf3(
    original: Path,
    modified: Path,
    output: Path,
    description: str = "Patch description",
) -> dict:
    """Stream-diff original→modified into a PPF3 file (RomPatcher.js-compatible)."""
    orig_size = original.stat().st_size
    mod_size = modified.stat().st_size
    # RomPatcher pads the shorter side with 0x00 when comparing
    compare_len = max(orig_size, mod_size)

    desc = description.encode("ascii", errors="replace")[:50]
    desc = desc + b" " * (50 - len(desc))

    records: list[tuple[int, bytes]] = []
    run_off: int | None = None
    run = bytearray()

    def flush() -> None:
        nonlocal run_off, run
        if run_off is None or not run:
            run_off = None
            run = bytearray()
            return
        # Split into ≤255-byte records
        pos = run_off
        data = bytes(run)
        i = 0
        while i < len(data):
            piece = data[i : i + MAX_RECORD]
            records.append((pos + i, piece))
            i += len(piece)
        run_off = None
        run = bytearray()

    with original.open("rb") as fo, modified.open("rb") as fm:
        offset = 0
        while offset < compare_len:
            n = min(CHUNK, compare_len - offset)
            a = fo.read(n)
            b = fm.read(n)
            if len(a) < n:
                a = a + b"\x00" * (n - len(a))
            if len(b) < n:
                b = b + b"\x00" * (n - len(b))

            for i in range(n):
                if a[i] != b[i]:
                    abs_off = offset + i
                    if run_off is None:
                        run_off = abs_off
                        run = bytearray([b[i]])
                    elif abs_off == run_off + len(run) and len(run) < MAX_RECORD:
                        run.append(b[i])
                    else:
                        flush()
                        run_off = abs_off
                        run = bytearray([b[i]])
                else:
                    flush()
            offset += n
        flush()

    # RomPatcher.js: if modified grew and last byte is 0x00, force a record
    if mod_size > orig_size:
        with modified.open("rb") as fm:
            fm.seek(mod_size - 1)
            if fm.read(1) == b"\x00":
                # avoid duplicate if already covered
                if not records or records[-1][0] + len(records[-1][1]) < mod_size:
                    records.append((mod_size - 1, b"\x00"))

    # Header (PPF3, no block-check, no undo) — layout matches RomPatcher.format.ppf.js
    out = bytearray()
    out += b"PPF30"
    out += bytes([2])  # version-1
    out += desc
    out += bytes([0x00, 0x00, 0x00, 0x00])  # imageType BIN, no blockcheck, no undo, dummy

    for off, data in records:
        out += _pack_u64_le(off)
        out += bytes([len(data)])
        out += data

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(out)

    return {
        "records": len(records),
        "changed_bytes": sum(len(d) for _, d in records),
        "ppf_size": len(out),
        "original_size": orig_size,
        "modified_size": mod_size,
        "output": str(output),
    }


def apply_ppf3(rom: Path, ppf: Path, output: Path) -> dict:
    """Apply PPF 2.0/3.0 to rom → output. Returns summary stats."""
    data = bytearray(rom.read_bytes())
    patch = ppf.read_bytes()
    magic = patch[:3]
    if magic != b"PPF":
        raise SystemExit(f"not a PPF file: {ppf}")

    ver_str = patch[3:5].decode("ascii", errors="replace")
    ver_byte = patch[5] + 1
    try:
        ver_from_str = int(ver_str) // 10
    except ValueError as e:
        raise SystemExit(f"bad PPF version string: {ver_str!r}") from e
    if ver_from_str != ver_byte or ver_from_str not in (1, 2, 3):
        raise SystemExit(f"unsupported/invalid PPF version ({ver_from_str})")
    version = ver_from_str

    pos = 6
    description = patch[pos : pos + 50].decode("ascii", errors="replace").rstrip()
    pos += 50

    block_check = False
    undo = False
    if version == 3:
        _image_type = patch[pos]
        block_check = patch[pos + 1] != 0
        undo = patch[pos + 2] != 0
        pos += 4
    elif version == 2:
        block_check = True
        pos += 4  # input file size u32

    if block_check:
        pos += 1024

    records = 0
    changed = 0
    while pos < len(patch):
        if patch[pos : pos + 4] == b"@BEG":
            break
        need = 4 + 1 if version < 3 else 8 + 1
        if pos + need > len(patch):
            break

        if version == 3:
            lo, hi = struct.unpack_from("<II", patch, pos)
            pos += 8
            offset = lo + (hi << 32)
        else:
            (offset,) = struct.unpack_from("<I", patch, pos)
            pos += 4

        length = patch[pos]
        pos += 1
        chunk = patch[pos : pos + length]
        pos += length
        if undo:
            # skip undo bytes (apply forward patch only)
            pos += length

        end = offset + length
        if end > len(data):
            data.extend(b"\x00" * (end - len(data)))
        data[offset:end] = chunk
        records += 1
        changed += length

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    return {
        "version": version,
        "description": description,
        "records": records,
        "changed_bytes": changed,
        "output_size": len(data),
        "output": str(output),
    }


def verify_ppf(original: Path, modified: Path, ppf: Path, tmp_dir: Path) -> None:
    patched = tmp_dir / "verify_patched.bin"
    apply_ppf3(original, ppf, patched)
    # Compare to modified (pad shorter with zeros like creator)
    with modified.open("rb") as fm, patched.open("rb") as fp:
        mo = fm.read()
        pa = fp.read()
    n = max(len(mo), len(pa))
    mo = mo + b"\x00" * (n - len(mo))
    pa = pa + b"\x00" * (n - len(pa))
    if mo != pa:
        # find first diff
        for i, (a, b) in enumerate(zip(mo, pa)):
            if a != b:
                raise SystemExit(f"verify FAILED at offset 0x{i:X}")
        raise SystemExit("verify FAILED (length/content)")
    patched.unlink(missing_ok=True)
    print("verify OK — applying PPF to original matches modified")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Create a PPF 3.0 patch (RomPatcher.js-compatible) from two BIN/ISO images."
    )
    ap.add_argument("original", type=Path, help="Pristine retail .bin")
    ap.add_argument("modified", type=Path, help="Final patched .bin (Makou + stub)")
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output .ppf (default: <modified_stem>.ppf next to modified)",
    )
    ap.add_argument(
        "-d",
        "--description",
        default="FF7 mod patch",
        help="PPF description (max 50 ASCII chars)",
    )
    ap.add_argument(
        "--verify",
        action="store_true",
        help="After create, apply PPF to original and compare to modified",
    )
    args = ap.parse_args()

    original = args.original.expanduser().resolve()
    modified = args.modified.expanduser().resolve()
    if not original.is_file():
        raise SystemExit(f"not found: {original}")
    if not modified.is_file():
        raise SystemExit(f"not found: {modified}")

    output = (
        args.output.expanduser().resolve()
        if args.output
        else modified.with_suffix(".ppf")
    )

    print(f"Original: {original} ({original.stat().st_size} bytes)")
    print(f"Modified: {modified} ({modified.stat().st_size} bytes)")
    print("Diffing (may take a few minutes on full disc images)...")

    info = create_ppf3(original, modified, output, args.description)
    print(f"Wrote:    {info['output']}")
    print(f"Records:  {info['records']}")
    print(f"Changed:  {info['changed_bytes']} bytes")
    print(f"PPF size: {info['ppf_size']} bytes")

    if args.verify:
        print("Verifying...")
        verify_ppf(original, modified, output, output.parent)

    print("Done. Users: pristine .bin + this .ppf in RomPatcher.js / PPF-O-Matic.")


if __name__ == "__main__":
    main()
