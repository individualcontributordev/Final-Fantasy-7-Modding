#!/usr/bin/env python3
"""Extract and compare all FIELD scripts: CSR D1, CSR D2, SD stack."""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSR = Path.home() / "Final-Fantasy-7-CSR"
sys.path.insert(0, str(ROOT / "scripts"))

from apply_layer import apply_layer  # noqa: E402
from field_dat import load_field_dat, op_size  # noqa: E402
from ff7_opcodes import OPCODE_NAMES  # noqa: E402
from psx_mode2_iso import extract_file  # noqa: E402

CD1 = (CSR / "cache/csr/FINALFANTASY7_D1.bin").read_bytes()
CD2 = (CSR / "cache/csr/FINALFANTASY7_D2.bin").read_bytes()
man = json.loads((ROOT / "builder/manifest.json").read_text())


def lp(aid: str) -> Path:
    e = next(x for x in man["addons"] if x["id"] == aid)
    return ROOT / "builder" / e["discs"]["1"].replace("./", "")


img = bytearray(CD1)
for a in [
    "single-disc-csr-manip-movies-v0.1.4",
    "single-disc-on-csr-v0.1.33",
    "single-disc-on-csr-v0.1.26",
    "single-disc-on-csr-v0.1.35",
]:
    apply_layer(img, json.loads(lp(a).read_text()))
SD = bytes(img)

OUT = ROOT / "workspace" / "field-script-compare-2026-08-13"
OUT.mkdir(parents=True, exist_ok=True)

# List FIELD/*.DAT from ISO directory (no MAPLIST on this image layout)
from psx_mode2_iso import _list_dir, _user, _u32_le  # type: ignore

pvd = _user(CD1, 16)
root = pvd[156 : 156 + 34]
entries = _list_dir(CD1, _u32_le(root, 2), _u32_le(root, 10))
field_ent = next(e for e in entries if e[0] == "FIELD")
field_entries = _list_dir(CD1, field_ent[1], field_ent[2])
FIELD_NAMES = sorted(
    {e[0][:-4] for e in field_entries if e[0].endswith(".DAT") and not e[3]}
)
print("FIELD/*.DAT count", len(FIELD_NAMES), "sample", FIELD_NAMES[:8])


def ops_digest(dat: bytes) -> dict:
    try:
        fd = load_field_dat(dat)
    except Exception as e:
        return {"_error": str(e)}
    out: dict = {
        "_entities": list(fd.entities),
        "_n_scripts": len(fd.scripts),
        "_dec_size": fd.dec_size,
        "_sha": hashlib.sha256(dat).hexdigest()[:16],
        "scripts": {},
    }
    for sc in fd.scripts:
        key = f"{sc.entity}/{sc.slot}"
        ops: list[str] = []
        pos = 0
        while pos < len(sc.raw):
            op = sc.raw[pos]
            sz = max(op_size(sc.raw, pos), 1)
            chunk = sc.raw[pos : pos + sz]
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else f"OP{op:02X}"
            extra = ""
            if name == "IFUB" and len(chunk) >= 6:
                extra = (
                    f"A={chunk[2]:02x}V={chunk[3]:02x}C={chunk[4]}"
                    f"E={chunk[5]:02x}->{(pos + 5) + chunk[5]:04x}"
                )
            elif name in ("IFUW", "IFSW") and len(chunk) >= 8:
                V = int.from_bytes(chunk[4:6], "little")
                extra = (
                    f"V={V:#x}C={chunk[6]}E={chunk[7]:02x}"
                    f"->{(pos + 7) + chunk[7]:04x}"
                )
            elif name == "JMPF" and len(chunk) >= 2:
                extra = f"->{pos + 2 + chunk[1]:04x}"
            elif name == "JMPB" and len(chunk) >= 2:
                extra = f"->{pos - chunk[1]:04x}"
            elif name.startswith("MAPJUMP") and len(chunk) >= 3:
                extra = f"#{int.from_bytes(chunk[1:3], 'little')}"
            elif name == "MUSIC" and len(chunk) >= 2:
                extra = f"id={chunk[1]}"
            elif name == "DSKCG" and len(chunk) >= 2:
                extra = f"disc={chunk[1]}"
            elif name in ("BITON", "BITOFF") and len(chunk) >= 4:
                extra = f"{chunk[1]:02x}/{chunk[2]:02x}#{chunk[3]}"
            elif name == "SETWORD" and len(chunk) >= 5:
                V = int.from_bytes(chunk[3:5], "little")
                extra = f"{chunk[1]:02x}/{chunk[2]:02x}={V:#x}"
            elif name == "SETBYTE" and len(chunk) >= 4:
                extra = f"{chunk[1]:02x}/{chunk[2]:02x}={chunk[3]:#x}"
            elif name in ("ASK", "MESSAGE"):
                extra = chunk.hex()[:16]
            elif name == "PMVIE" and len(chunk) >= 2:
                extra = f"id={chunk[1]}"
            ops.append(f"{pos:04x}:{name}{(' ' + extra) if extra else ''}")
            pos += sz
        out["scripts"][key] = {
            "len": len(sc.raw),
            "sha": hashlib.sha256(sc.raw).hexdigest()[:12],
            "ops": ops,
        }
    return out


def extract_all(image: bytes, label: str) -> dict:
    results = {}
    missing = 0
    for name in FIELD_NAMES:
        try:
            dat = extract_file(image, f"FIELD/{name}.DAT")
        except Exception:
            missing += 1
            continue
        results[name] = ops_digest(dat)
    print(f"{label}: extracted {len(results)} missing {missing}")
    return results


print("Extracting...")
d1 = extract_all(CD1, "D1")
d2 = extract_all(CD2, "D2")
sd = extract_all(SD, "SD")

for lab, data in [("csr-d1", d1), ("csr-d2", d2), ("sd", sd)]:
    p = OUT / f"{lab}-scripts.json"
    p.write_text(json.dumps(data))
    print("wrote", p.name, p.stat().st_size)


def file_equal(a, b) -> bool:
    if a is None or b is None:
        return False
    return a.get("_sha") == b.get("_sha")


all_names = sorted(set(d1) | set(d2) | set(sd))
sd_eq_d1, sd_eq_d2, sd_neither = [], [], []
for name in all_names:
    a, b, c = d1.get(name), d2.get(name), sd.get(name)
    if c is None:
        continue
    eq1, eq2 = file_equal(c, a), file_equal(c, b)
    if eq1 and not eq2:
        sd_eq_d1.append(name)
    elif eq2 and not eq1:
        sd_eq_d2.append(name)
    elif eq1 and eq2:
        sd_eq_d1.append(name)
    else:
        sd_neither.append(name)

d1_ne_d2 = [
    n for n in all_names if n in d1 and n in d2 and not file_equal(d1[n], d2[n])
]
print("SD==D1", len(sd_eq_d1), "SD==D2 only", len(sd_eq_d2), "neither", len(sd_neither))
print("neither:", sd_neither)
print("D1!=D2", len(d1_ne_d2))


def op_interesting(ops: list[str]) -> list[str]:
    keys = (
        "MAPJUMP", "DSKCG", "MUSIC", "ASK", "BITON", "BITOFF", "SETWORD",
        "SETBYTE", "IFUB", "IFUW", "IFSW", "JMPF", "PMVIE", "MOVIE", "RET",
        "MESSAGE", "REQ",
    )
    return [o for o in ops if any(k in o for k in keys)]


def diff_scripts(left, right, labl: str, labr: str) -> list[str]:
    if left is None or right is None:
        return [f"- missing on {labl if left is None else labr}"]
    if left.get("_error") or right.get("_error"):
        return [f"- error {left.get('_error')} / {right.get('_error')}"]
    out: list[str] = []
    ls, rs = left["scripts"], right["scripts"]
    for k in sorted(set(ls) | set(rs)):
        a, b = ls.get(k), rs.get(k)
        if a is None:
            out.append(f"- `{k}` only in {labr} len={b['len']}")
            continue
        if b is None:
            out.append(f"- `{k}` only in {labl} len={a['len']}")
            continue
        if a["sha"] == b["sha"]:
            continue
        ao, bo = a["ops"], b["ops"]
        out.append(f"- **`{k}`** len {a['len']}->{b['len']} ({a['sha']}->{b['sha']})")
        if max(len(ao), len(bo)) <= 100:
            out.append(f"  - {labl}:")
            out.extend(f"    - `{x}`" for x in ao)
            out.append(f"  - {labr}:")
            out.extend(f"    - `{x}`" for x in bo)
        else:
            ai, bi = op_interesting(ao), op_interesting(bo)
            out.append(f"  - {labl} interesting ({len(ai)}):")
            out.extend(f"    - `{x}`" for x in ai[:80])
            if len(ai) > 80:
                out.append(f"    - ... +{len(ai) - 80}")
            out.append(f"  - {labr} interesting ({len(bi)}):")
            out.extend(f"    - `{x}`" for x in bi[:80])
            if len(bi) > 80:
                out.append(f"    - ... +{len(bi) - 80}")

            def hist(ops):
                h: dict[str, int] = defaultdict(int)
                for o in ops:
                    h[o.split(":")[1].split(" ")[0]] += 1
                return h

            ha, hb = hist(ao), hist(bo)
            deltas = [
                f"{op}:{ha[op]}->{hb[op]}"
                for op in sorted(set(ha) | set(hb))
                if ha[op] != hb[op]
            ]
            if deltas:
                out.append(f"  - opcode counts: {', '.join(deltas)}")
    return out


prefer_path = ROOT / "mods/single-disc/patches/csr-field-disc-prefer.txt"
prefer: dict[str, str] = {}
if prefer_path.is_file():
    for line in prefer_path.read_text().splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            key = parts[0].upper().replace(".DAT", "")
            prefer[key] = parts[1].lower()

rows = []
for name in sorted(d1_ne_d2):
    if name not in sd:
        continue
    eq1, eq2 = file_equal(sd[name], d1[name]), file_equal(sd[name], d2[name])
    if eq1:
        side = "d1"
    elif eq2:
        side = "d2"
    else:
        side = "NEITHER"
    pref = prefer.get(name)
    mark = ""
    if pref in ("d1", "d2") and side not in (pref, "NEITHER") and side != pref:
        mark = f" PREFER_MISMATCH want {pref}"
    if side == "NEITHER":
        mark = " PATCHED"
    rows.append((name, side, pref or "", mark))

lines: list[str] = []
lines += [
    "# Field script compare: CSR D1 / CSR D2 / Single-disc stack",
    "",
    "Stack: movies 0.1.4 + single-disc-on-csr-v0.1.33 + path 0.1.26 + v0.1.35",
    "",
    f"- Maplist fields: {len(FIELD_NAMES)}",
    f"- Extracted D1/D2/SD: {len(d1)}/{len(d2)}/{len(sd)}",
    f"- SD byte-identical to D1 (incl D1==D2): {len(sd_eq_d1)}",
    f"- SD byte-identical to D2 only: {len(sd_eq_d2)}",
    f"- SD differs from both: **{len(sd_neither)}**",
    f"- CSR D1!=D2 collisions: {len(d1_ne_d2)}",
    "",
    "## SD fields that match neither pure CSR D1 nor D2",
    "",
]
for name in sorted(sd_neither):
    lines.append(f"### {name}")
    lines.append(f"- D1 sha: {d1.get(name, {}).get('_sha')} dec={d1.get(name, {}).get('_dec_size')}")
    lines.append(f"- D2 sha: {d2.get(name, {}).get('_sha')} dec={d2.get(name, {}).get('_dec_size')}")
    lines.append(f"- SD sha: {sd.get(name, {}).get('_sha')} dec={sd.get(name, {}).get('_dec_size')}")
    lines.append("")
    lines.append("#### SD vs CSR D1")
    lines.extend(diff_scripts(d1.get(name), sd.get(name), "D1", "SD"))
    lines.append("")
    lines.append("#### SD vs CSR D2")
    lines.extend(diff_scripts(d2.get(name), sd.get(name), "D2", "SD"))
    lines.append("")

lines += [
    "## CSR D1!=D2 collisions: which side SD matched",
    "",
    "| Field | SD matches | Prefer list | Note |",
    "|-------|------------|-------------|------|",
]
for name, side, pref, mark in rows:
    lines.append(f"| {name} | {side} | {pref} |{mark}|")

lines += ["", "## High-signal ops on PATCHED fields", ""]


def collect_ops(digest, needle: str) -> list[str]:
    hits = []
    if not digest:
        return hits
    for sk, sc in digest.get("scripts", {}).items():
        for o in sc["ops"]:
            if needle in o:
                hits.append(f"{sk} {o}")
    return hits


for name in sorted(sd_neither):
    lines.append(f"### {name}")
    for lab, dig in [("D1", d1.get(name)), ("D2", d2.get(name)), ("SD", sd.get(name))]:
        for pref in ("DSKCG", "MAPJUMP", "MUSIC", "ASK", "BITON", "BITOFF", "SETWORD"):
            hits = collect_ops(dig, pref)
            if not hits:
                continue
            lines.append(f"- {lab} {pref} ({len(hits)}):")
            for h in hits[:50]:
                lines.append(f"  - `{h}`")
            if len(hits) > 50:
                lines.append(f"  - ... +{len(hits) - 50}")
    lines.append("")

rep_path = OUT / "COMPARE.md"
rep_path.write_text("\n".join(lines))
print("wrote", rep_path, "bytes", rep_path.stat().st_size)

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "sd_neither": sd_neither,
            "sd_eq_d2_only": sd_eq_d2,
            "collision_sides": rows,
        },
        indent=2,
    )
)
print("done", OUT)
