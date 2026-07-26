#!/usr/bin/env python3
"""Recompress a patched FIELD.BIN.dec back to GZIPPS format."""

import gzip
import struct
import sys
from pathlib import Path

GZIPPS_HEADER_SIZE = 8


def _best_gzip_payload(uncompressed: bytes, prefer_max_len: int | None) -> tuple[bytes, int]:
    """Try gzip levels; prefer smallest that fits prefer_max_len, else overall smallest."""
    # (fits_rank, size, -level, payload) — prefer fit, then smaller, then higher level
    candidates: list[tuple[int, int, int, bytes]] = []
    for level in range(10):
        payload = gzip.compress(uncompressed, compresslevel=level, mtime=0)
        fits = prefer_max_len is None or len(payload) <= prefer_max_len
        candidates.append((0 if fits else 1, len(payload), -level, payload))

    candidates.sort()
    _fits_rank, _size, neg_level, payload = candidates[0]
    return payload, -neg_level


def compress_field_bin(
    src_dec: Path,
    original_field_bin: Path,
    dst: Path | None = None,
) -> Path:
    original = original_field_bin.read_bytes()
    if len(original) < GZIPPS_HEADER_SIZE:
        raise ValueError(f"{original_field_bin}: invalid GZIPPS source")

    dec_size = struct.unpack("<I", original[0:4])[0]
    gzip_subheader = original[4:8]
    # Max gzip payload length that keeps total file <= original
    prefer_payload_max = len(original) - GZIPPS_HEADER_SIZE

    uncompressed = src_dec.read_bytes()
    if len(uncompressed) != dec_size:
        print(
            f"Warning: patched size {len(uncompressed)} != original dec size {dec_size}",
            file=sys.stderr,
        )

    compressed_payload, level = _best_gzip_payload(uncompressed, prefer_payload_max)
    # GZIPPS: [dec_size u32][4-byte subheader from original][gzip payload]
    out = struct.pack("<I", len(uncompressed)) + gzip_subheader + compressed_payload

    if dst is None:
        dst = original_field_bin.with_name(original_field_bin.name + ".new")

    dst.write_bytes(out)

    print(f"Source (dec):     {src_dec} ({len(uncompressed)} bytes)")
    print(f"Original (bin):   {original_field_bin} ({len(original)} bytes)")
    print(f"Output:           {dst} ({len(out)} bytes)")
    print(f"Gzip level used:  {level} (mtime=0; picked for size)")
    size_delta = len(out) - len(original)
    print(f"Size delta:       {size_delta:+d} bytes")
    if size_delta > 0:
        print(
            "WARNING: still larger than original — CDmage will truncate if you force import.\n"
            "  Re-extract Makou FIELD.BIN, re-apply stub, re-compress; or import with relocate\n"
            "  only if your ISO tool can grow the file without truncate.",
            file=sys.stderr,
        )
    elif size_delta < 0:
        print("Shorter than original — CDmage 'pad with zeros?' → Yes.")

    return dst


def main() -> None:
    if len(sys.argv) < 3:
        print(
            f"Usage: {sys.argv[0]} <FIELD.BIN.dec.patched> <original FIELD.BIN> [output]",
            file=sys.stderr,
        )
        sys.exit(1)

    src_dec = Path(sys.argv[1]).expanduser().resolve()
    original = Path(sys.argv[2]).expanduser().resolve()
    dst = Path(sys.argv[3]).expanduser().resolve() if len(sys.argv) > 3 else None

    for p in (src_dec, original):
        if not p.is_file():
            print(f"Error: not found: {p}", file=sys.stderr)
            sys.exit(1)

    compress_field_bin(src_dec, original, dst)


if __name__ == "__main__":
    main()
