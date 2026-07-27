#!/usr/bin/env python3
"""Deprecated path — use mods/field-random-encounters/scripts/build_on_base.py"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

target = (
	Path(__file__).resolve().parents[1]
	/ "mods"
	/ "field-random-encounters"
	/ "scripts"
	/ "build_on_base.py"
)
sys.argv[0] = str(target)
runpy.run_path(str(target), run_name="__main__")
