#!/usr/bin/env python3
"""Extract real FIELD/*.DAT map files from the pristine disc images.

This is a thin wrapper around the already-verified `scripts/extract_field_dat.py`
(which in turn uses `scripts/psx_mode2_iso.py`'s MODE2/2352 + ISO9660 directory
parsing). It intentionally does NOT reimplement disc/LGP parsing — that logic
already exists and is exercised elsewhere in this repo (see
`scripts/verify_built_disc.py`, `scripts/compare_field_dat.py`). Duplicating it
here would risk drifting from the verified implementation.

Usage:
    python3 extract_game_assets.py

Writes to data/extracted_fields/<NAME>.DAT.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
OUT_DIR = REPO_ROOT / "data" / "extracted_fields"

# (field name, disc number to try first) — field id 67 -> fship_12,
# field id 731 -> md8_5, per Final-Fantasy-7-CSR/scripts/field_maplist.py.
TARGETS = [
    ("FSHIP_12", 1),
    ("MD8_5", 2),
]


def extract_one(field: str, disc_hint: int) -> Path:
    out_path = OUT_DIR / f"{field}.DAT"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Try the hinted disc first, then fall back across the other two —
    # field->disc placement isn't hardcoded here to avoid asserting an
    # unverified fact; we let the real ISO directory lookup decide.
    discs = [disc_hint] + [d for d in (1, 2, 3) if d != disc_hint]
    last_err = None
    for disc in discs:
        cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "extract_field_dat.py"),
            "--from", f"pristine:{disc}",
            "--field", field,
            "-o", str(out_path),
        ]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        if proc.returncode == 0:
            print(proc.stdout.strip())
            return out_path
        last_err = proc.stderr.strip() or proc.stdout.strip()
    raise SystemExit(f"failed to extract {field} from any disc: {last_err}")


def main() -> int:
    for field, disc_hint in TARGETS:
        extract_one(field, disc_hint)
    print(f"\nDone. Files written to {OUT_DIR}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
