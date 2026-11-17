"""fanfare-skip's ``build_on_base`` (shared base-image/pack/manifest helpers) as ``fb``.

Every mod has its own ``build_on_base.py``, so it can't be a plain import.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parents[2] / "mods" / "fanfare-skip" / "scripts" / "build_on_base.py"
_spec = importlib.util.spec_from_file_location("fanfare_build_on_base", _PATH)
fb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fb)
