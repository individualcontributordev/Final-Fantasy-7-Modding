"""Regression tests for the structural RE-extraction toolchain: opcode/struct
decoders sourced from makoureactor / ff7-decomp / ffvii / ff7-landscaper /
ff7-chocobo+coaster. No disc images required -- pure library/CLI logic
against the extracted external/ headers, so these always run (no skips).

Guards against: extraction regex drift, external/ submodule updates changing
field counts/order, and the [CONFIRMED]/[UNCONFIRMED] contract silently
breaking on any of the five decoder tools.
"""
from __future__ import annotations

import sys

import pytest


@pytest.fixture(autouse=True)
def _scripts_on_path(scripts_dir):
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))


def test_opcode_struct_decoder_music():
    from opcode_struct_decoder import decode, list_mismatches

    lines = decode("MUSIC", bytes.fromhex("2801"))
    assert lines, "MUSIC should decode to at least one field line"
    assert lines[0].startswith("[CONFIRMED]")
    assert "musicID" in lines[0]
    # Ground-truth cross-check must stay clean across makoureactor updates.
    assert list_mismatches() == []


def test_opcode_struct_decoder_unknown_opcode():
    from opcode_struct_decoder import decode

    lines = decode("NOT_A_REAL_OPCODE", b"\x00")
    assert len(lines) == 1
    assert lines[0].startswith("[UNCONFIRMED:")


def test_field_pattern_finder_decode_fields_wiring():
    """find_opcode(..., decode_fields=True) must indent decoded field lines
    under the [CONFIRMED] hit, using the mnemonic stripped of any
    entity-qualifying suffix (e.g. 'MUSIC.something' -> 'MUSIC')."""
    from field_pattern_finder import find_opcode

    class _FakeSlot:
        def __init__(self, raw):
            self.raw = raw
            self.start = 0
            self.entity = "test"
            self.slot = 0

    class _FakeFD:
        def __init__(self, raw):
            self.scripts = [_FakeSlot(raw)]

    fd = _FakeFD(bytes.fromhex("f001"))  # opcode 0xF0 = MUSIC, 1 param byte
    out = find_opcode(fd, "MUSIC", decode_fields=True)
    assert len(out) == 2
    assert out[0].startswith("[CONFIRMED]")
    assert out[1].strip().startswith("[CONFIRMED]")
    assert out[1].startswith("    "), "decoded field line must be indented under the hit"


def test_worldmap_opcode_lookup_basic():
    from worldmap_opcode_layout import get, find_by_mnemonic, load_opcodes

    op = get(0x318)
    assert op is not None
    assert op.mnemonic == "ENTER_FIELD"

    by_name = find_by_mnemonic("ENTER_FIELD")
    assert by_name is not None
    assert by_name.opcode_id == 0x318

    ops = load_opcodes()
    assert len(ops) > 50, "extraction should find the bulk of Landscaper's opcode table"


def test_worldmap_opcode_lookup_unknown_id():
    from worldmap_opcode_layout import get

    assert get(0xFFF) is None


def test_pc_struct_decoder_vector():
    from pc_struct_decoder import decode, list_structs

    raw = bytes.fromhex("01000000020000000300000004000000")
    lines = decode("VECTOR", raw, base_addr=None)
    assert lines
    assert all(l.startswith("[CONFIRMED]") for l in lines)
    assert len(list_structs()) > 20


def test_pc_struct_decoder_unknown_struct():
    from pc_struct_decoder import decode

    lines = decode("NotAStruct", b"\x00", base_addr=None)
    assert len(lines) == 1
    assert lines[0].startswith("[UNCONFIRMED:")


def test_decomp_struct_decoder_list_structs():
    from decomp_struct_decoder import list_structs

    structs = list_structs()
    assert structs
    assert any("WorldTriangle" in s for s in structs)


def test_decomp_symbol_lookup_stats_and_lookup():
    from decomp_symbol_map import load_symbols, get

    syms = load_symbols()
    assert len(syms) > 500
    confirmed = [s for s in syms.values() if s.confirmed]
    assert confirmed, "extraction must yield at least some address-confirmed symbols"

    sym = get("Savemap")
    if sym is not None:
        assert sym.confirmed
