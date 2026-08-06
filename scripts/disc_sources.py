"""Resolve pristine bins and CSR layers for FIELD tools (no CLI).

Environment (optional):
  FF7_PRISTINE_DIR  directory with FINALFANTASY7_D1.bin … D3
  FF7_CSR_ROOT      Final-Fantasy-7-CSR repo root
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pristine_dir() -> Path:
    env = os.environ.get("FF7_PRISTINE_DIR")
    if env:
        return Path(env).expanduser().resolve()
    return (ROOT / "workspace/pristine").resolve()


def csr_root() -> Path:
    env = os.environ.get("FF7_CSR_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    cand = (ROOT.parent / "Final-Fantasy-7-CSR").resolve()
    if cand.is_dir():
        return cand
    alt = (ROOT / "../Final-Fantasy-7-CSR").resolve()
    return alt


def pristine_bin(disc: int) -> Path:
    if disc not in (1, 2, 3):
        raise ValueError(f"disc must be 1..3, got {disc}")
    return pristine_dir() / f"FINALFANTASY7_D{disc}.bin"


def csr_layer(disc: int) -> Path:
    if disc not in (1, 2, 3):
        raise ValueError(f"disc must be 1..3, got {disc}")
    return (
        csr_root()
        / "builder/csr-v0.14.1/layers"
        / f"disc{disc}.layer.json"
    )


def load_pristine_image(disc: int) -> bytearray:
    path = pristine_bin(disc)
    if not path.is_file():
        raise FileNotFoundError(f"missing pristine disc image: {path}")
    return bytearray(path.read_bytes())


def load_csr_image(disc: int) -> bytearray:
    """Pristine disc N + CSR v0.14.1 layer for that disc."""
    from apply_layer import apply_layer  # local import: scripts/ on path

    img = load_pristine_image(disc)
    layer_path = csr_layer(disc)
    if not layer_path.is_file():
        raise FileNotFoundError(f"missing CSR layer: {layer_path}")
    apply_layer(img, json.loads(layer_path.read_text(encoding="utf-8")))
    return img


def normalize_field_name(name: str) -> str:
    """DEL1 or DEL1.DAT → DEL1."""
    n = name.strip().upper()
    if n.endswith(".DAT"):
        n = n[: -len(".DAT")]
    if not n or "/" in n or "\\" in n:
        raise ValueError(f"bad field map name: {name!r}")
    return n


def field_iso_path(name: str) -> str:
    return f"FIELD/{normalize_field_name(name)}.DAT"
