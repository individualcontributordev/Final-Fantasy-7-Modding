"""Resolve pristine, cached, and CSR-base images for this repository."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .layer import apply_layer

ROOT = Path(__file__).resolve().parents[2]
PRISTINE_DIR = ROOT / "workspace" / "pristine"
CACHE_DIR = ROOT / "cache"
CSR_BASES = ("csr", "csr-plus", "highwind")
ALL_BASES = CSR_BASES + ("clean",)


def expand_base_names(tokens: list[str]) -> list[str]:
    """Resolve CLI base names, preserving order and dropping duplicates.

    ``all`` means every published base including ``clean``. Leaving clean out
    of ``all`` let the pristine packs sit unrebuilt for weeks, because nothing
    in a run says which base you skipped. Use ``csr-family`` after a base
    version bump, when the pristine packs provably cannot have changed.
    """
    wanted: list[str] = []
    for token in tokens:
        if token == "all":
            wanted.extend(ALL_BASES)
        elif token == "csr-family":
            wanted.extend(CSR_BASES)
        elif token in ALL_BASES:
            wanted.append(token)
        else:
            raise SystemExit(
                f"Unknown base {token!r}. Use all, csr-family, clean, csr, "
                "csr-plus, or highwind."
            )
    return list(dict.fromkeys(wanted))


def pristine_bin(disc: int) -> Path:
    return PRISTINE_DIR / f"FINALFANTASY7_D{disc}.bin"


def default_pristine_arg(disc: int = 1) -> Path:
    return pristine_bin(disc)


def cache_bin_path(flavor: str, disc: int) -> Path:
    return CACHE_DIR / flavor / f"FINALFANTASY7_D{disc}.bin"


def csr_root(cli_root: Path | None = None) -> Path | None:
    if cli_root is not None:
        return cli_root.expanduser().resolve()
    value = os.environ.get("FF7_CSR_ROOT")
    return Path(value).expanduser().resolve() if value else None


def _csr_base_layer(csr: Path, base_id: str, disc: int) -> Path:
    manifest_path = csr / "builder" / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"Missing CSR manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest.get("bases") or []:
        if str(entry.get("id", "")) != base_id:
            continue
        relative = (entry.get("discs") or {}).get(str(disc))
        if not relative:
            raise SystemExit(f"{base_id}: no CSR layer for disc {disc}")
        path = (csr / "builder" / str(relative).lstrip("./")).resolve()
        if not path.is_file():
            raise SystemExit(f"Missing CSR base layer: {path}")
        return path
    raise SystemExit(f"Unknown CSR base id {base_id!r}")


def csr_base_version(base_id: str, csr: Path | None = None) -> str:
    """Read the published version of a CSR base, e.g. csr-plus -> "0.2.1".

    A mod layer is a byte diff against one specific base build, so the mod has
    to record which build it was cut from. Pristine ``clean`` never changes and
    carries no version.
    """
    if base_id in ("clean", "unmodified"):
        return ""

    csr_path = csr_root(csr)
    if csr_path is None:
        raise SystemExit(
            f"Cannot read the {base_id} version: set FF7_CSR_ROOT or pass --csr-root."
        )
    version_path = csr_path / "builder" / base_id / "VERSION"
    if not version_path.is_file():
        raise SystemExit(f"Missing base version file: {version_path}")
    version = version_path.read_text(encoding="utf-8").strip().splitlines()[0].strip()
    if not version:
        raise SystemExit(f"Empty base version file: {version_path}")
    return version


def ensure_parent_image(
    *,
    base_id: str,
    disc: int,
    pristine: Path | None = None,
    csr: Path | None = None,
    use_cache: bool = True,
) -> tuple[bytes, Path]:
    """Return the parent BIN, reconstructing into this repo's cache on miss.

    Order: this repo's ``cache/<base>/``, then pristine plus the CSR base
    layer from ``$FF7_CSR_ROOT/builder``. CSR's cache directory is never read.
    """
    if base_id in ("clean", "unmodified"):
        pristine_path = pristine or pristine_bin(disc)
        if not pristine_path.is_file():
            raise SystemExit(f"Missing pristine: {pristine_path}")
        return pristine_path.read_bytes(), pristine_path

    if base_id not in CSR_BASES:
        raise SystemExit(f"Unknown compatible base {base_id!r}")

    cached = cache_bin_path(base_id, disc)
    if use_cache and cached.is_file():
        print(f"  parent cache hit: {cached}")
        return cached.read_bytes(), cached

    csr_path = csr_root(csr)
    if csr_path is None:
        raise SystemExit(
            f"Missing parent image {cached}. Pass --parent, place the base BIN "
            "in this repo's cache/<base>/, or set FF7_CSR_ROOT / --csr-root "
            "to rebuild it from pristine plus the CSR base layer."
        )

    pristine_path = pristine or pristine_bin(disc)
    if not pristine_path.is_file():
        raise SystemExit(f"Missing pristine (needed to reconstruct {base_id}): {pristine_path}")
    layer_path = _csr_base_layer(csr_path, base_id, disc)
    print(f"  parent miss -- apply {layer_path.name} onto pristine -> {cached}")
    image = bytearray(pristine_path.read_bytes())
    apply_layer(image, json.loads(layer_path.read_text(encoding="utf-8")))
    data = bytes(image)
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(data)
    print(f"  wrote {cached} ({len(data)} bytes)")
    return data, cached
