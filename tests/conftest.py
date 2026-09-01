"""Shared fixtures for the remaining publish-path tests."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CSR_ROOT = Path(
    __import__("os").environ.get(
        "FF7_CSR_ROOT", str(ROOT.parent / "Final-Fantasy-7-CSR")
    )
).expanduser().resolve()


def _load_apply_layer():
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
def apply_layer():
    return _load_apply_layer()
