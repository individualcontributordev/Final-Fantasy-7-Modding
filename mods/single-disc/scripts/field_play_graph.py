#!/usr/bin/env python3
"""Runtime field play graph for any disc .bin: which fields are actually
enterable, and via what edges.

Reuses the CFG reachability machinery from analyze_movie_reachability.py
(reachable MAPJUMP targets) plus walkmesh gateway (door/exit-line) targets
from field_gateway_targets(), same graph-building logic as
scan_csr_movie_reachability.py's build_field_graph()/reachable_field_names(),
but works on an arbitrary disc image path (not just csr:N) and reports the
field-to-field graph itself, not just the movie set.

Edges are one of:
  mapjump  - reachable (CFG-live) MAPJUMP opcode in some entity/slot
  gateway  - walkmesh exit line / door in the field's Triggers section
             (always counted as live; no polygon-connectivity analysis)

Usage:
  python3 mods/single-disc/scripts/field_play_graph.py \\
      --disc workspace/iso-extract/ff7_d1_csrplus_final.bin
  python3 mods/single-disc/scripts/field_play_graph.py --disc csr:1 --dump-edges
  python3 mods/single-disc/scripts/field_play_graph.py --disc csr:2 \\
      --entry-field-id 0 -o /tmp/d2_play_graph.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze_movie_reachability import analyze_field_bytes, field_gateway_targets  # noqa: E402
from disc_sources import load_csr_image, load_pristine_image  # noqa: E402
from scan_csr_movie_reachability import (  # noqa: E402
    ENTRY_FIELD_ID,
    MAPJUMP_FANOUT_EXCLUDE,
    _load_field_id_mapping,
    field_dat_listing,
    read_extent,
)


def load_image(spec: str) -> bytes:
    if spec.startswith("csr:"):
        return bytes(load_csr_image(int(spec.split(":", 1)[1])))
    if spec.startswith("pristine:"):
        return bytes(load_pristine_image(int(spec.split(":", 1)[1])))
    return Path(spec).expanduser().read_bytes()


def build_field_graph_detailed(
    img: bytes, fields: dict[str, tuple[int, int]]
) -> dict[str, list[tuple[int, str]]]:
    """field NAME -> list of (target field id, edge kind) tuples.

    Same source data as scan_csr_movie_reachability.build_field_graph(), but
    keeps the edge kind (mapjump/gateway) instead of collapsing to a set.
    """
    graph: dict[str, list[tuple[int, str]]] = {}
    for name, (lba, size) in fields.items():
        raw = read_extent(img, lba, size)
        edges: list[tuple[int, str]] = []
        if name.upper() not in MAPJUMP_FANOUT_EXCLUDE:
            try:
                slots = analyze_field_bytes(raw, name)
                for s in slots:
                    for tid in s.reachable_mapjump_targets():
                        edges.append((tid, "mapjump"))
            except Exception:  # noqa: BLE001
                pass
        try:
            for tid in field_gateway_targets(raw, name):
                edges.append((tid, "gateway"))
        except Exception:  # noqa: BLE001
            pass
        graph[name] = edges
    return graph


def bfs_reachable(
    fields: dict[str, tuple[int, int]],
    graph: dict[str, list[tuple[int, str]]],
    entry_field_id: int,
) -> tuple[set[str], dict[str, tuple[str, str]]]:
    """BFS from entry_field_id. Returns (reachable field names, {field ->
    (via_field, edge_kind)} predecessor map for the first edge that reached
    it, entry field itself excluded from the map)."""
    id_to_name = _load_field_id_mapping()
    name_set = set(fields)
    entry_name = id_to_name.get(entry_field_id)
    if entry_name is None or entry_name not in name_set:
        return set(name_set), {}

    visited: set[str] = set()
    came_from: dict[str, tuple[str, str]] = {}
    stack = [entry_name]
    while stack:
        cur = stack.pop()
        if cur in visited:
            continue
        visited.add(cur)
        for tid, kind in graph.get(cur, ()):
            tname = id_to_name.get(tid)
            if tname and tname in name_set and tname not in visited:
                came_from.setdefault(tname, (cur, kind))
                stack.append(tname)
    return visited, came_from


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disc", required=True, help="csr:N | pristine:N | path/to.bin")
    ap.add_argument("--entry-field-id", type=int, default=ENTRY_FIELD_ID,
                     help=f"default {ENTRY_FIELD_ID} (md1stin, Reactor 1 train platform)")
    ap.add_argument("--dump-edges", action="store_true", help="print every graph edge, not just the summary")
    ap.add_argument("-o", "--output", type=Path, help="write full JSON graph + reachability to this path")
    args = ap.parse_args()

    print(f"Loading {args.disc}...", file=sys.stderr)
    img = load_image(args.disc)
    fields = field_dat_listing(img)
    print(f"  {len(fields)} FIELD/*.DAT", file=sys.stderr)

    print("  Building field-level play graph (MAPJUMP + gateways)...", file=sys.stderr)
    graph = build_field_graph_detailed(img, fields)
    reachable, came_from = bfs_reachable(fields, graph, args.entry_field_id)
    unreachable = sorted(set(fields) - reachable)

    print(f"\n{len(reachable)}/{len(fields)} fields reachable from entry field id {args.entry_field_id}")
    print(f"{len(unreachable)} fields UNREACHABLE from entry (dead/orphaned or reached only via WORLD.BIN "
          "or other unmodeled entry points):")
    for name in unreachable:
        print(f"  [UNCONFIRMED] {name}")

    if args.dump_edges:
        print("\nEdges:")
        for name in sorted(graph):
            for tid, kind in graph[name]:
                tname = _load_field_id_mapping().get(tid, f"id={tid}")
                print(f"  [CONFIRMED] {name} --{kind}--> {tname} (field id {tid})")

    if args.output:
        id_to_name = _load_field_id_mapping()
        out = {
            "disc": args.disc,
            "entry_field_id": args.entry_field_id,
            "field_count": len(fields),
            "reachable_count": len(reachable),
            "reachable_fields": sorted(reachable),
            "unreachable_fields": unreachable,
            "came_from": {k: {"via": v[0], "edge": v[1]} for k, v in came_from.items()},
            "graph": {
                name: [{"target_id": tid, "target_name": id_to_name.get(tid), "edge": kind} for tid, kind in edges]
                for name, edges in graph.items()
            },
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"\nWrote {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
