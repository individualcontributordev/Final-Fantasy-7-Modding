"""Prefer-list contract for CSR field merge (no discs)."""
from __future__ import annotations

from helpers import parse_prefer_list


def test_prefer_list_hard_rows(root):
    path = root / "mods/single-disc/patches/csr-field-disc-prefer.txt"
    prefer = parse_prefer_list(path)
    assert prefer["LOSIN2.DAT"] == "d1"
    assert prefer["LOST2.DAT"] == "d2"
    assert prefer["CANON_2.DAT"] == "d2"
    assert prefer["BLACKBGB.DAT"] == "d1"
    assert prefer["DEL1.DAT"] == "d1"
    # review rows must not be auto-applied as d1/d2 hard prefer
    for stem, side in prefer.items():
        assert side in ("d1", "d2", "review"), (stem, side)


def test_prefer_list_comments_ignored(tmp_path):
    p = tmp_path / "prefer.txt"
    p.write_text(
        "# comment\n"
        "FOO.DAT d1  # note\n"
        "\n"
        "BAR.DAT review\n"
        "not a row\n"
    )
    prefer = parse_prefer_list(p)
    assert prefer == {"FOO.DAT": "d1", "BAR.DAT": "review"}
