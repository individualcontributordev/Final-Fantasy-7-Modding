#!/usr/bin/env python3
"""Sweep AceZephyr/wmsim manip scripts over an IGT window and write human reports.

World-map RNG is seeded from IGT (seconds). Each route replays a speedrun path
and keeps IGTs that 0-enc, 1-enc, or hit a target formation.

  python3 scripts/wmsim_generate_igts.py --start 0:30:00 --end 0:32:00

Writes PlayStation (psx/) and PC (pc/) wait-clock tables. Same RNG; load
offsets differ (PSX ~3s, PC ~0s). Pass --platforms psx or --platforms pc for one.

Needs ./external/wmsim (git clone). Results go under workspace/ (gitignored).
Disc 1 Skip is skipped unless --include-d1s (very slow per second).
"""

from __future__ import annotations

import argparse
import functools
import importlib.util
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WMSIM_ROOT = REPO_ROOT / "external" / "wmsim"
MANIPS_DIR = WMSIM_ROOT / "manips"

# Wait clock = world-map seed IGT minus this load. RNG itself is the same;
# only the on-screen timer you aim for changes. Per-route overrides match
# AceZephyr's manips (beachplugs uses 5s on PSX; pc_manip used 2s on PC).
PLATFORMS = {
    "psx": {
        "label": "PlayStation",
        "default_load": 3,
        "route_load": {"beachplugs": 5},
    },
    "pc": {
        "label": "PC (1998)",
        "default_load": 0,
        "route_load": {"pc_manip": 2},
    },
}

KNOWN_FORMATIONS = {
    56: "Grasslands chocobo (catchable)",
    65: "Junon area (pc_manip target)",
    92: "Beachplug 3x",
    93: "Beachplug 4x",
    94: "Beachplug SIDE",
}


def parse_clock(text: str) -> int:
    parts = [int(p) for p in text.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    raise argparse.ArgumentTypeError(f"expected H:MM:SS or MM:SS, got {text!r}")


def format_clock(total_seconds: int) -> str:
    if total_seconds < 0:
        return f"-{format_clock(-total_seconds)}"
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours}:{minutes:02d}:{seconds:02d}"


ARM_SWING_FRAMES = 15

# Upstream construct_arm_swings() subtracts 8 frames from the first cue so the
# menu lands mid-check rather than on its boundary.
FIRST_SWING_LEAD_FRAMES = 8


def frames_to_arm_swings(abs_frames: list[int]) -> tuple[list[float], list[float]]:
    """Absolute movement frames -> (relative, absolute) arm swings.

    Mirrors construct_arm_swings() in the wmsim manip scripts: 15 frames per
    swing, first cue counted from route start, later cues counted from the
    previous menu.
    """
    if not abs_frames:
        return [], []
    gaps = [abs_frames[0] - FIRST_SWING_LEAD_FRAMES]
    for prev, current in zip(abs_frames, abs_frames[1:]):
        gaps.append(current - prev)
    to_swings = lambda values: [round(v / ARM_SWING_FRAMES, 1) for v in values]
    return to_swings(gaps), to_swings(abs_frames)


def platform_load(platform: str, route_id: str) -> int:
    spec = PLATFORMS[platform]
    return spec["route_load"].get(route_id, spec["default_load"])


def clock_after_load(seed_igt: int, load: int) -> str:
    return format_clock(seed_igt - load)


_MANIP_CACHE = {}


def load_manip(stem: str):
    cached = _MANIP_CACHE.get(stem)
    if cached is not None:
        return cached
    path = MANIPS_DIR / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(f"wmsim_manip_{stem.replace('-', '_')}", path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _MANIP_CACHE[stem] = mod
    return mod


def _ensure_tabulate_stub() -> None:
    # Manip scripts import tabulate only to print; we format reports ourselves.
    if "tabulate" in sys.modules:
        return
    import types
    stub = types.ModuleType("tabulate")
    stub.tabulate = lambda *args, **kwargs: ""
    sys.modules["tabulate"] = stub


def _ensure_wmsim_on_path() -> None:
    _ensure_tabulate_stub()
    root = str(WMSIM_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def _pad_row(cells: list[str], widths: list[int]) -> str:
    return "  ".join(cell.ljust(width) for cell, width in zip(cells, widths))


GLOBAL_HOWTO = """\
WHAT THESE FILES ARE
--------------------
Each file lists In-Game Timer (IGT) values where a specific world-map route works.
wmsim replays the exact walk path speedrunners use and checks whether you get the
desired outcome (no battle, one late battle, a specific formation, etc.).

These are WORLD MAP routes only. Field/dungeon RNG is not simulated.

PSX vs PC
---------
World-map RNG is seeded from IGT the same way on both. Load time differs:
  PSX: usually ~3s (beachplugs uses 5s). Use the psx/ folder.
  PC:  usually ~0s (Junon formation-65 manip uses 2s). Use the pc/ folder.

Wait clock is already adjusted. Do not add load time yourself.

The "Junon grass — force formation 65" segment comes from AceZephyr's
pc_manip.py. Despite that filename it is generated for BOTH platforms; the
name does not mean "PC-only".

ONE FILE PER GAME SEGMENT
-------------------------
Each file covers one stretch of the run and holds every outcome for it — zero
encounters, one late encounter, and target formations — in a single table sorted
by Wait clock. Open the file for the segment you are about to run and scroll to
your split time.

HOW TO USE ANY ROW (the short version)
--------------------------------------
1. Open psx/ or pc/ depending on what you play.
2. Open the file for the segment you are running.
3. Scroll to your Wait clock, then pick a row you can execute.
4. Do the Setup inputs, then walk, opening the menu at any Arm swings cues.

ARM SWINGS (the timing unit for mid-route menus)
------------------------------------------------
Routes that need menus while walking give the cue as ARM SWINGS, not seconds.
One arm swing = 15 movement frames (wmsim's construct_arm_swings divides by 15).

Numbers are cumulative from the previous cue:
  [38.3, 10.2]  =  menu after 38.3 swings, then 10.2 swings later, menu again.

The first cue is counted 8 frames early on purpose, so the menu lands inside the
encounter-check window instead of on its boundary.

WHY MULTIPLE ROWS FOR THE SAME CLOCK?
-------------------------------------
RNG can be reached with different button setups (extra left taps, opening the menu
at different times). Same Wait clock may appear on several lines — pick the setup
you can execute; fewer menus is usually easier.

FILES IN THIS FOLDER
--------------------
INDEX.txt          — overview (start here)
HOW_TO_USE.txt     — this guide
psx/               — PlayStation wait clocks, one .txt per segment
pc/                — PC wait clocks, one .txt per segment
jsonl/all.jsonl    — machine-readable rows (includes platform + section)
meta.json          — sweep window and timing
"""


UNIFIED_HEADERS = ["Wait clock", "Seed IGT", "Outcome", "Setup", "Arm swings", "Fight", "Detail"]

EMPTY_CELL = "-"

COLUMN_HELP = """\
HOW TO READ A ROW
-----------------
  Wait clock   IGT on screen when you leave for this segment. This is what you wait for.
  Seed IGT     Internal: when world-map RNG seeds (wait clock + load time).
  Outcome      "0 enc" = no battles, "1 enc" = one late battle, otherwise the formation you get.
  Setup        Inputs before you start walking.
  Arm swings   Mid-route menu cues. 15 movement frames per swing, each counted from the
               previous cue. "-" means no menus while walking.
  Fight        The battle you will get. "none" on 0-enc rows.
  Detail       Extra reference: menu frames, encounter-check windows, or walk frames.

Rows are sorted by Wait clock, so scroll to your split time and take the first row
you can execute. 0-enc rows are listed before 1-enc rows at the same clock."""


SECTION_GUIDES: dict[str, dict] = {
    "midgar_to_choco_ranch": {
        "when": "You have just left Midgar and are walking to the Chocobo Farm.",
        "zero": "No battles at all. Needs menus while walking (see Arm swings).",
        "one": "One battle, but late (700+ walk frames) so you are nearly at the farm. No mid-route menus.",
        "setup": "\"2left, adj -5\" = two extra Left taps, then 5 Down taps. Positive adj = start menus instead.",
        "steps": [
            "Leave Midgar when the IGT shows the Wait clock.",
            "Do the Setup inputs before you start walking.",
            "On 0-enc rows, open the menu at each Arm swings cue while walking.",
            "On 1-enc rows, just walk; the one fight comes near the end.",
        ],
    },
    "chocobo_ranch_catch": {
        "when": "At the Chocobo Farm, you want the catchable chocobo encounter (formation 56).",
        "setup": "\"spin 2.5\" = spin to the 2.5 mark and open the menu there. \"spin 0\" = no menu, just walk.",
        "steps": [
            "Enter the world map at the Wait clock.",
            "Do the spin/menu in the Setup column.",
            "Walk on chocobo tracks until the fight.",
        ],
    },
    "mines_to_junon": {
        "when": "Leaving Mythril Mines, heading to Junon.",
        "zero": "No battles. Zolom-box start plus arm-swing menus.",
        "one": "One battle in the last quarter of the walk, start inputs only.",
        "setup": "\"low pattern\" / \"high pattern\" are the two known Zolom-box frame timings.",
        "steps": [
            "Leave the mines at the Wait clock.",
            "Use the Zolom-box pattern named in Setup.",
            "On 0-enc rows, menu at each Arm swings cue.",
        ],
    },
    "junon_formation_65": {
        "when": "Junon grass — you specifically want formation 65 as the first battle.",
        "setup": "\"Left+L1\" or \"Up/Down\" held during the free frames at spawn.",
        "steps": [
            "Enter the world map in the Zolom box at the Wait clock.",
            "Hold the direction in Setup through the free frames.",
            "Walk until the first battle.",
        ],
    },
    "beachplugs": {
        "when": "After exiting the buggy near Costa del Sol — you want a Beachplug fight.",
        "setup": "\"2 menu\" = open and close the menu twice before moving.",
        "steps": [
            "Exit the buggy at the Wait clock.",
            "Do the start menus in Setup.",
            "Walk the beach/grass stripe until the fight.",
            "Outcome 3x / 4x / SIDE is the formation layout. Detail \"best\" marks the pruned winner.",
        ],
    },
    "corel_to_bronco": {
        "when": "North Corel, heading to the Tiny Bronco.",
        "zero": "No battles, using arm-swing menus only.",
        "one": "One late battle, start menus only.",
        "setup": "\"-\" means no start input. \"2 start menu\" means two menus before walking.",
        "steps": [
            "Leave at the Wait clock.",
            "On 0-enc rows, menu at each Arm swings cue during the walk.",
        ],
    },
    "bronco_to_corel": {
        "when": "Tiny Bronco has just spawned after Palmer; sailing back toward Corel.",
        "zero": "No battles across 33 encounter checks.",
        "one": "One late battle.",
        "setup": "\"line 3\" = the third bronco spawn-line hold length. Match the line you actually use.",
        "steps": [
            "Spawn on the bronco at the Wait clock.",
            "Pick the row matching your spawn line.",
            "On 0-enc rows, menu at each Arm swings cue.",
        ],
    },
    "nibel_to_rocket_town": {
        "when": "Leaving Mt. Nibel / Nibelheim for Rocket Town.",
        "zero": "No battles for the whole 22-check walk.",
        "one": "One battle in the last quarter of the walk.",
        "setup": "\"Hold, 1 menu\" = hold Left/Right through the 13 free frames, then one menu. "
                 "\"Delay\" = do not hold.",
        "steps": [
            "Enter the world map at the Wait clock.",
            "Do the hold/delay and start menus in Setup.",
            "Walk to Rocket Town. No mid-route menus are needed on this segment.",
        ],
    },
    "cota_to_icicle_inn": {
        "when": "City of the Ancients to Icicle Inn across the snow.",
        "zero": "No battles over ~880 movement frames, using arm swings.",
        "one": "One late battle with start inputs only. Rare here, because the route is long.",
        "setup": "\"hold, adj -2\" = hold 13 frames then two Down taps. Positive adj = extra start menus.",
        "steps": [
            "Leave CotA at the Wait clock.",
            "Do the hold/delay and start adjustment in Setup.",
            "On 0-enc rows, menu at each Arm swings cue on the snow walk.",
        ],
    },
    "disc1_skip": {
        "when": "Disc 1 Skip chocobo path from Kalm.",
        "setup": "Summary only — this sweep records which RNG offsets worked per path segment.",
        "steps": [
            "Use AceZephyr's d1s tooling or community sheets for in-run execution.",
        ],
    },
}


def outcome_rank(outcome: str) -> int:
    return {"0 enc": 0, "1 enc": 1}.get(outcome, 0)


def unified_row(route: dict, rec: dict) -> list[str]:
    cells = route["unify"](rec)
    return [
        rec["clock"],
        format_clock(rec["seed_igt"]),
        cells.get("outcome", route["outcome"]),
        cells.get("setup") or EMPTY_CELL,
        cells.get("arm") or EMPTY_CELL,
        cells.get("fight") or "none",
        cells.get("detail") or "",
    ]


def describe_row(row: list[str]) -> str:
    clock, _seed, outcome, setup, arm, fight, _detail = row
    parts = [f"At {clock} you can get {outcome}"]
    if setup != EMPTY_CELL:
        parts.append(f"setup: {setup}")
    if arm != EMPTY_CELL:
        parts.append(f"menu at arm swings {arm}")
    if fight != "none":
        parts.append(f"fight: {fight}")
    return ". ".join(parts) + "."


def build_section_guide(section: dict, rows: list[list[str]]) -> str:
    guide = SECTION_GUIDES.get(section["id"], {})
    lines = ["", "WHEN YOU USE THIS", "-----------------", guide.get("when", section["title"])]

    outcomes = {row[2] for row in rows}
    meanings = []
    if guide.get("zero"):
        meanings.append(f"  0 enc   {guide['zero']}")
    if guide.get("one"):
        meanings.append(f"  1 enc   {guide['one']}")
    for outcome in sorted(o for o in outcomes if o not in ("0 enc", "1 enc")):
        meanings.append(f"  {outcome:<7} target formation row.")
    if meanings:
        lines.extend(["", "WHAT THE OUTCOME COLUMN MEANS", "-----------------------------", *meanings])

    lines.extend(["", COLUMN_HELP])
    if guide.get("setup"):
        lines.extend(["", "READING THE SETUP COLUMN", "------------------------", guide["setup"]])

    if guide.get("steps"):
        lines.extend(["", "WHAT TO DO IN-GAME", "------------------"])
        for i, step in enumerate(guide["steps"], 1):
            lines.append(f"{i}. {step}")

    if rows:
        lines.extend(["", "EXAMPLE ROW FROM THIS SWEEP", "---------------------------", describe_row(rows[0])])
    lines.append("")
    return "\n".join(lines)


def write_section_report(
    path: Path,
    section: dict,
    title: str,
    rows: list[list[str]],
    extra_note: str = "",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [title, build_section_guide(section, rows)]
    if extra_note:
        lines.extend([extra_note, ""])
    if not rows:
        lines.extend(["No usable IGTs in this time window.", ""])
        path.write_text("\n".join(lines), encoding="utf-8")
        return

    widths = [len(h) for h in UNIFIED_HEADERS]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    lines.extend(["RESULTS", "-------", ""])
    lines.append(_pad_row(UNIFIED_HEADERS, widths))
    lines.append(_pad_row(["-" * w for w in widths], widths))
    for row in rows:
        lines.append(_pad_row(row, widths))
    lines.extend(["", f"{len(rows)} row(s) in this window.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def formation_label(battle_id) -> str:
    if battle_id is None:
        return ""
    name = KNOWN_FORMATIONS.get(int(battle_id))
    if name:
        return f"{battle_id} ({name})"
    return str(battle_id)


def igt_range(start: int, end: int, load: int) -> range:
    # Match upstream: loop seeded IGT = displayed clock + load.
    return range(start + load, end + load)


# --- workers (must be top-level for ProcessPoolExecutor) ---

def worker_midgar_1enc(igt: int):
    _ensure_wmsim_on_path()
    mod = load_manip("midgar_choco_1enc")
    return igt, mod.run_for_igt(igt)


def worker_midgar_0enc(igt: int):
    _ensure_wmsim_on_path()
    mod = load_manip("midgar_choco_0enc")
    return igt, mod.run_for_igt(igt)


def worker_nibel(igt: int):
    _ensure_wmsim_on_path()
    mod = load_manip("nibel_to_rocket_town")
    hits = []
    for hold in (True, False):
        for menus in range(mod.MAXMENUS + 1):
            if mod.run(igt, hold, menus):
                hits.append(["Hold" if hold else "Delay", menus])
                break
    return igt, hits


def worker_mines(igt: int):
    _ensure_wmsim_on_path()
    mod = load_manip("mines_to_junon")
    rows = []
    for pattern_key in mod.PATTERNS:
        result = mod.run_for_igt_pattern(igt, pattern_key)
        if result:
            rows.extend(result)
    return igt, rows


def worker_corel_bronco(igt: int):
    _ensure_wmsim_on_path()
    mod = load_manip("corel_to_bronco")
    return igt, mod.run_for_igt(igt)


def worker_bronco_corel(igt: int):
    _ensure_wmsim_on_path()
    mod = load_manip("bronco_to_corel")
    return igt, mod.run_for_igt(igt)


def worker_choco_ranch(igt: int):
    _ensure_wmsim_on_path()
    mod = load_manip("choco_ranch")
    return igt, mod.run_second(igt)


def worker_pc_manip(igt: int):
    _ensure_wmsim_on_path()
    mod = load_manip("pc_manip")
    hit_left, s_left = mod.run(igt, True)
    if hit_left.battle_id in mod.TARGET_ENCOUNTERS:
        return igt, ("Left+L1", hit_left.battle_id, hit_left.preempt, s_left.walkframes)
    hit_ud, s_ud = mod.run(igt, False)
    if hit_ud.battle_id in mod.TARGET_ENCOUNTERS:
        return igt, ("Up/Down", hit_ud.battle_id, hit_ud.preempt, s_ud.walkframes)
    return igt, None


def worker_icicle(igt: int):
    _ensure_wmsim_on_path()
    mod = load_manip("icicle-inn-armswings")
    return igt, mod.run_for_igt(igt)


def worker_beachplugs(igt: int):
    _ensure_wmsim_on_path()
    mod = load_manip("beachplugs")
    return igt, mod.run_igt(igt)


def worker_d1s(igt: int):
    _ensure_wmsim_on_path()
    mod = load_manip("d1s")
    return igt, mod.run_for_igt(igt)


def map_pool(worker, igts: list[int], workers: int):
    if not igts:
        return []
    results = []
    worker_count = max(1, min(workers, len(igts)))
    with ProcessPoolExecutor(max_workers=worker_count) as pool:
        futures = {pool.submit(worker, igt): igt for igt in igts}
        done = 0
        total = len(futures)
        for future in as_completed(futures):
            done += 1
            igt = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                print(f"  IGT {format_clock(igt)} failed: {exc}", flush=True)
            if done % 30 == 0 or done == total:
                print(f"  {done}/{total}", flush=True)
    results.sort(key=lambda item: item[0])
    return results


def collect_midgar_1enc(igts, workers):
    records = []
    for igt, rows in map_pool(worker_midgar_1enc, igts, workers):
        for row in rows:
            records.append({
                "seed_igt": igt,
                "left": row[2],
                "adjust": row[3],
                "walkframes": row[4],
                "formation": row[5],
                "preempt": bool(row[6]),
            })
    return records


def collect_midgar_0enc(igts, workers):
    records = []
    for igt, rows in map_pool(worker_midgar_0enc, igts, workers):
        for row in rows:
            menu_frames = list(row[4]) if row[4] else []
            arm_swings_rel, arm_swings_abs = frames_to_arm_swings(menu_frames)
            records.append({
                "seed_igt": igt,
                "left": row[2],
                "adj": row[3],
                "menu_frames": menu_frames,
                "menu_count": len(menu_frames),
                "arm_swings_rel": str(arm_swings_rel),
                "arm_swings_abs": str(arm_swings_abs),
            })
    return records


def collect_nibel(igts, workers):
    records = []
    for igt, rows in map_pool(worker_nibel, igts, workers):
        for row in rows:
            records.append({
                "seed_igt": igt,
                "start": row[0],
                "menus": row[1],
            })
    return records


def collect_mines(igts, workers):
    records = []
    for igt, rows in map_pool(worker_mines, igts, workers):
        for row in rows:
            arm = row[5]
            if len(arm) > 2:
                continue
            records.append({
                "seed_igt": igt,
                "pattern": row[2],
                "enc_windows": str(row[3]),
                "arm_swings_rel": str(row[4]),
                "arm_swings_abs": str(arm),
                "menu_count": len(arm),
            })
    return records


def collect_corel_bronco(igts, workers):
    records = []
    for igt, row in map_pool(worker_corel_bronco, igts, workers):
        if row is None:
            continue
        arm = row[4]
        if len(arm) > 2:
            continue
        records.append({
            "seed_igt": igt,
            "enc_windows": str(row[2]),
            "arm_swings_rel": str(row[3]),
            "arm_swings_abs": str(arm),
            "menu_count": len(arm),
        })
    return records


def collect_bronco_corel(igts, workers):
    records = []
    for igt, rows in map_pool(worker_bronco_corel, igts, workers):
        for row in rows:
            arm = row[5]
            if len(arm) > 2:
                continue
            records.append({
                "seed_igt": igt,
                "bronco_line": row[2],
                "enc_windows": str(row[3]),
                "arm_swings_rel": str(row[4]),
                "arm_swings_abs": str(arm),
                "menu_count": len(arm),
            })
    return records


def collect_choco_ranch(igts, workers):
    records = []
    for igt, row in map_pool(worker_choco_ranch, igts, workers):
        if row is None:
            continue
        records.append({
            "seed_igt": igt,
            "walkframes": row[1],
            "spin_menus": row[4],
            "preempt": bool(row[3]),
            "formation": 56,
        })
    return records


def collect_pc_manip(igts, workers):
    records = []
    for igt, row in map_pool(worker_pc_manip, igts, workers):
        if row is None:
            continue
        direction, battle_id, preempt, walkframes = row
        records.append({
            "seed_igt": igt,
            "hold": direction,
            "formation": battle_id,
            "preempt": bool(preempt),
            "walkframes": walkframes,
        })
    return records


def collect_icicle(igts, workers):
    records = []
    for igt, rows in map_pool(worker_icicle, igts, workers):
        for row in rows:
            arm = row[6]
            if len(arm) > 4:
                continue
            records.append({
                "seed_igt": igt,
                "hold_start": bool(row[2]),
                "start_condition": row[3],
                "enc_windows": str(row[4]),
                "arm_swings_rel": str(row[5]),
                "arm_swings_abs": str(arm),
                "menu_count": len(arm),
            })
    return records


BEACHPLUG_KIND_POINTS = {"3x": 0, "4x": 150, "SIDE": -60}
BEACHPLUG_KIND_FORMATION = {"3x": 92, "4x": 93, "SIDE": 94}


def collect_beachplugs(igts, workers):
    records = []
    for igt, rows in map_pool(worker_beachplugs, igts, workers):
        for row in rows:
            records.append({
                "seed_igt": row[0],
                "menus": row[2],
                "walkframes": row[3],
                "kind": row[5],
            })
    return records


def mark_beachplug_best(records: list[dict]) -> list[dict]:
    if not records:
        return records
    _ensure_wmsim_on_path()
    mod = load_manip("beachplugs")
    rows = []
    for rec in records:
        points = BEACHPLUG_KIND_POINTS.get(rec["kind"], 0)
        rows.append([rec["seed_igt"], rec.get("clock"), rec["menus"], rec["walkframes"], points, rec["kind"]])
    pruned = [list(row) for row in rows]
    mod.prune(pruned)
    pruned_keys = {(row[0], row[2], row[3], row[5]) for row in pruned}
    out = []
    for rec in records:
        tagged = dict(rec)
        tagged["pruned_best"] = (rec["seed_igt"], rec["menus"], rec["walkframes"], rec["kind"]) in pruned_keys
        out.append(tagged)
    return out


def collect_d1s(igts, workers):
    records = []
    for igt, payload in map_pool(worker_d1s, igts, workers):
        if payload is None:
            continue
        t4, t5_up, t5_up_full, t5_three, t5, end = payload
        records.append({
            "seed_igt": igt,
            "t4_offsets": sorted(t4.keys()) if t4 else [],
            "t5_offsets": sorted(t5.keys()) if t5 else [],
            "end_offsets": sorted(end.keys()) if end else [],
            "t5_3menu_safe": t5_three,
            "end_min_menus": min((len(v) for v in end.values()), default=None) if end else None,
        })
    return records


# --- generic 1-encounter variants of the 0-enc routes ---
#
# The shipped 0-enc scripts menu around every encounter check. These variants
# instead walk the same path with only simple start inputs and keep the run if
# the single battle lands late (near the destination), like midgar_choco_1enc.

ONE_ENC_LATE_FRACTION = 0.75


def one_enc_nibel(igt, variant):
    _ensure_wmsim_on_path()
    from state import State, Battle
    from constants import Region, Ground

    hold, menus = variant
    mod = load_manip("nibel_to_rocket_town")
    total = mod.END_DANGER // 512
    state = State(igt)
    try:
        if hold:
            for _ in range(13):
                state.walk(Region.Rocket_Launch_Pad, Ground.Grass, True, movement=False)
        for _ in range(menus):
            state.walk(Region.Rocket_Launch_Pad, Ground.Grass, True, movement=False)
        while state.danger < mod.END_DANGER:
            state.walk(Region.Rocket_Launch_Pad, Ground.Grass, True)
    except Battle as battle:
        return battle, state.encounter_checks, state.walkframes, total
    return None, state.encounter_checks, state.walkframes, total


def one_enc_mines(igt, variant):
    _ensure_wmsim_on_path()
    from state import State, Battle
    from constants import Region, Ground

    mod = load_manip("mines_to_junon")
    pattern = mod.PATTERNS[variant]
    total = pattern["encChecksTotal"]
    state = State(igt)
    try:
        state.walk(Region.Junon, Ground.Grass, False, movement=False, zolombox=True)
        for _ in range(13):
            state.walk(Region.Junon, Ground.Grass, True, movement=False, zolombox=True)
        for _ in range(pattern["framesZolom"]):
            state.walk(Region.Junon, Ground.Grass, True, movement=True, zolombox=True)
        while state.encounter_checks < total:
            state.walk(Region.Junon, Ground.Grass, True)
    except Battle as battle:
        return battle, state.encounter_checks, state.walkframes, total
    return None, state.encounter_checks, state.walkframes, total


def one_enc_corel_to_bronco(igt, variant):
    _ensure_wmsim_on_path()
    from state import State, Battle

    mod = load_manip("corel_to_bronco")
    total = mod.ENCOUNTER_THRESHOLDS_TO_END
    state = State(igt)
    try:
        for _ in range(13):
            state.walk(mod.REGION, mod.GROUND, True, movement=False)
        for _ in range(variant):
            state.walk(mod.REGION, mod.GROUND, True, movement=False)
        while state.encounter_checks < total:
            state.walk(mod.REGION, mod.GROUND, True)
    except Battle as battle:
        return battle, state.encounter_checks, state.walkframes, total
    return None, state.encounter_checks, state.walkframes, total


def one_enc_bronco_to_corel(igt, variant):
    _ensure_wmsim_on_path()
    from state import State, Battle

    mod = load_manip("bronco_to_corel")
    total = mod.ENCOUNTER_THRESHOLDS_TO_END
    state = State(igt)
    try:
        for _ in range(mod.LINES[variant]):
            state.walk(mod.REGION, mod.GROUND, True, movement=False)
        state.vehicle_frac_reset()
        while state.encounter_checks < total:
            state.walk(mod.REGION, mod.GROUND, True)
    except Battle as battle:
        return battle, state.encounter_checks, state.walkframes, total
    return None, state.encounter_checks, state.walkframes, total


def one_enc_icicle(igt, variant):
    _ensure_wmsim_on_path()
    from state import State, Battle

    mod = load_manip("icicle-inn-armswings")
    hold, start_condition = variant
    frames = mod.FRAMES_OF_MOVEMENT_TO_END
    if hold:
        frames -= 13
    frames -= abs(start_condition)
    total = (frames - 140) // 17

    state = State(igt)
    try:
        if hold:
            for _ in range(13):
                state.walk(mod.REGION, mod.GROUND, True, movement=False)
        for _ in range(abs(start_condition)):
            if start_condition > 0:  # extra start menus
                state.walk(mod.REGION, mod.GROUND, True, movement=False)
            else:  # down taps
                state.walk(mod.REGION, mod.GROUND, False, movement=True)
        while state.encounter_checks < total:
            state.walk(mod.REGION, mod.GROUND, True)
    except Battle as battle:
        return battle, state.encounter_checks, state.walkframes, total
    return None, state.encounter_checks, state.walkframes, total


ONE_ENC_SPECS = {
    "nibel_to_rocket_town_1enc": {
        "run": one_enc_nibel,
        "variants": [
            ((hold, menus), f"{'Hold' if hold else 'Delay'}, {menus} menu")
            for hold in (True, False)
            for menus in range(3)
        ],
        "pc_skip": lambda label: label.startswith("Delay"),
    },
    "mines_to_junon_1enc": {
        "run": one_enc_mines,
        "variants": [("low", "low pattern"), ("high", "high pattern")],
    },
    "corel_to_bronco_1enc": {
        "run": one_enc_corel_to_bronco,
        "variants": [(menus, f"{menus} start menu") for menus in range(4)],
    },
    "bronco_to_corel_1enc": {
        "run": one_enc_bronco_to_corel,
        "variants": [(line, f"line {line}") for line in (1, 2, 3, 4)],
    },
    "icicle_inn_1enc": {
        "run": one_enc_icicle,
        "variants": [
            ((hold, adj), f"{'hold' if hold else 'delay'}, adj {adj}")
            for hold in (True, False)
            for adj in range(-3, 4)
        ],
    },
}


def worker_one_enc(route_id: str, igt: int):
    spec = ONE_ENC_SPECS[route_id]
    hits = []
    for value, label in spec["variants"]:
        battle, checks, walkframes, total = spec["run"](igt, value)
        if battle is None:
            continue
        if checks < math.ceil(total * ONE_ENC_LATE_FRACTION):
            continue
        hits.append({
            "setup": label,
            "check": checks,
            "total_checks": total,
            "walkframes": walkframes,
            "formation": battle.battle_id,
            "preempt": bool(battle.preempt),
        })
    return igt, hits


def collect_one_enc(route_id: str):
    def collect(igts, workers):
        records = []
        worker = functools.partial(worker_one_enc, route_id)
        for igt, hits in map_pool(worker, igts, workers):
            for hit in hits:
                records.append({"seed_igt": igt, **hit})
        return records

    return collect


def one_enc_route(route_id: str, section: str, title: str) -> dict:
    return {
        "id": route_id,
        "section": section,
        "title": title,
        "outcome": "1 enc",
        "collect": collect_one_enc(route_id),
        "unify": lambda r: {
            "setup": r["setup"],
            "fight": f"check {r['check']}/{r['total_checks']}, {formation_label(r['formation'])}"
                     + (" PE" if r["preempt"] else ""),
            "detail": f"{r['walkframes']} frames",
        },
        "heavy": False,
    }


ROUTES = [
    {
        "id": "midgar_choco_0enc",
        "section": "midgar_to_choco_ranch",
        "title": "Midgar → Chocobo Ranch",
        "outcome": "0 enc",
        "collect": collect_midgar_0enc,
        "unify": lambda r: {
            "setup": f"{r['left']}left, adj {r['adj']}",
            "arm": r["arm_swings_rel"],
            "detail": "menu frames " + (",".join(str(x) for x in r["menu_frames"]) or "none"),
        },
        "heavy": False,
    },
    {
        "id": "midgar_choco_1enc",
        "section": "midgar_to_choco_ranch",
        "title": "Midgar → Chocobo Ranch",
        "outcome": "1 enc",
        "collect": collect_midgar_1enc,
        "unify": lambda r: {
            "setup": f"{r['left']}, {r['adjust']}",
            "fight": formation_label(r["formation"]) + (" PE" if r["preempt"] else ""),
            "detail": f"{r['walkframes']} frames",
        },
        "heavy": False,
    },
    {
        "id": "choco_ranch",
        "section": "chocobo_ranch_catch",
        "title": "Chocobo Ranch — catch a chocobo",
        "outcome": "chocobo",
        "collect": collect_choco_ranch,
        "unify": lambda r: {
            "setup": f"spin {r['spin_menus']}",
            "fight": formation_label(56) + (" PE" if r["preempt"] else ""),
            "detail": f"{r['walkframes']} frames",
        },
        "heavy": False,
    },
    {
        "id": "mines_to_junon",
        "section": "mines_to_junon",
        "title": "Mythril Mines → Junon",
        "outcome": "0 enc",
        "collect": collect_mines,
        "unify": lambda r: {
            "setup": f"{r['pattern']} pattern",
            "arm": r["arm_swings_rel"],
            "detail": f"windows {r['enc_windows']}",
        },
        "heavy": False,
    },
    one_enc_route("mines_to_junon_1enc", "mines_to_junon", "Mythril Mines → Junon"),
    {
        "id": "pc_manip",
        "section": "junon_formation_65",
        "title": "Junon grass — force formation 65",
        "outcome": "form 65",
        "collect": collect_pc_manip,
        "unify": lambda r: {
            "setup": str(r["hold"]),
            "fight": formation_label(r["formation"]) + (" PE" if r["preempt"] else ""),
            "detail": f"{r['walkframes']} frames",
        },
        "heavy": False,
    },
    {
        "id": "beachplugs",
        "section": "beachplugs",
        "title": "Costa / buggy → Beachplugs",
        "outcome": "beachplug",
        "collect": collect_beachplugs,
        "unify": lambda r: {
            "outcome": str(r["kind"]),
            "setup": f"{r['menus']} menu",
            "fight": formation_label(BEACHPLUG_KIND_FORMATION[r["kind"]]),
            "detail": f"{r['walkframes']} frames" + (", best" if r["pruned_best"] else ""),
        },
        "heavy": False,
    },
    {
        "id": "corel_to_bronco",
        "section": "corel_to_bronco",
        "title": "North Corel → Tiny Bronco",
        "outcome": "0 enc",
        "collect": collect_corel_bronco,
        "unify": lambda r: {
            "arm": r["arm_swings_rel"],
            "detail": f"windows {r['enc_windows']}",
        },
        "heavy": False,
    },
    one_enc_route("corel_to_bronco_1enc", "corel_to_bronco", "North Corel → Tiny Bronco"),
    {
        "id": "bronco_to_corel",
        "section": "bronco_to_corel",
        "title": "Tiny Bronco spawn → Corel",
        "outcome": "0 enc",
        "collect": collect_bronco_corel,
        "unify": lambda r: {
            "setup": f"line {r['bronco_line']}",
            "arm": r["arm_swings_rel"],
            "detail": f"windows {r['enc_windows']}",
        },
        "heavy": False,
    },
    one_enc_route("bronco_to_corel_1enc", "bronco_to_corel", "Tiny Bronco spawn → Corel"),
    {
        "id": "nibel_to_rocket_town",
        "section": "nibel_to_rocket_town",
        "title": "Nibel → Rocket Town",
        "outcome": "0 enc",
        "collect": collect_nibel,
        "unify": lambda r: {"setup": f"{r['start']}, {r['menus']} menu"},
        "heavy": False,
    },
    one_enc_route("nibel_to_rocket_town_1enc", "nibel_to_rocket_town", "Nibel → Rocket Town"),
    {
        "id": "icicle_inn",
        "section": "cota_to_icicle_inn",
        "title": "City of the Ancients → Icicle Inn",
        "outcome": "0 enc",
        "collect": collect_icicle,
        "unify": lambda r: {
            "setup": f"{'hold' if r['hold_start'] else 'delay'}, adj {r['start_condition']}",
            "arm": r["arm_swings_rel"],
            "detail": f"windows {r['enc_windows']}",
        },
        "heavy": False,
    },
    one_enc_route("icicle_inn_1enc", "cota_to_icicle_inn", "City of the Ancients → Icicle Inn"),
    {
        "id": "d1s",
        "section": "disc1_skip",
        "title": "Disc 1 Skip (Kalm chocobo path)",
        "outcome": "d1s",
        "collect": collect_d1s,
        "unify": lambda r: {
            "detail": f"t4={len(r['t4_offsets'])} t5={len(r['t5_offsets'])} "
                      f"end={len(r['end_offsets'])} min end menus={r['end_min_menus']}",
        },
        "heavy": True,
    },
]

# File order follows game progression, not the compute order above.
SECTIONS = [
    {"id": "midgar_to_choco_ranch", "title": "Midgar → Chocobo Ranch"},
    {"id": "chocobo_ranch_catch", "title": "Chocobo Ranch — catch a chocobo"},
    {"id": "mines_to_junon", "title": "Mythril Mines → Junon"},
    {"id": "junon_formation_65", "title": "Junon grass — force formation 65"},
    {"id": "beachplugs", "title": "Costa / buggy → Beachplugs"},
    {"id": "corel_to_bronco", "title": "North Corel → Tiny Bronco"},
    {"id": "bronco_to_corel", "title": "Tiny Bronco spawn → Corel"},
    {"id": "nibel_to_rocket_town", "title": "Nibel → Rocket Town"},
    {"id": "cota_to_icicle_inn", "title": "City of the Ancients → Icicle Inn"},
    {"id": "disc1_skip", "title": "Disc 1 Skip (Kalm chocobo path)"},
]


def records_for_platform(
    route: dict,
    records: list[dict],
    platform: str,
    wait_start: int,
    wait_end: int,
) -> list[dict]:
    route_id = route["id"]
    load = platform_load(platform, route_id)
    out = []
    for rec in records:
        wait = rec["seed_igt"] - load
        if wait < wait_start or wait >= wait_end:
            continue
        if platform == "pc" and route_id == "nibel_to_rocket_town" and rec.get("start") == "Delay":
            continue
        pc_skip = ONE_ENC_SPECS.get(route_id, {}).get("pc_skip")
        if platform == "pc" and pc_skip and pc_skip(rec["setup"]):
            continue
        tagged = dict(rec)
        tagged["clock"] = format_clock(wait)
        tagged["wait_igt"] = wait
        tagged["platform"] = platform
        tagged["load_seconds"] = load
        tagged["route"] = route_id
        tagged["section"] = route["section"]
        tagged["outcome"] = route["outcome"]
        out.append(tagged)
    if route_id == "beachplugs":
        out = mark_beachplug_best(out)
    return out


def section_index_lines(summaries: list[dict], file_prefix: str) -> list[str]:
    lines = [
        "Rows   Section                                        File",
        "-----  ---------------------------------------------  -----",
    ]
    for item in summaries:
        rows = str(item["rows"]).rjust(5)
        lines.append(f"{rows}  {item['title']:<45}  {file_prefix}{item['id']}.txt")
    return lines


def write_index(
    out_dir: Path,
    start: int,
    end: int,
    platforms: list[str],
    per_platform: dict[str, list[dict]],
    seed_lo: int,
    seed_hi: int,
    elapsed: float,
) -> None:
    lines = [
        "wmsim IGT sweep",
        "",
        GLOBAL_HOWTO,
        "",
        "THIS SWEEP",
        "----------",
        f"Wait-clock window: {format_clock(start)} → {format_clock(end)} (end exclusive)",
        f"Seeded IGT simulated: {format_clock(seed_lo)} → {format_clock(seed_hi)} (end exclusive)",
        f"Platforms: {', '.join(platforms)}",
        f"Generator runtime: {elapsed:.1f}s",
        "",
        "Open psx/ or pc/, then the one file for the segment you are running.",
        "",
    ]
    for platform in platforms:
        lines.append(f"{PLATFORMS[platform]['label'].upper()} ({platform}/)")
        lines.extend(section_index_lines(per_platform[platform], f"{platform}/"))
        lines.append("")
    out_dir.joinpath("INDEX.txt").write_text("\n".join(lines), encoding="utf-8")
    out_dir.joinpath("HOW_TO_USE.txt").write_text(GLOBAL_HOWTO, encoding="utf-8")

    for platform in platforms:
        spec = PLATFORMS[platform]
        plat_lines = [
            f"wmsim IGT sweep — {spec['label']}",
            "",
            f"Use these Wait clocks on {spec['label']}.",
            f"Window: {format_clock(start)} → {format_clock(end)}",
            "",
            "One file per game segment. Each file holds every outcome for that segment",
            "(0 encounters, 1 late encounter, target formations), sorted by Wait clock.",
            "",
        ]
        plat_lines.extend(section_index_lines(per_platform[platform], ""))
        plat_lines.append("")
        (out_dir / platform / "INDEX.txt").write_text("\n".join(plat_lines), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=parse_clock, default=parse_clock("0:30:00"))
    parser.add_argument("--end", type=parse_clock, default=parse_clock("0:32:00"))
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output directory (default: workspace/wmsim-runs/<start>-<end>/)",
    )
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4) - 1))
    parser.add_argument("--include-d1s", action="store_true")
    parser.add_argument("--sections", nargs="*", default=None, help="Subset of section ids")
    parser.add_argument(
        "--platforms",
        nargs="*",
        default=["psx", "pc"],
        choices=["psx", "pc"],
        help="Generate wait clocks for these platforms (default: both)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not (WMSIM_ROOT / "state.py").exists():
        print(f"Missing {WMSIM_ROOT}. Clone https://github.com/AceZephyr/wmsim there.", file=sys.stderr)
        return 1
    if args.end <= args.start:
        print("--end must be after --start", file=sys.stderr)
        return 1

    platforms = list(dict.fromkeys(args.platforms))
    wanted = set(args.sections) if args.sections else None
    sections = [s for s in SECTIONS if wanted is None or s["id"] in wanted]
    active = [r for r in ROUTES if any(r["section"] == s["id"] for s in sections)]
    if not active:
        print("No routes selected.", file=sys.stderr)
        return 1

    _ensure_wmsim_on_path()

    stamp = f"{args.start:05d}-{args.end:05d}"
    out_dir = args.out or (REPO_ROOT / "workspace" / "wmsim-runs" / stamp)
    jsonl_path = out_dir / "jsonl" / "all.jsonl"
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    for platform in platforms:
        (out_dir / platform).mkdir(parents=True, exist_ok=True)

    loads = [platform_load(p, r["id"]) for p in platforms for r in active]
    seed_lo = args.start + min(loads)
    seed_hi = args.end + max(loads)
    igts = list(range(seed_lo, seed_hi))
    print(
        f"Window {format_clock(args.start)}–{format_clock(args.end)} "
        f"({len(igts)} seeded seconds, platforms={platforms}, {args.workers} workers)",
        flush=True,
    )
    print(f"Writing {out_dir}", flush=True)

    t0 = time.time()
    records_by_route = {}
    for route in active:
        if route["heavy"] and not args.include_d1s:
            records_by_route[route["id"]] = None
            print(f"skip {route['id']} (heavy; pass --include-d1s)", flush=True)
            continue
        print(f"route {route['id']}...", flush=True)
        route_t0 = time.time()
        records_by_route[route["id"]] = route["collect"](igts, args.workers)
        print(f"  {len(records_by_route[route['id']])} raw in {time.time() - route_t0:.1f}s", flush=True)

    per_platform = {platform: [] for platform in platforms}
    with jsonl_path.open("w", encoding="utf-8") as jsonl_file:
        for section in sections:
            section_routes = [r for r in active if r["section"] == section["id"]]
            skipped = all(records_by_route[r["id"]] is None for r in section_routes)
            for platform in platforms:
                sortable = []
                for route in section_routes:
                    raw = records_by_route[route["id"]]
                    if raw is None:
                        continue
                    for rec in records_for_platform(route, raw, platform, args.start, args.end):
                        jsonl_file.write(json.dumps(rec) + "\n")
                        row = unified_row(route, rec)
                        sort_key = (rec["wait_igt"], outcome_rank(row[2]), rec.get("menu_count", 0))
                        sortable.append((sort_key, row))
                sortable.sort(key=lambda item: item[0])
                rows = [row for _key, row in sortable]
                note = (
                    f"Platform: {PLATFORMS[platform]['label']}. "
                    "Wait clock is the on-screen timer; Seed IGT is when world-map RNG seeds."
                )
                if skipped:
                    note = "SKIPPED (pass --include-d1s to run; minutes per IGT)."
                write_section_report(
                    out_dir / platform / f"{section['id']}.txt",
                    section,
                    f"{section['title']}  [{PLATFORMS[platform]['label']}]",
                    rows,
                    extra_note=note,
                )
                per_platform[platform].append({
                    "id": section["id"],
                    "title": section["title"],
                    "rows": "skip" if skipped else len(rows),
                })

    meta = {
        "start": args.start,
        "end": args.end,
        "start_clock": format_clock(args.start),
        "end_clock": format_clock(args.end),
        "platforms": platforms,
        "seeded_seconds": len(igts),
        "seed_lo": seed_lo,
        "seed_hi": seed_hi,
        "workers": args.workers,
        "elapsed_seconds": time.time() - t0,
        "sections": per_platform,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    write_index(
        out_dir, args.start, args.end, platforms, per_platform, seed_lo, seed_hi, time.time() - t0
    )
    print(f"Done. Open {out_dir / 'INDEX.txt'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
