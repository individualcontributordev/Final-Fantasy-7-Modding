#!/usr/bin/env python3
"""Deprecated path — use mods/field-random-encounters/scripts/apply_force_stub_rcnt2.py"""
from __future__ import annotations
import runpy, sys
from pathlib import Path
target = Path(__file__).resolve().parents[1] / "mods/field-random-encounters/scripts/apply_force_stub_rcnt2.py"
sys.argv[0] = str(target)
runpy.run_path(str(target), run_name="__main__")
