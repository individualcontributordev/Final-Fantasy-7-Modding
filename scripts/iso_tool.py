#!/usr/bin/env python3
"""List, extract and inject files inside a raw MODE2/2352 FF7 disc BIN.

  python scripts/iso_tool.py ls disc.bin
  python scripts/iso_tool.py extract disc.bin FIELD/FIELD.BIN out.bin [--dec]
  python scripts/iso_tool.py inject disc.bin FIELD/FIELD.BIN in.bin [--dec] [-o out.bin]

--dec treats the ISO file as GZIPPS: extract decompresses it, inject
recompresses the input against the file already on the disc. Inject keeps the
file's LBA and size, edits the BIN in place unless -o is given, and leaves
EDC/ECC stale: run repair_mode2_edc.py afterwards.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from compress_gzipps import compress_gzipps
from decompress_gzipps import decompress_gzipps
from psx_mode2_iso import extract_file, replace_file_padded, walk_tree


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ls").add_argument("bin", type=Path)
    for name in ("extract", "inject"):
        p = sub.add_parser(name)
        p.add_argument("bin", type=Path)
        p.add_argument("path", help="ISO path, e.g. FIELD/FIELD.BIN")
        p.add_argument("file", type=Path)
        p.add_argument("--dec", action="store_true", help="file is GZIPPS-compressed on disc")
        if name == "inject":
            p.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    img = bytearray(args.bin.read_bytes())
    if args.cmd == "ls":
        for f in sorted(walk_tree(img).values(), key=lambda f: f.path):
            if not f.path.endswith("/"):
                print(f"{f.lba}\t{f.size}\t{f.path}")
        return 0

    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw"
        raw.write_bytes(extract_file(img, args.path))
        if args.cmd == "extract":
            if args.dec:
                decompress_gzipps(raw, args.file)
            else:
                args.file.write_bytes(raw.read_bytes())
            print(f"Wrote {args.file}")
            return 0
        data = args.file.read_bytes()
        if args.dec:
            out = Path(td) / "out"
            compress_gzipps(args.file, raw, out)
            data = out.read_bytes()
        meta = replace_file_padded(img, args.path, data)
    dst = args.output or args.bin
    dst.write_bytes(img)
    print(f"Injected {len(data)} bytes into {meta.path} (slot {meta.size}); wrote {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
