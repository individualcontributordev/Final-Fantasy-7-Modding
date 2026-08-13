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
def stack_ids(latest_movies, sd_on_csr_stack):
    # movies first, then single-disc core + path-engine deltas (version order)
    return [latest_movies, *sd_on_csr_stack]


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
        if stem == "LOST2.DAT":
            exp = extract_file(csr_d2_bytes, path)
            assert same_or_prefix(got, exp), "LOST2 must be pure CSR D2"
            continue
        if stem == "COS_BTM2.DAT":
            # opened for break ASK in v0.1.34 — not pure bytes
            assert got != extract_file(csr_d1_bytes, path)
            assert len(got) > 1000
            continue
        if stem == "LOSIN2.DAT":
            # BITON break bit (v0.1.34) — still D1-based
            assert got != extract_file(csr_d2_bytes, path)
            assert len(got) > 1000
            continue
        src = csr_d1_bytes if side == "d1" else csr_d2_bytes
        exp = extract_file(src, path)
        assert same_or_prefix(got, exp), f"{stem} prefer {side} mismatch"


def test_fship_12_engine_path_ids(stacked, iso_api):
    """FSHIP_12 uses remapped D1 engine ids 54-57 (D2 mids 55/59/50/51)."""
    extract_file, _ = iso_api
    ops = field_ops(extract_file(stacked, "FIELD/FSHIP_12.DAT"))
    pm = {o[1] for o in ops if o[0] == "P"}
    assert {54, 55, 56, 57} <= pm
    assert ("J", 731) in ops  # MD8_5 next


def test_md8_5_parashot_engine_id(stacked, pristine_d2_bytes, iso_api):
    """MD8_5 (#731) must play PARASHOT via MOVIE_ID[58], not wrong mid53."""
    import struct

    extract_file, find_file = iso_api
    from psx_mode2_iso import SECTOR

    ops = field_ops(extract_file(stacked, "FIELD/MD8_5.DAT"))
    assert ("P", 58) in ops
    mid = extract_file(stacked, "MINT/MOVIE_ID.BIN")
    assert len(mid) // 20 >= 59
    lba, eng = struct.unpack_from("<2I", mid, 58 * 20)
    sec = stacked[lba * SECTOR : (lba + 1) * SECTOR]
    p = find_file(pristine_d2_bytes, "MOVIE/PARASHOT.MOV")
    exp = pristine_d2_bytes[p.lba * SECTOR : (p.lba + 1) * SECTOR]
    assert sec == exp
    assert eng == 11957984  # D2 Form2 eng size for PARASHOT


def test_md8_52_engine_id(stacked, iso_api):
    extract_file, _ = iso_api
    ops = field_ops(extract_file(stacked, "FIELD/MD8_52.DAT"))
    assert ("P", 59) in ops
    assert ("J", 72) in ops  # FSHIP_25


def test_fship_24_and_blin66_6_csr_d2_trims(stacked, csr_d2_bytes, iso_api, scripts_dir):
    """#71 FSHIP_24 and #255 BLIN66_6: CSR trims live on D2 (D1==pristine)."""
    import sys

    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from lzs import decompress_all_with_header

    extract_file, _ = iso_api
    for stem in ("FSHIP_24", "BLIN66_6"):
        got = extract_file(stacked, f"FIELD/{stem}.DAT")
        exp = extract_file(csr_d2_bytes, f"FIELD/{stem}.DAT")
        assert decompress_all_with_header(got) == decompress_all_with_header(exp)


def test_movie_id_grown_for_path_mids(stacked, iso_api):
    extract_file, _ = iso_api
    mid = extract_file(stacked, "MINT/MOVIE_ID.BIN")
    assert len(mid) // 20 >= 60  # need ids 54..59


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

def test_movie_id_stays_in_place_lba(stacked, csr_d1_bytes, iso_api):
    """MOVIE_ID must not relocate near EOF (DuckStation seek 80:52:34 failed)."""
    extract_file, find_file = iso_api
    got = find_file(stacked, "MINT/MOVIE_ID.BIN")
    csr = find_file(csr_d1_bytes, "MINT/MOVIE_ID.BIN")
    assert got.lba == csr.lba, (got.lba, csr.lba)
    assert got.lba < 200_000
    assert len(extract_file(stacked, "MINT/MOVIE_ID.BIN")) // 20 >= 60

def test_image_under_80_minute_cd(stacked):
    """DuckStation rejects seeks near/past ~80:00 lead-out for CD images."""
    from psx_mode2_iso import SECTOR
    max_lba = len(stacked) // SECTOR - 1
    hard = 80 * 60 * 75 - 150  # 80:00:00
    assert max_lba < hard, max_lba

def test_break_path_losin2_bit_lost2_cos(stacked, iso_api, csr_d2_bytes, scripts_dir):
    """D1→2 break: LOSIN2 leaves bit4 ON; LOST2 a455+bit → #526; COS reaches ASK."""
    import sys
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from field_dat import load_field_dat, op_size
    from ff7_opcodes import OPCODE_NAMES
    from helpers import same_or_prefix

    extract_file, _ = iso_api
    # LOST2 still pure CSR D2 body (gate is flags + COS open)
    assert same_or_prefix(
        extract_file(stacked, "FIELD/LOST2.DAT"),
        extract_file(csr_d2_bytes, "FIELD/LOST2.DAT"),
    )
    # LOSIN2 must BITON 84#4 not BITOFF
    fd = load_field_dat(extract_file(stacked, "FIELD/LOSIN2.DAT"))
    saw_on = False
    for sc in fd.scripts:
        pos = 0
        while pos < len(sc.raw):
            op = sc.raw[pos]
            sz = max(op_size(sc.raw, pos), 1)
            chunk = sc.raw[pos : pos + sz]
            assert chunk.hex() != "83308404", "LOSIN2 still clears break bit"
            if chunk.hex() == "82308404":
                saw_on = True
            pos += sz
    assert saw_on

    def sim_lost2(dat, gm=0xA455, bit84=1 << 4):
        fd = load_field_dat(dat)
        for sc in fd.scripts:
            if sc.entity != "init" or sc.slot != 0:
                continue
            raw, pos = sc.raw, 0
            for _ in range(80):
                op = raw[pos]
                sz = max(op_size(raw, pos), 1)
                chunk = raw[pos : pos + sz]
                name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
                if name == "IFUB":
                    c, e, v = chunk[4], chunk[5], chunk[3]
                    cond = bool(bit84 & (1 << v)) if c == 9 else False
                    fail = (pos + sz - 1) + e
                    pos = fail if not cond else pos + sz
                    continue
                if name == "IFUW":
                    v = int.from_bytes(chunk[4:6], "little")
                    c, e = chunk[6], chunk[7]
                    table = {0: gm == v, 1: gm != v, 2: gm > v, 3: gm < v, 4: gm >= v, 5: gm <= v}
                    cond = table.get(c, False)
                    fail = (pos + sz - 1) + e
                    pos = fail if not cond else pos + sz
                    continue
                if name == "JMPF":
                    pos = pos + sz + chunk[1]
                    continue
                if name == "RET":
                    return "RET"
                if name.startswith("MAPJUMP"):
                    return f"MJ{int.from_bytes(chunk[1:3], 'little')}"
                pos += sz
        return "miss"

    assert sim_lost2(extract_file(stacked, "FIELD/LOST2.DAT")) == "MJ526"

    # COS a455 reaches ASK
    fd = load_field_dat(extract_file(stacked, "FIELD/COS_BTM2.DAT"))
    gm = 0xA455
    saw_ask = False
    for sc in fd.scripts:
        if sc.entity != "directr" or sc.slot != 0:
            continue
        raw, pos = sc.raw, 0
        for _ in range(250):
            if pos >= len(raw):
                break
            op = raw[pos]
            sz = max(op_size(raw, pos), 1)
            chunk = raw[pos : pos + sz]
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
            if name == "IFUB":
                pos = (pos + sz - 1) + chunk[5]
                continue
            if name in ("IFUW", "IFSW"):
                v = int.from_bytes(chunk[4:6], "little")
                c, e = chunk[6], chunk[7]
                table = {0: gm == v, 1: gm != v, 2: gm > v, 3: gm < v, 4: gm >= v, 5: gm <= v}
                cond = table.get(c, False)
                fail = (pos + sz - 1) + e
                pos = fail if not cond else pos + sz
                continue
            if name == "JMPF":
                pos = pos + sz + chunk[1]
                continue
            if name == "RET":
                break
            if name == "ASK":
                saw_ask = True
                break
            pos += sz
    assert saw_ask

    fd = load_field_dat(extract_file(stacked, "FIELD/BLACKBGB.DAT"))
    for sc in fd.scripts:
        pos = 0
        while pos < len(sc.raw):
            op = sc.raw[pos]
            sz = max(op_size(sc.raw, pos), 1)
            name = OPCODE_NAMES[op] if op < len(OPCODE_NAMES) else ""
            assert name != "DSKCG"
            pos += sz

