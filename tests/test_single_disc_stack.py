"""Integration: CSR + movies + single-disc stack must not regress known fixes."""
from __future__ import annotations

import sys

import pytest

from helpers import field_ops, movie_id_rows_for_lba, parse_prefer_list, same_or_prefix

SECTOR = 2352
WATERFALL_CANONON_LBA = 250450

# D1 slot -> pristine D2 movie (path / hojo critical)
PATH_MOVIES = [
    ("OPENINGE.MOV", "PARASHOT.MOV", "PARASHOT"),
    ("MTCRL.STR", "METEOFIX.MOV", "METEOFIX"),
    ("MTNVL.STR", "METEOSKY.MOV", "METEOSKY"),
    ("MTNVL2.STR", "NRCRL.MOV", "NRCRL"),
    ("NIVLSFS.MOV", "NRCRLB.MOV", "NRCRLB"),
    ("JAIROFAL.MOV", "CANONON.MOV", "JAIROFAL"),
    ("CAR_1209.STR", "CANONHT2.MOV", "CANONHT2"),
]

pytestmark = [pytest.mark.integration, pytest.mark.slow]


@pytest.fixture(scope="module")
def stack_ids(latest_movies, latest_sd_on_csr):
    return [latest_movies, latest_sd_on_csr]


@pytest.fixture(scope="module")
def stacked(build_stack, stack_ids, require_discs, scripts_dir):
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return build_stack(stack_ids)


@pytest.fixture(scope="module")
def iso_api(scripts_dir):
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from psx_mode2_iso import extract_file, find_file  # noqa: WPS433

    return extract_file, find_file


def test_image_sector_aligned(stacked):
    assert len(stacked) % SECTOR == 0
    assert len(stacked) > 700_000_000


def test_prefer_list_fields(stacked, csr_d1_bytes, csr_d2_bytes, iso_api, root):
    extract_file, _ = iso_api
    prefer = parse_prefer_list(
        root / "mods/single-disc/patches/csr-field-disc-prefer.txt"
    )
    # Always enforce the hard rows (not review)
    hard = {k: v for k, v in prefer.items() if v in ("d1", "d2")}
    assert "LOSIN2.DAT" in hard and hard["LOSIN2.DAT"] == "d1"
    assert "LOST2.DAT" in hard and hard["LOST2.DAT"] == "d2"
    assert "CANON_2.DAT" in hard and hard["CANON_2.DAT"] == "d2"
    assert "BLACKBGB.DAT" in hard

    for stem, side in hard.items():
        path = f"FIELD/{stem}"
        got = extract_file(stacked, path)
        if stem == "BLACKBGB.DAT":
            # Ask-stripped single-disc file — must differ from stock CSR D1
            assert got != extract_file(csr_d1_bytes, path)
            assert len(got) > 1000
            continue
        src = csr_d1_bytes if side == "d1" else csr_d2_bytes
        exp = extract_file(src, path)
        assert same_or_prefix(got, exp), f"{stem} prefer {side} mismatch"


def test_fship_12_parashot_script(stacked, csr_d2_bytes, iso_api):
    extract_file, _ = iso_api
    got = extract_file(stacked, "FIELD/FSHIP_12.DAT")
    assert got == extract_file(csr_d2_bytes, "FIELD/FSHIP_12.DAT")
    ops = field_ops(got)
    assert ("P", 59) in ops  # PARASHOT
    assert ("P", 50) in ops and ("P", 51) in ops
    assert ("J", 731) in ops  # MD8_5


def test_md8_5_nrcrlb(stacked, csr_d1_bytes, csr_d2_bytes, iso_api):
    extract_file, _ = iso_api
    for ext in (".DAT", ".MIM", ".BSX"):
        p = f"FIELD/MD8_5{ext}"
        assert extract_file(stacked, p) == extract_file(csr_d1_bytes, p)
        assert extract_file(stacked, p) == extract_file(csr_d2_bytes, p)
    ops = field_ops(extract_file(stacked, "FIELD/MD8_5.DAT"))
    assert ("P", 53) in ops


def test_md8_52_nrcrl(stacked, csr_d2_bytes, iso_api):
    extract_file, _ = iso_api
    got = extract_file(stacked, "FIELD/MD8_52.DAT")
    exp = extract_file(csr_d2_bytes, "FIELD/MD8_52.DAT")
    assert same_or_prefix(got, exp)
    ops = field_ops(got)
    assert ("P", 52) in ops
    assert ("J", 72) in ops  # FSHIP_25


def test_path_fmv_payloads_unique_lbas(stacked, pristine_d2_bytes, iso_api):
    extract_file, find_file = iso_api
    lbs = {}
    for d1, d2, lab in PATH_MOVIES:
        got = extract_file(stacked, f"MOVIE/{d1}")
        exp = extract_file(pristine_d2_bytes, f"MOVIE/{d2}")
        assert same_or_prefix(got, exp), lab
        meta = find_file(stacked, f"MOVIE/{d1}")
        lbs[lab] = meta.lba
        # MOVIE_ID must reference this LBA
        mid = extract_file(stacked, "MINT/MOVIE_ID.BIN")
        rows = movie_id_rows_for_lba(mid, meta.lba)
        assert rows, f"no MOVIE_ID row for {lab} LBA {meta.lba}"

    path_labs = ["PARASHOT", "METEOFIX", "METEOSKY", "NRCRL", "NRCRLB", "JAIROFAL"]
    path_lbs = [lbs[k] for k in path_labs]
    assert len(path_lbs) == len(set(path_lbs)), path_lbs


def test_waterfall_absolute_lba_canonon(stacked, pristine_d2_bytes, iso_api):
    _, find_file = iso_api
    can = find_file(pristine_d2_bytes, "MOVIE/CANONON.MOV")
    sec_s = stacked[WATERFALL_CANONON_LBA * SECTOR : (WATERFALL_CANONON_LBA + 1) * SECTOR]
    sec_d = pristine_d2_bytes[can.lba * SECTOR : (can.lba + 1) * SECTOR]
    assert sec_s == sec_d


def test_loslake_and_white2_present(stacked, iso_api):
    extract_file, _ = iso_api
    for name in (
        "LOSLAKE1",
        "LOSLAKE2",
        "LOSLAKE3",
        "WHITE2",
        "DEL1",
        "DEL2",
        "DEL3",
    ):
        assert len(extract_file(stacked, f"FIELD/{name}.DAT")) > 100


def test_endings_do_not_clobber_core(build_stack, stack_ids, endings_parts, iso_api, stacked):
    if not endings_parts:
        pytest.skip("no endings packs")
    extract_file, _ = iso_api
    with_end = build_stack(stack_ids + endings_parts)
    assert len(with_end) % SECTOR == 0
    assert extract_file(with_end, "FIELD/LOSIN2.DAT") == extract_file(
        stacked, "FIELD/LOSIN2.DAT"
    )
    assert extract_file(with_end, "FIELD/CANON_2.DAT") == extract_file(
        stacked, "FIELD/CANON_2.DAT"
    )
    assert extract_file(with_end, "MOVIE/OPENINGE.MOV") == extract_file(
        stacked, "MOVIE/OPENINGE.MOV"
    )
