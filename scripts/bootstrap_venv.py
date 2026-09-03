#!/usr/bin/env python3
"""Create ``.venv`` at the repo root and install ``requirements.txt``."""

from __future__ import annotations

import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / ".venv"
REQUIREMENTS = ROOT / "requirements.txt"


def venv_python(root: Path) -> Path:
	if sys.platform == "win32":
		return root / "Scripts" / "python.exe"
	return root / "bin" / "python"


def main() -> int:
	if not REQUIREMENTS.is_file():
		raise SystemExit(f"Missing {REQUIREMENTS}")
	py = venv_python(VENV)
	if py.is_file():
		print(f"Reusing {VENV}")
	else:
		print(f"Creating {VENV} with {sys.executable}")
		venv.EnvBuilder(with_pip=True).create(VENV)
	if not py.is_file():
		raise SystemExit(f"venv python missing: {py}")
	subprocess.run(
		[str(py), "-m", "pip", "install", "-r", str(REQUIREMENTS)],
		check=True,
	)
	if sys.platform == "win32":
		print("\nActivate, then use python (not python3 — that is often still the Store shim):")
		print(r"  .venv\Scripts\activate")
		print(r"  python scripts\rebuild_on_base.py all")
	else:
		print("\nActivate, then run scripts as usual:")
		print("  source .venv/bin/activate")
		print("  python scripts/rebuild_on_base.py all")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
