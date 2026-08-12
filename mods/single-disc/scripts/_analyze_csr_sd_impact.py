#!/usr/bin/env python3
"""Offline: CSR D1 + single-disc 0.1.20 + movies 0.1.4 vs pristine D1/D2/D3."""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts"))

from apply_layer import apply_layer  # noqa: E402
from psx_mode2_iso import (  # noqa: E402
    SECTOR,
    USER,
    extract_file,
    find_file,
    _list_dir,
    _u32_le,
    _user,
)

# Makou field ids — load field_maplist without shadowing Modding psx_mode2_iso
import importlib.util

def _load_maplist():
    for base in (Path.home() / "Final-Fantasy-7-CSR/scripts", _ROOT.parent / "Final-Fantasy-7-CSR/scripts"):
        fp = base / "field_maplist.py"
        if fp.is_file():
            spec = importlib.util.spec_from_file_location("field_maplist", fp)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader
            spec.loader.exec_module(mod)
            return mod.MAPLIST
    raise FileNotFoundError("field_maplist.py")

MAPLIST = _load_maplist()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:12]


def extract_by_lba_size(img: bytes, lba: int, size: int) -> bytes:
    out = bytearray()
    remaining = size
    sec = lba
    while remaining > 0:
        take = min(USER, remaining)
        off = sec * SECTOR + 24
        out.extend(img[off : off + take])
        remaining -= take
        sec += 1
    return bytes(out)


def field_map(img: bytes):
    pvd = _user(img, 16)
    root = pvd[156:190]
    for n, lba, sz, d in _list_dir(img, _u32_le(root, 2), _u32_le(root, 10)):
        if n != "FIELD" or not d:
            continue
        ents = []
        maplist_raw = None
        for nn, lb, ss, dd in _list_dir(img, lba, sz):
            if nn in (".", ".."):
                continue
            if dd:
                continue
            up = nn.upper()
            if up in ("MAPLIST", "MAPLIST.TXT", "MAPLIST.BIN"):
                maplist_raw = extract_file(img, f"FIELD/{nn}")
            if up.endswith(".DAT"):
                ents.append((up, lb, ss))
        by_name = {fn: (lb, ss) for fn, lb, ss in ents}
        # Field id = Makou MAPLIST index (not ISO alpha order)
        id_for: dict[str, int] = {}
        for i, stem in enumerate(MAPLIST):
            u = stem.upper()
            id_for[u] = i
            id_for[u + ".DAT"] = i
        return by_name, id_for, list(MAPLIST)
    raise FileNotFoundError("FIELD")


def parse_maplist(raw: bytes) -> list[str]:
    if not raw:
        return []
    names: list[str] = []
    for i in range(0, len(raw), 32):
        chunk = raw[i : i + 32]
        if not chunk or all(b == 0 for b in chunk):
            if i > 0:
                break
            continue
        name = chunk.split(b"\x00", 1)[0].decode("ascii", "replace").upper()
        if name.endswith(".DAT"):
            name = name[:-4]
        names.append(name)
    if sum(1 for n in names if n) > 50:
        return names
    try:
        text = raw.decode("ascii", "replace")
        if "\n" in text or "\r" in text:
            out = []
            for line in text.replace("\r", "\n").split("\n"):
                s = line.strip().upper()
                if not s:
                    continue
                if s.endswith(".DAT"):
                    s = s[:-4]
                out.append(s)
            if len(out) > 50:
                return out
    except Exception:
        pass
    return names


def movie_entries(img: bytes):
    pvd = _user(img, 16)
    root = pvd[156:190]
    for n, lba, sz, d in _list_dir(img, _u32_le(root, 2), _u32_le(root, 10)):
        if n == "MOVIE" and d:
            ents = []
            for nn, lb, ss, dd in _list_dir(img, lba, sz):
                if nn in (".", "..") or dd:
                    continue
                ents.append((nn.upper(), lb, ss))
            return sorted(ents, key=lambda x: x[0])
    return []


def file_hash(img, name_map, fname):
    if fname not in name_map:
        return None
    lb, ss = name_map[fname]
    return sha(extract_by_lba_size(img, lb, ss)), ss, lb


def mid_rows(img):
    try:
        raw = extract_file(img, "MINT/MOVIE_ID.BIN")
    except Exception:
        return []
    out = []
    for i in range(0, len(raw) // 20):
        lba, size, a, b, c = struct.unpack_from("<5I", raw, i * 20)
        out.append((i, lba, size, a, b, c))
    return out


def main() -> int:
    pristine_d1 = (_ROOT / "workspace/pristine/FINALFANTASY7_D1.bin").read_bytes()
    pristine_d2 = (_ROOT / "workspace/pristine/FINALFANTASY7_D2.bin").read_bytes()
    pristine_d3 = (_ROOT / "workspace/pristine/FINALFANTASY7_D3.bin").read_bytes()
    csr_path = Path.home() / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D1.bin"
    if not csr_path.is_file():
        csr_path = _ROOT.parent / "Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D1.bin"
    img = bytearray(csr_path.read_bytes())
    print("base", len(img))

    sd = json.loads(
        (_ROOT / "builder/single-disc-on-csr-v0.1.20/layers/disc1.layer.json").read_text()
    )
    apply_layer(img, sd)
    print("after sd", len(img))
    mv = json.loads(
        (
            _ROOT
            / "builder/single-disc-csr-manip-movies-v0.1.4/layers/disc1.layer.json"
        ).read_text()
    )
    apply_layer(img, mv)
    print("after movies", len(img), "mod", len(img) % SECTOR)
    built = bytes(img)

    b_name, b_id, b_order = field_map(built)
    p1_name, p1_id, _ = field_map(pristine_d1)
    p2_name, p2_id, _ = field_map(pristine_d2)
    p3_name, p3_id, _ = field_map(pristine_d3)
    csr_only = csr_path.read_bytes()
    c_name, c_id, _ = field_map(csr_only)
    print("fields", len(b_name), "maplist", len(b_order))

    prefer: dict[str, str] = {}
    for line in (_ROOT / "mods/single-disc/patches/csr-field-disc-prefer.txt").read_text().splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            prefer[parts[0].upper()] = parts[1].lower()

    rows = []
    same_p1 = 0
    for fname in sorted(b_name.keys()):
        hb = file_hash(built, b_name, fname)
        if not hb:
            continue
        h_built, sz_b, _lba_b = hb
        h_p1 = file_hash(pristine_d1, p1_name, fname)
        h_p2 = file_hash(pristine_d2, p2_name, fname)
        h_p3 = file_hash(pristine_d3, p3_name, fname)
        h_csr = file_hash(csr_only, c_name, fname)
        p1s = h_p1[0] if h_p1 else None
        p2s = h_p2[0] if h_p2 else None
        p3s = h_p3[0] if h_p3 else None
        csrs = h_csr[0] if h_csr else None

        if p1s and h_built == p1s:
            same_p1 += 1
            if not (csrs and csrs != p1s):
                continue

        sources = []
        if csrs and h_built == csrs:
            sources.append("CSR-D1")
        if p1s and h_built == p1s:
            sources.append("pristine-D1")
        if p2s and h_built == p2s:
            sources.append("pristine-D2")
        if p3s and h_built == p3s:
            sources.append("pristine-D3")
        match = "+".join(sources) if sources else "modified"

        fid = b_id.get(fname)
        if fid is None:
            fid = b_id.get(fname[:-4] if fname.endswith(".DAT") else fname, -1)

        rows.append(
            {
                "file": fname,
                "id": fid if fid is not None else -1,
                "size": sz_b,
                "match": match,
                "prefer": prefer.get(fname, ""),
                "vs_csr_d1": "same" if csrs and h_built == csrs else ("diff" if csrs else "n/a"),
                "vs_p1": "same" if p1s and h_built == p1s else ("diff" if p1s else "missing-p1"),
                "vs_p2": "same" if p2s and h_built == p2s else ("diff" if p2s else "missing-p2"),
                "vs_p3": "same" if p3s and h_built == p3s else ("diff" if p3s else "missing-p3"),
            }
        )

    # CSR D2/D3 labeling
    for disc_n, rel in ((2, "D2"), (3, "D3")):
        cp = csr_path.parent / f"FINALFANTASY7_{rel}.bin"
        if not cp.is_file():
            continue
        print("match CSR", rel)
        cimg = cp.read_bytes()
        cn, _, _ = field_map(cimg)
        for r in rows:
            h = file_hash(built, b_name, r["file"])
            hx = file_hash(cimg, cn, r["file"])
            if h and hx and h[0] == hx[0]:
                tag = f"CSR-{rel}"
                if tag not in r["match"]:
                    if r["match"] in ("modified", "hybrid/unique"):
                        r["match"] = tag
                    else:
                        r["match"] = r["match"] + "+" + tag

    rows_sd = sorted(
        [r for r in rows if r["vs_csr_d1"] == "diff"],
        key=lambda r: (r["id"] if r["id"] >= 0 else 9999, r["file"]),
    )
    rows_csr = sorted(
        [r for r in rows if r["vs_csr_d1"] == "same" and r["vs_p1"] == "diff"],
        key=lambda r: (r["id"] if r["id"] >= 0 else 9999, r["file"]),
    )
    mc = Counter(r["match"] for r in rows_sd)

    # Movies
    bm = movie_entries(built)
    p1m = {n: (lb, ss) for n, lb, ss in movie_entries(pristine_d1)}
    p2m = {n: (lb, ss) for n, lb, ss in movie_entries(pristine_d2)}
    p3m = {n: (lb, ss) for n, lb, ss in movie_entries(pristine_d3)}
    b_mid = mid_rows(built)
    p1_mid = mid_rows(pristine_d1)
    movie_rows = []
    for mid, (name, lb, ss) in enumerate(bm):
        hb = sha(extract_by_lba_size(built, lb, ss))
        src = "?"
        for label, img, mp in (
            ("pristine-D1", pristine_d1, p1m),
            ("pristine-D2", pristine_d2, p2m),
            ("pristine-D3", pristine_d3, p3m),
        ):
            if name in mp:
                lb2, ss2 = mp[name]
                if ss2 == ss and sha(extract_by_lba_size(img, lb2, ss2)) == hb:
                    src = label
                    break
        if src == "?":
            for label, img, mp in (
                ("pristine-D2", pristine_d2, p2m),
                ("pristine-D3", pristine_d3, p3m),
                ("pristine-D1", pristine_d1, p1m),
            ):
                for n2, (lb2, ss2) in mp.items():
                    if ss2 != ss:
                        continue
                    if sha(extract_by_lba_size(img, lb2, ss2)) == hb:
                        src = f"{label}:{n2}"
                        break
                if src != "?":
                    break
        p1_same = (
            name in p1m
            and p1m[name][1] == ss
            and sha(extract_by_lba_size(pristine_d1, *p1m[name])) == hb
        )
        mid_meta = b_mid[mid] if mid < len(b_mid) else None
        p1_meta = p1_mid[mid] if mid < len(p1_mid) else None
        meta_changed = bool(mid_meta and p1_meta and mid_meta[1:] != p1_meta[1:])
        if p1_same and not meta_changed:
            continue
        movie_rows.append(
            {
                "id": mid,
                "slot": name,
                "size": ss,
                "lba": lb,
                "content": src if not p1_same else "pristine-D1",
                "movie_id_meta_changed": meta_changed,
                "eng_size": mid_meta[2] if mid_meta else None,
                "eng_lba": mid_meta[1] if mid_meta else None,
            }
        )

    alias_lba = 250450
    alias_sec = built[alias_lba * SECTOR : (alias_lba + 1) * SECTOR]
    d2_canon = find_file(pristine_d2, "MOVIE/CANONON.MOV")
    d2_sec = pristine_d2[d2_canon.lba * SECTOR : (d2_canon.lba + 1) * SECTOR]
    alias_ok = alias_sec == d2_sec

    out = _ROOT / "docs/findings/2026-08-12-csr-single-disc-field-movie-impact.md"
    lines: list[str] = []
    lines += [
        "# CSR + Single-disc impact vs pristine D1/D2/D3",
        "",
        "Stack (offline, same as builder):",
        "",
        "1. CSR D1 cache `csr-v0.14.1`",
        "2. `single-disc-on-csr-v0.1.20`",
        "3. `single-disc-csr-manip-movies-v0.1.4`",
        "",
        "FIELD compare = SHA-256 prefix of ISO user payload. "
        "Field **Id** = MAPLIST index. Movie **Id** = sorted MOVIE/ name (PMVIE).",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|------:|",
        f"| FIELD files on built D1 | {len(b_name)} |",
        f"| Same as pristine D1 (not listed) | {same_p1} |",
        f"| Diff vs pristine D1 (interesting) | {len(rows)} |",
        f"| **Single-disc touched** (diff vs CSR-D1) | **{len(rows_sd)}** |",
        f"| CSR-base field deltas left as-is | {len(rows_csr)} |",
        f"| MOVIE slots content and/or MOVIE_ID meta != P1 | {len(movie_rows)} |",
        f"| LBA 250450 == pristine D2 CANONON sec0 | {alias_ok} |",
        "",
        "### Single-disc-touched — content match buckets",
        "",
        "| Built bytes match | Count |",
        "|-------------------|------:|",
    ]
    for k, v in mc.most_common():
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Prefer-list overrides",
        "",
        "| Field | Id | Prefer | Built matches | vs CSR-D1 |",
        "|-------|---:|--------|---------------|-----------|",
    ]
    for fname, pref in sorted(prefer.items()):
        r = next((x for x in rows if x["file"] == fname), None)
        fid = b_id.get(fname, b_id.get(fname[:-4], "?"))
        if r:
            lines.append(
                f"| {fname} | {r['id']} | {pref} | {r['match']} | {r['vs_csr_d1']} |"
            )
        else:
            lines.append(
                f"| {fname} | {fid} | {pref} | (same as pristine D1 / not in diff) | n/a |"
            )

    lines += [
        "",
        "## A. Fields single-disc changed vs CSR D1",
        "",
        "Primary single-disc FIELD surface (movies pack does not rewrite FIELD).",
        "",
        "| Id | Field | Bytes match | vs P1 | vs P2 | vs P3 | Prefer |",
        "|---:|-------|-------------|------|------|------|--------|",
    ]
    for r in rows_sd:
        fid = r["id"] if r["id"] >= 0 else "—"
        lines.append(
            f"| {fid} | {r['file']} | {r['match']} | {r['vs_p1']} | "
            f"{r['vs_p2']} | {r['vs_p3']} | {r['prefer'] or '—'} |"
        )

    notes = {
        "LOSIN2.DAT": "End D1 / disc-2 break arm — keep CSR D1 so GM 0xa455 for LOST2/COS.",
        "LOST2.DAT": "Disc 1->2 break scene body — CSR D2 on single-disc.",
        "CANON_2.DAT": "Hojo lab — pure CSR D2 (never raw-strip 0e03 in AKAO).",
        "BLACKBGB.DAT": "Post-Hojo / disc-3 gate — SD Ask/DSKCG stripped keep.",
        "COS_BTM2.DAT": "Cosmo / break IFUW disc-id path.",
        "WHITE2.DAT": "Cosmo Canyon graphical hybrid history.",
        "DEL1.DAT": "Forced keep CSR D1 core.",
    }
    lines += [
        "",
        "## B. Notable transitions",
        "",
        "| Id | Field | Why |",
        "|---:|-------|-----|",
    ]
    for fn, why in notes.items():
        r = next((x for x in rows if x["file"] == fn), None)
        fid = r["id"] if r and r["id"] >= 0 else b_id.get(fn, "—")
        match = r["match"] if r else "same-as-P1-or-absent"
        lines.append(f"| {fid} | {fn} | {why} Built: `{match}`. |")

    lines += [
        "",
        "## C. CSR-base field deltas (single-disc did not overwrite)",
        "",
        f"{len(rows_csr)} maps differ from pristine D1 because CSR changed them.",
        "",
    ]
    if len(rows_csr) <= 250:
        lines += ["| Id | Field | Matches |", "|---:|-------|---------|"]
        for r in rows_csr:
            fid = r["id"] if r["id"] >= 0 else "—"
            lines.append(f"| {fid} | {r['file']} | {r['match']} |")
    else:
        lines.append("```")
        lines.append(
            ", ".join(f"{r['id']}:{r['file'][:-4]}" for r in rows_csr)
        )
        lines.append("```")

    lines += [
        "",
        "## D. Movies / MOVIE_ID (manip-movies pack)",
        "",
        "| Id | D1 slot | ISO size | Content | Meta!=P1 | eng LBA | eng size |",
        "|---:|---------|---------:|---------|----------|--------:|---------:|",
    ]
    for m in movie_rows:
        lines.append(
            f"| {m['id']} | {m['slot']} | {m['size']} | {m['content']} | "
            f"{m['movie_id_meta_changed']} | {m['eng_lba']} | {m['eng_size']} |"
        )
    lines += [
        "",
        "### Absolute seeks",
        "",
        "| LBA | Purpose | Status |",
        "|----:|---------|--------|",
        f"| 250450 | LOSLAKE1 -> D2 CANONON (waterfall) | sec0 match D2: **{alias_ok}** "
        "(clobbers RCKTFAIL tail; may relocate JAIROFLY) |",
        "",
        "## E. Playtest coverage vs residual risk",
        "",
        "| Area | Your tests | Residual |",
        "|------|------------|----------|",
        "| Hojo CANON_2 + FMV | yes | — |",
        "| LOSLAKE1 waterfall | yes | RCKTFAIL destroyed (tradeoff) |",
        "| Disc1->2 break | yes | — |",
        "| Final descent / battles | yes | — |",
        "| Ending credits | planned | Full D3 credits need endings pack; manip is partial |",
        "| Cosmo WHITE2 / COS_BTM* | history | Revisit if graphics/break odd |",
        "| Rare D2/D3-only maps | no | See section A CSR-D2/D3 rows |",
        "| Stock D1 movies at inject ids | side effect | CAR_1209/GOLD7_2/JAIRO* etc. |",
        "",
        "## Method",
        "",
        "- Offline ic-layer-v1 apply onto CSR D1 cache.",
        "- No builder EDC step here (FMV Form2 bytes compared pre-EDC; alias is raw).",
        "",
    ]
    out.write_text("\n".join(lines) + "\n")
    print("WROTE", out)
    print("SD touched", len(rows_sd))
    for r in rows_sd[:30]:
        print(f"  id={r['id']:4} {r['file']:16} {r['match']}")
    print("movies", len(movie_rows))
    for m in movie_rows:
        print(f"  mid={m['id']:3} {m['slot']:16} {m['content']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
