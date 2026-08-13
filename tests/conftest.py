"""Shared paths + fixtures for single-disc / builder regression tests."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CSR_ROOT = Path(
    __import__("os").environ.get("FF7_CSR_ROOT", str(ROOT.parent / "Final-Fantasy-7-CSR"))
).expanduser().resolve()
SITE_ROOT = Path(
    __import__("os").environ.get(
        "FF7_SITE_ROOT", str(ROOT.parent / "individualcontributordev.github.io")
    )
).expanduser().resolve()

SECTOR = 2352
CSR_BASE_ID = "csr-v0.14.1"
SD_ON_CSR_PREFIX = "single-disc-on-csr-v"
SD_ON_CSR_DELTA_PREFIX = "single-disc-on-csr-delta-v"
MOVIES_PREFIX = "single-disc-csr-manip-movies-v"
ENDINGS_PREFIX = "single-disc-endings-v"


def _load_modding_apply_layer():
    """Load this repo's apply_layer (2352 pad) — never CSR's unpadded copy."""
    path = SCRIPTS / "apply_layer.py"
    spec = importlib.util.spec_from_file_location("apply_layer_modding", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.apply_layer


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def scripts_dir() -> Path:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    return SCRIPTS


@pytest.fixture(scope="session")
def csr_root() -> Path:
    return CSR_ROOT


@pytest.fixture(scope="session")
def site_root() -> Path:
    return SITE_ROOT


@pytest.fixture(scope="session")
def apply_layer():
    return _load_modding_apply_layer()


@pytest.fixture(scope="session")
def manifest() -> dict:
    return json.loads((ROOT / "builder" / "manifest.json").read_text(encoding="utf-8"))


def _enabled_addons(manifest: dict, prefix: str) -> list[str]:
    out = []
    for a in manifest.get("addons") or []:
        aid = str(a.get("id") or "")
        if aid.startswith(prefix) and a.get("enabled", True):
            out.append(aid)
    return sorted(out)


def _version_key(pid: str) -> tuple:
    ver = pid.split("-v", 1)[-1]
    parts = []
    for p in ver.replace("-", ".").split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _sd_on_csr_apply_key(pid: str) -> tuple:
    """Core first (rank 20), then path/ref autos (rank 21)."""
    if "single-disc-on-csr-ref-" in pid:
        return (1, _version_key(pid))
    if pid.startswith(SD_ON_CSR_PREFIX):
        ver = pid.split("-v", 1)[-1]
        if ver.startswith("0.1.26"):
            return (1, _version_key(pid))
        return (0, _version_key(pid))
    return (2, _version_key(pid))


@pytest.fixture(scope="session")
def latest_sd_on_csr(manifest: dict) -> str:
    """Player-facing single-disc-on-csr core (not path/ref autos)."""
    ids = [
        a
        for a in _enabled_addons(manifest, SD_ON_CSR_PREFIX)
        if "ref-" not in a and not a.endswith("v0.1.26")
    ]
    # also include packs that start with prefix via ref separately
    if not ids:
        pytest.skip("no enabled single-disc-on-csr core pack in manifest")
    return max(ids, key=_version_key)


@pytest.fixture(scope="session")
def sd_on_csr_stack(manifest: dict) -> list[str]:
    """Enabled single-disc-on-csr packs + ref pack in apply order."""
    ids = _enabled_addons(manifest, SD_ON_CSR_PREFIX)
    ids += _enabled_addons(manifest, "single-disc-on-csr-ref-v")
    seen = set()
    out = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    if not out:
        pytest.skip("no enabled single-disc-on-csr pack in manifest")
    return sorted(out, key=_sd_on_csr_apply_key)


@pytest.fixture(scope="session")
def latest_movies(manifest: dict) -> str:
    ids = _enabled_addons(manifest, MOVIES_PREFIX)
    if not ids:
        pytest.skip("no enabled manip-movies pack")
    return max(ids)  # ids embed full version string; lexical ok for 0.1.x


@pytest.fixture(scope="session")
def endings_parts(manifest: dict) -> list[str]:
    ids = _enabled_addons(manifest, ENDINGS_PREFIX)
    return sorted(ids)


@pytest.fixture(scope="session")
def layer_path(root: Path, manifest: dict):
    def _lp(pack_id: str, disc: int = 1) -> Path:
        # Prefer manifest discs[] (may point at a shared core layer folder).
        for a in manifest.get("addons") or []:
            if a.get("id") != pack_id:
                continue
            rel = (a.get("discs") or {}).get(str(disc))
            if rel:
                cand = (root / "builder" / str(rel).lstrip("./")).resolve()
                if cand.is_file():
                    return cand
            break
        p = root / "builder" / pack_id / "layers" / f"disc{disc}.layer.json"
        if p.is_file():
            return p
        pack_json = root / "builder" / pack_id / "pack.json"
        if pack_json.is_file():
            pack = json.loads(pack_json.read_text(encoding="utf-8"))
            rel = (pack.get("discs") or {}).get(str(disc))
            if rel:
                cand = (root / "builder" / pack_id / rel).resolve()
                if cand.is_file():
                    return cand
                cand = (root / "builder" / str(rel).lstrip("./")).resolve()
                if cand.is_file():
                    return cand
        raise FileNotFoundError(p)

    return _lp


def _pristine_ok() -> bool:
    p = ROOT / "workspace" / "pristine" / "FINALFANTASY7_D1.bin"
    return p.is_file() and p.stat().st_size > 100_000_000


def _csr_cache_ok() -> bool:
    p = CSR_ROOT / "cache" / "csr" / "FINALFANTASY7_D1.bin"
    return p.is_file() and p.stat().st_size > 100_000_000


@pytest.fixture(scope="session")
def require_discs():
    if not _pristine_ok() and not _csr_cache_ok():
        pytest.skip("pristine/CSR disc images not available")
    return True


@pytest.fixture(scope="session")
def csr_d1_bytes(require_discs, apply_layer) -> bytes:
    """CSR v0.14.1 Disc 1 image (cache preferred)."""
    cache = CSR_ROOT / "cache" / "csr" / "FINALFANTASY7_D1.bin"
    if cache.is_file():
        return cache.read_bytes()
    # build from pristine + layer
    from disc_sources import load_csr_image  # noqa: WPS433

    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    return bytes(load_csr_image(1))


@pytest.fixture(scope="session")
def csr_d2_bytes(require_discs) -> bytes:
    cache = CSR_ROOT / "cache" / "csr" / "FINALFANTASY7_D2.bin"
    if cache.is_file():
        return cache.read_bytes()
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from disc_sources import load_csr_image  # noqa: WPS433

    return bytes(load_csr_image(2))


@pytest.fixture(scope="session")
def pristine_d2_bytes(require_discs) -> bytes:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from disc_sources import pristine_bin  # noqa: WPS433

    p = pristine_bin(2)
    if not p.is_file():
        pytest.skip(f"missing pristine D2: {p}")
    return p.read_bytes()


@pytest.fixture(scope="session")
def build_stack(apply_layer, layer_path, csr_d1_bytes):
    def _build(addon_ids: list[str], base: bytes | None = None) -> bytes:
        img = bytearray(base if base is not None else csr_d1_bytes)
        for aid in addon_ids:
            layer = json.loads(layer_path(aid).read_text(encoding="utf-8"))
            apply_layer(img, layer)
        return bytes(img)

    return _build
