"""Structured diff of two PSX FIELD/*.DAT (after LZS + section parse)."""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from typing import Any

from field_dat import SECTION_NAMES, FieldDat, load_field_dat


@dataclass
class FieldDiff:
    a_label: str
    b_label: str
    raw_sizes: tuple[int, int]
    dec_sizes: tuple[int, int]
    section_same: dict[str, bool]
    section_sizes: dict[str, tuple[int, int]]
    scripts_identical: bool
    script_slots_a: int
    script_slots_b: int
    script_diffs: list[dict[str, Any]] = field(default_factory=list)
    entities_a: list[str] = field(default_factory=list)
    entities_b: list[str] = field(default_factory=list)
    texts_content_same: bool = True
    text_count: tuple[int, int] = (0, 0)
    text_pad: tuple[int, int] = (0, 0)
    text_content_diff_ids: list[int] = field(default_factory=list)
    akao_same: bool = True
    classification: str = ""  # identical | pad-only | scripts | mixed | sections

    def is_innocuous(self) -> bool:
        """True if only compression / text padding / identical."""
        return self.classification in ("identical", "pad-only")


def compare_fields(
    a: FieldDat, b: FieldDat, *, a_label: str = "A", b_label: str = "B"
) -> FieldDiff:
    sec_same = {
        SECTION_NAMES[i]: a.sections[i] == b.sections[i] for i in range(7)
    }
    sec_sizes = {
        SECTION_NAMES[i]: (len(a.sections[i]), len(b.sections[i]))
        for i in range(7)
    }

    map_a = {(s.entity, s.slot): s for s in a.scripts}
    map_b = {(s.entity, s.slot): s for s in b.scripts}
    keys = sorted(set(map_a) | set(map_b), key=lambda x: (x[0], x[1]))
    script_diffs: list[dict[str, Any]] = []
    for k in keys:
        sa, sb = map_a.get(k), map_b.get(k)
        ra = sa.raw if sa else None
        rb = sb.raw if sb else None
        if ra == rb:
            continue
        ops_a = sa.ops() if sa else []
        ops_b = sb.ops() if sb else []
        script_diffs.append(
            {
                "entity": k[0],
                "slot": k[1],
                "bytes": (len(ra) if ra else 0, len(rb) if rb else 0),
                "ops_a": ops_a,
                "ops_b": ops_b,
                "unified": list(
                    difflib.unified_diff(
                        ops_a,
                        ops_b,
                        fromfile=a_label,
                        tofile=b_label,
                        lineterm="",
                    )
                ),
            }
        )

    n = max(len(a.text_entries), len(b.text_entries))
    text_diff_ids = [
        i
        for i in range(n)
        if (a.text_entries[i] if i < len(a.text_entries) else None)
        != (b.text_entries[i] if i < len(b.text_entries) else None)
    ]
    texts_content_same = not text_diff_ids
    akao_same = a.akao == b.akao

    non_script_sec = any(
        not sec_same[n] for n in SECTION_NAMES if n != "scripts"
    )
    # scripts section may differ only in text pad
    scripts_id = not script_diffs

    if all(sec_same.values()) and a.raw_size == b.raw_size:
        cls = "identical"
    elif scripts_id and texts_content_same and akao_same and not non_script_sec:
        # only text packing / LZS recompress inside scripts section
        if a.text_pad_total != b.text_pad_total or a.raw_size != b.raw_size:
            cls = "pad-only"
        elif a.sections[0] != b.sections[0]:
            cls = "pad-only"  # header ptr / akao offset shift from pad
        else:
            cls = "identical"
    elif script_diffs and not non_script_sec and texts_content_same:
        cls = "scripts"
    elif non_script_sec and scripts_id and texts_content_same:
        cls = "sections"
    else:
        cls = "mixed"

    return FieldDiff(
        a_label=a_label,
        b_label=b_label,
        raw_sizes=(a.raw_size, b.raw_size),
        dec_sizes=(a.dec_size, b.dec_size),
        section_same=sec_same,
        section_sizes=sec_sizes,
        scripts_identical=scripts_id,
        script_slots_a=len(a.scripts),
        script_slots_b=len(b.scripts),
        script_diffs=script_diffs,
        entities_a=list(a.entities),
        entities_b=list(b.entities),
        texts_content_same=texts_content_same,
        text_count=(len(a.text_entries), len(b.text_entries)),
        text_pad=(a.text_pad_total, b.text_pad_total),
        text_content_diff_ids=text_diff_ids,
        akao_same=akao_same,
        classification=cls,
    )


def format_diff_report(d: FieldDiff, *, max_script_diffs: int = 20) -> str:
    lines = [
        f"# Field compare: {d.a_label} vs {d.b_label}",
        "",
        f"**Classification:** `{d.classification}`"
        + (" (innocuous)" if d.is_innocuous() else " (meaningful)"),
        "",
        f"| | {d.a_label} | {d.b_label} | delta |",
        "|--|--:|--:|--:|",
        f"| compressed | {d.raw_sizes[0]} | {d.raw_sizes[1]} | {d.raw_sizes[1]-d.raw_sizes[0]} |",
        f"| decompressed | {d.dec_sizes[0]} | {d.dec_sizes[1]} | {d.dec_sizes[1]-d.dec_sizes[0]} |",
        f"| script slots | {d.script_slots_a} | {d.script_slots_b} | |",
        f"| text entries | {d.text_count[0]} | {d.text_count[1]} | |",
        f"| text padding | {d.text_pad[0]} | {d.text_pad[1]} | {d.text_pad[1]-d.text_pad[0]} |",
        "",
        "## Sections",
        "",
    ]
    for name in SECTION_NAMES:
        sa, sb = d.section_sizes[name]
        same = "same" if d.section_same[name] else "**DIFF**"
        lines.append(f"- `{name}`: {sa} → {sb} ({same})")
    lines += [
        "",
        f"Scripts identical: **{d.scripts_identical}** "
        f"({len(d.script_diffs)} differing slots)",
        f"Text content identical: **{d.texts_content_same}** "
        f"(diff ids: {d.text_content_diff_ids[:40]}"
        f"{'…' if len(d.text_content_diff_ids) > 40 else ''})",
        f"AKAO identical: **{d.akao_same}**",
        "",
    ]
    if d.entities_a != d.entities_b:
        lines += [
            f"Entities A: {d.entities_a}",
            f"Entities B: {d.entities_b}",
            "",
        ]
    for i, sd in enumerate(d.script_diffs[:max_script_diffs]):
        lines += [
            f"## Script `{sd['entity']}` slot {sd['slot']}",
            "",
            f"bytes {sd['bytes'][0]} → {sd['bytes'][1]}",
            "",
            "```diff",
        ]
        lines += sd["unified"][:200]
        if len(sd["unified"]) > 200:
            lines.append(f"... ({len(sd['unified'])-200} more diff lines)")
        lines += ["```", ""]
    if len(d.script_diffs) > max_script_diffs:
        lines.append(
            f"_… {len(d.script_diffs) - max_script_diffs} more script slots omitted_"
        )
    return "\n".join(lines) + "\n"


def compare_bytes(
    a: bytes, b: bytes, *, a_label: str = "A", b_label: str = "B"
) -> FieldDiff:
    return compare_fields(
        load_field_dat(a, a_label), load_field_dat(b, b_label),
        a_label=a_label, b_label=b_label,
    )
