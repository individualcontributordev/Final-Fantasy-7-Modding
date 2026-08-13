"""Builder JS contracts that single-disc relies on (no disc images)."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from helpers import extract_addon_apply_rank_fn, is_mode2_form1_py


@pytest.fixture(scope="module")
def builder_js(site_root: Path) -> str:
    p = site_root / "builder" / "builder.js"
    if not p.is_file():
        pytest.skip(f"site builder.js not found: {p}")
    return p.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def layer_js(site_root: Path) -> str:
    p = site_root / "builder" / "layer.js"
    if not p.is_file():
        pytest.skip(f"site layer.js not found: {p}")
    return p.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def edc_js(site_root: Path) -> str:
    p = site_root / "builder" / "edc.js"
    if not p.is_file():
        pytest.skip(f"site edc.js not found: {p}")
    return p.read_text(encoding="utf-8")


def test_addon_apply_rank_movies_before_single_disc(builder_js: str):
    rank = extract_addon_apply_rank_fn(builder_js)
    assert rank("single-disc-csr-manip-movies-v0.1.4") == 10
    assert rank("single-disc-on-csr-v0.1.24") == 20
    assert rank("single-disc-on-csr-v0.1.28") == 21
    assert rank("single-disc-on-csr-v0.1.27") == 21
    assert rank("single-disc-on-csr-v0.1.26") == 21
    assert rank("single-disc-on-csr-v0.1.25") == 21  # path-engine delta after core
    assert rank("single-disc-endings-v0.1.0-part1") == 30
    assert rank("field-encounter-25-v0.1.2") == 40
    assert rank("csr-plus-scene-hojo-v0.1.0") == 50
    # order invariant
    assert rank("single-disc-csr-manip-movies-v9") < rank("single-disc-on-csr-v9")
    assert rank("single-disc-on-csr-v0.1.24") < rank("single-disc-on-csr-v0.1.28")
    assert rank("single-disc-on-csr-v9") < rank("single-disc-endings-v9")
    assert rank("single-disc-endings-v9") < rank("csr-plus-scene-x")


def test_builder_js_contains_rank_function(builder_js: str):
    assert "function addonApplyRank" in builder_js
    assert "single-disc-csr-manip-movies" in builder_js
    # movies return 10, sd-on return 20
    body = builder_js[builder_js.find("function addonApplyRank") :][
        :800
    ]
    assert "return 10" in body
    assert "return 20" in body
    assert body.find("manip-movies") < body.find("single-disc-on-")


def test_layer_js_pads_grown_images_to_2352(layer_js: str):
    assert "SECTOR = 2352" in layer_js or "SECTOR=2352" in layer_js
    assert "modifiedBytes" in layer_js
    assert "size % SECTOR" in layer_js or "% SECTOR" in layer_js


def test_edc_js_skips_form2_audio_video(edc_js: str):
    assert "function isMode2Form1" in edc_js
    # critical: do not Form1-repair FMV payload tails
    assert "0x20" in edc_js  # Form2 bit
    assert "0x04" in edc_js  # audio
    assert "0x02" in edc_js  # video
    start = edc_js.find("function isMode2Form1")
    end = edc_js.find("\nexport function", start)
    if end < 0:
        end = start + 1200
    body = edc_js[start:end]
    assert "return false" in body
    assert "0x08" in body  # require Data bit
    assert "0x20" in body and "0x04" in body and "0x02" in body


def test_is_mode2_form1_python_mirror_matches_contract():
    """Synthetic sectors — Form1 data repaired; FMV/XA not."""

    def sector(mode=2, submode=0x08):
        s = bytearray(2352)
        s[0] = 0x00
        for i in range(1, 11):
            s[i] = 0xFF
        s[11] = 0x00
        s[15] = mode
        s[18] = submode
        return s

    assert is_mode2_form1_py(sector(2, 0x08)) is True  # data Form1
    assert is_mode2_form1_py(sector(2, 0x28)) is False  # Form2|data
    assert is_mode2_form1_py(sector(2, 0x42)) is False  # RT|video
    assert is_mode2_form1_py(sector(2, 0x64)) is False  # RT|Form2|audio
    assert is_mode2_form1_py(sector(2, 0x00)) is False  # no Data bit
    assert is_mode2_form1_py(sector(1, 0x08)) is False  # Mode1


def test_manifest_enables_sd_core_and_optional_path_delta(manifest: dict):
    enabled = [
        a
        for a in manifest.get("addons") or []
        if str(a.get("id", "")).startswith("single-disc-on-csr-v")
        and a.get("enabled", True)
    ]
    assert len(enabled) >= 1
    # One visible core + any number of uiHidden auto deltas (path-engine, music, …)
    visible = [e for e in enabled if not e.get("uiHidden") and not e.get("hidden")]
    hidden = [e for e in enabled if e.get("uiHidden") or e.get("hidden")]
    assert len(visible) == 1, f"visible SD cores: {[e['id'] for e in visible]}"
    core = visible[0]
    assert core.get("version")
    assert "v0.1.24" in core["id"] or core["id"].startswith("single-disc-on-csr-")
    for delta in hidden:
        aw = delta.get("autoIncludeWhen") or {}
        assert aw.get("addonSelected") == core["id"] or str(
            aw.get("addonSelected", "")
        ).startswith("single-disc-on-csr-"), delta["id"]


def test_manifest_movies_and_endings_enabled(manifest: dict):
    movies = [
        a
        for a in manifest.get("addons") or []
        if "single-disc-csr-manip-movies" in str(a.get("id", ""))
        and a.get("enabled", True)
    ]
    endings = [
        a
        for a in manifest.get("addons") or []
        if "single-disc-endings" in str(a.get("id", "")) and a.get("enabled", True)
    ]
    assert len(movies) == 1, movies
    assert len(endings) >= 1
