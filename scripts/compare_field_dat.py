#!/usr/bin/env python3
"""Compare PSX FIELD/*.DAT files (opcodes, sections, text pad vs content).

Examples:
  # two local DAT files
  python scripts/compare_field_dat.py a.DAT b.DAT

  # same field from pristine D1 vs CSR D1
  python scripts/compare_field_dat.py --field DEL1 --left pristine:1 --right csr:1

  # CSR D1 vs CSR D2 (multi-disc collision check)
  python scripts/compare_field_dat.py --field DEL1 --left csr:1 --right csr:2

  # batch the 10 D1+D2 CSR collision stems
  python scripts/compare_field_dat.py --batch-collisions

Labels: pristine:N | csr:N | file:PATH | N is disc 1|2|3
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_layer import apply_layer  # noqa: E402
from field_compare import compare_bytes, format_diff_report  # noqa: E402
from psx_mode2_iso import extract_file  # noqa: E402

PRISTINE = {
    1: ROOT / "workspace/pristine/FINALFANTASY7_D1.bin",
    2: ROOT / "workspace/pristine/FINALFANTASY7_D2.bin",
    3: ROOT / "workspace/pristine/FINALFANTASY7_D3.bin",
}
CSR_LAYER = {
    1: Path("/Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json"),
    2: Path("/Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc2.layer.json"),
    3: Path("/Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc3.layer.json"),
}
# Known multi-disc CSR collision stems (see docs/findings/2026-08-06-csr-multi-disc-field-edits.md)
COLLISION_STEMS = [
    "BLACKBGB", "BUGIN1A", "COS_BTM", "COS_BTM2", "DEL1",
    "JUNAIR2", "LOST2", "NIVGATE", "RCKTIN2", "RCKTIN7",
]

_img_cache: dict[tuple[str, int], bytes] = {}


def _load_image(kind: str, disc: int) -> bytes:
    key = (kind, disc)
    if key in _img_cache:
        return _img_cache[key]
    p = PRISTINE[disc]
    if not p.is_file():
        raise SystemExit(f"missing pristine disc image: {p}")
    img = bytearray(p.read_bytes())
    if kind == "csr":
        layer_path = CSR_LAYER[disc]
        if not layer_path.is_file():
            raise SystemExit(f"missing CSR layer: {layer_path}")
        apply_layer(img, json.loads(layer_path.read_text()))
    _img_cache[key] = bytes(img)
    return _img_cache[key]


def resolve_side(spec: str, field: str | None) -> tuple[bytes, str]:
    """Return (dat_bytes, label)."""
    if spec.startswith("file:"):
        path = Path(spec[5:]).expanduser()
        return path.read_bytes(), str(path)
    if ":" in spec and not Path(spec).exists():
        kind, d_s = spec.split(":", 1)
        kind = kind.lower()
        disc = int(d_s)
        if kind not in ("pristine", "csr") or disc not in (1, 2, 3):
            raise SystemExit(f"bad side spec {spec!r} (want pristine:N|csr:N|file:PATH)")
        if not field:
            raise SystemExit("--field required with pristine:/csr: sides")
        stem = field.upper().removesuffix(".DAT")
        iso_path = f"FIELD/{stem}.DAT"
        data = extract_file(_load_image(kind, disc), iso_path)
        return data, f"{kind}:D{disc}:{stem}"
    # bare path
    path = Path(spec).expanduser()
    return path.read_bytes(), str(path)


def run_one(left_spec: str, right_spec: str, field: str | None, out: Path | None) -> int:
    a, la = resolve_side(left_spec, field)
    b, lb = resolve_side(right_spec, field)
    diff = compare_bytes(a, b, a_label=la, b_label=lb)
    report = format_diff_report(diff)
    print(report)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report)
        print(f"Wrote {out}", file=sys.stderr)
    # exit 0 identical/pad, 2 meaningful
    return 0 if diff.is_innocuous() else 2


def run_batch_collisions(out_dir: Path) -> int:
    """CSR D1 vs CSR D2 for each known collision stem."""
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    worst = 0
    for stem in COLLISION_STEMS:
        print(f"=== {stem} CSR D1 vs CSR D2 ===", flush=True)
        a, la = resolve_side("csr:1", stem)
        b, lb = resolve_side("csr:2", stem)
        # also pristine same-disc baselines for context
        p1, _ = resolve_side("pristine:1", stem)
        p2, _ = resolve_side("pristine:2", stem)
        d12 = compare_bytes(a, b, a_label=la, b_label=lb)
        d1p = compare_bytes(p1, a, a_label=f"pristine:D1:{stem}", b_label=la)
        d2p = compare_bytes(p2, b, a_label=f"pristine:D2:{stem}", b_label=lb)
        report = format_diff_report(d12)
        report += "\n## vs pristine (same disc)\n\n"
        report += (
            f"- pristine D1 vs CSR D1: `{d1p.classification}` "
            f"(scripts_id={d1p.scripts_identical}, text_content={d1p.texts_content_same}, "
            f"pad {d1p.text_pad[0]}→{d1p.text_pad[1]})\n"
        )
        report += (
            f"- pristine D2 vs CSR D2: `{d2p.classification}` "
            f"(scripts_id={d2p.scripts_identical}, text_content={d2p.texts_content_same}, "
            f"pad {d2p.text_pad[0]}→{d2p.text_pad[1]})\n"
        )
        path = out_dir / f"{stem.lower()}-csr-d1-vs-d2.md"
        path.write_text(report)
        print(f"  class={d12.classification} script_diffs={len(d12.script_diffs)} "
              f"text_content_diffs={len(d12.text_content_diff_ids)} "
              f"pad={d12.text_pad} → {path}", flush=True)
        rows.append((stem, d12, d1p, d2p))
        if not d12.is_innocuous():
            worst = 2

    # summary table
    lines = [
        "# CSR multi-disc field collisions — structured compare",
        "",
        "CSR D1 vs CSR D2 for stems edited on both discs.",
        "Tool: `scripts/compare_field_dat.py --batch-collisions`",
        "",
        "| Field | CSR D1 vs D2 | script slots differ | text content differ | text pad Δ | D1 CSR vs pris | D2 CSR vs pris | verdict |",
        "|-------|--------------|--------------------:|--------------------:|-----------:|----------------|----------------|---------|",
    ]
    for stem, d12, d1p, d2p in rows:
        verd = (
            "innocuous (pad/identical)"
            if d12.is_innocuous()
            else "REAL collision — pick prefer disc"
        )
        lines.append(
            f"| {stem} | `{d12.classification}` | {len(d12.script_diffs)} | "
            f"{len(d12.text_content_diff_ids)} | {d12.text_pad[1]-d12.text_pad[0]} | "
            f"`{d1p.classification}` | `{d2p.classification}` | {verd} |"
        )
    lines += ["", "## Per-field reports", ""]
    for stem, *_ in rows:
        lines.append(f"- [{stem}]({stem.lower()}-csr-d1-vs-d2.md)")
    summary = out_dir / "README.md"
    summary.write_text("\n".join(lines) + "\n")
    print(f"\nSummary: {summary}")
    return worst


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("left", nargs="?", help="left DAT path or pristine:N / csr:N")
    ap.add_argument("right", nargs="?", help="right DAT path or pristine:N / csr:N")
    ap.add_argument("--field", "-f", help="FIELD stem (e.g. DEL1) when using pristine:/csr:")
    ap.add_argument("-o", "--output", type=Path, help="write markdown report")
    ap.add_argument(
        "--batch-collisions",
        action="store_true",
        help="compare all 10 multi-disc CSR stems (CSR D1 vs D2)",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "docs/findings/field-collisions-2026-08-06",
        help="batch output directory",
    )
    args = ap.parse_args()
    if args.batch_collisions:
        return run_batch_collisions(args.out_dir)
    if not args.left or not args.right:
        ap.error("left and right required (or --batch-collisions)")
    return run_one(args.left, args.right, args.field, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
