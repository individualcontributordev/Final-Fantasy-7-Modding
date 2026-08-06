#!/usr/bin/env python3
"""Compare two PSX FIELD map files after LZS + section parse.

When to use:
  - Decide if two DATs differ in scripts vs only dialog padding / compression.
  - Single-disc multi-disc map collisions; checks after inject.

Not for: extract/write ISO (extract_field_dat / put_field_dat), FIELD.BIN engine.

Exit: 0 = identical or pad-only; 2 = meaningful change.

Examples:
  python3 scripts/compare_field_dat.py a.DAT b.DAT
  python3 scripts/compare_field_dat.py csr:1 csr:2 --field DEL1 -o /tmp/del1.md
  python3 scripts/compare_field_dat.py --batch-collisions

Sides: path | pristine:N | csr:N | file:PATH
See scripts/README.md. Env: FF7_PRISTINE_DIR, FF7_CSR_ROOT.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from disc_sources import (  # noqa: E402
    ROOT,
    field_iso_path,
    load_csr_image,
    load_pristine_image,
    normalize_field_name,
)
from field_compare import compare_bytes, format_diff_report  # noqa: E402
from psx_mode2_iso import extract_file  # noqa: E402

COLLISION_MAPS = [
    "BLACKBGB", "BUGIN1A", "COS_BTM", "COS_BTM2", "DEL1",
    "JUNAIR2", "LOST2", "NIVGATE", "RCKTIN2", "RCKTIN7",
]
_img_cache: dict[tuple[str, int], bytes] = {}


def _image(kind: str, disc: int) -> bytes:
    key = (kind, disc)
    if key not in _img_cache:
        loader = load_pristine_image if kind == "pristine" else load_csr_image
        _img_cache[key] = bytes(loader(disc))
    return _img_cache[key]


def resolve_side(spec: str, field: str | None) -> tuple[bytes, str]:
    if spec.startswith("file:"):
        path = Path(spec[5:]).expanduser()
        return path.read_bytes(), str(path)
    if ":" in spec and not Path(spec).exists():
        kind, d_s = spec.split(":", 1)
        kind = kind.lower()
        try:
            disc = int(d_s)
        except ValueError as e:
            raise SystemExit(f"bad side {spec!r}") from e
        if kind not in ("pristine", "csr") or disc not in (1, 2, 3):
            raise SystemExit(f"bad side {spec!r}")
        if not field:
            raise SystemExit("--field required with pristine:/csr:")
        name = normalize_field_name(field)
        data = extract_file(_image(kind, disc), field_iso_path(name))
        return data, f"{kind}:D{disc}:{name}"
    path = Path(spec).expanduser()
    if not path.is_file():
        raise SystemExit(f"missing file: {path}")
    return path.read_bytes(), str(path)


def run_one(left: str, right: str, field: str | None, out: Path | None) -> int:
    a, la = resolve_side(left, field)
    b, lb = resolve_side(right, field)
    diff = compare_bytes(a, b, a_label=la, b_label=lb)
    print(format_diff_report(diff))
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(format_diff_report(diff), encoding="utf-8")
        print(f"Wrote {out}", file=sys.stderr)
    return 0 if diff.is_innocuous() else 2


def run_batch(out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows, worst = [], 0
    for name in COLLISION_MAPS:
        print(f"=== {name} CSR D1 vs CSR D2 ===", flush=True)
        a, la = resolve_side("csr:1", name)
        b, lb = resolve_side("csr:2", name)
        p1, _ = resolve_side("pristine:1", name)
        p2, _ = resolve_side("pristine:2", name)
        d12 = compare_bytes(a, b, a_label=la, b_label=lb)
        d1p = compare_bytes(p1, a, a_label=f"pristine:D1:{name}", b_label=la)
        d2p = compare_bytes(p2, b, a_label=f"pristine:D2:{name}", b_label=lb)
        report = format_diff_report(d12)
        report += "\n## vs pristine (same disc)\n\n"
        report += (
            f"- pristine D1 vs CSR D1: `{d1p.classification}` "
            f"(scripts_id={d1p.scripts_identical}, pad {d1p.text_pad})\n"
            f"- pristine D2 vs CSR D2: `{d2p.classification}` "
            f"(scripts_id={d2p.scripts_identical}, pad {d2p.text_pad})\n"
        )
        path = out_dir / f"{name.lower()}-csr-d1-vs-d2.md"
        path.write_text(report, encoding="utf-8")
        print(f"  class={d12.classification} diffs={len(d12.script_diffs)} → {path}", flush=True)
        rows.append((name, d12, d1p, d2p))
        if not d12.is_innocuous():
            worst = 2
    lines = [
        "# CSR multi-disc field collisions — structured compare",
        "",
        "Tool: `python3 scripts/compare_field_dat.py --batch-collisions`",
        "",
        "| Map | CSR D1 vs D2 | script slots | text content | pad Δ | D1 vs pris | D2 vs pris | verdict |",
        "|-----|--------------|-------------:|-------------:|------:|------------|------------|---------|",
    ]
    for name, d12, d1p, d2p in rows:
        verd = "innocuous" if d12.is_innocuous() else "real collision — pick CSR disc"
        lines.append(
            f"| {name} | `{d12.classification}` | {len(d12.script_diffs)} | "
            f"{len(d12.text_content_diff_ids)} | {d12.text_pad[1]-d12.text_pad[0]} | "
            f"`{d1p.classification}` | `{d2p.classification}` | {verd} |"
        )
    lines += ["", "## Per-map reports", ""] + [
        f"- [{n}]({n.lower()}-csr-d1-vs-d2.md)" for n, *_ in rows
    ]
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSummary: {out_dir / 'README.md'}")
    return worst


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("left", nargs="?", help="left path or pristine:N / csr:N")
    ap.add_argument("right", nargs="?", help="right path or pristine:N / csr:N")
    ap.add_argument("--field", "-f", help="map name with pristine:/csr: (e.g. DEL1)")
    ap.add_argument("-o", "--output", type=Path, help="markdown report path")
    ap.add_argument("--batch-collisions", action="store_true",
                    help="CSR D1 vs D2 for all known multi-disc CSR maps")
    ap.add_argument("--out-dir", type=Path,
                    default=ROOT / "docs/findings/field-collisions-2026-08-06")
    args = ap.parse_args()
    if args.batch_collisions:
        return run_batch(args.out_dir)
    if not args.left or not args.right:
        ap.error("left and right required (or --batch-collisions)")
    return run_one(args.left, args.right, args.field, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
