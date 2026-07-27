#!/usr/bin/env python3
"""Deprecated path — use mods/field-random-encounters/scripts/apply_force_stub_rcnt2.py"""
from __future__ import annotations

import importlib.util
import runpy
import sys
from pathlib import Path

_TARGET = (
	Path(__file__).resolve().parents[1]
	/ "mods/field-random-encounters/scripts/apply_force_stub_rcnt2.py"
)


def _load():
	name = "_field_encounter_apply_force_stub_rcnt2"
	spec = importlib.util.spec_from_file_location(name, _TARGET)
	if spec is None or spec.loader is None:
		raise ImportError(f"Cannot load {_TARGET}")
	mod = importlib.util.module_from_spec(spec)
	sys.modules[name] = mod
	spec.loader.exec_module(mod)
	return mod


if __name__ == "__main__":
	sys.argv[0] = str(_TARGET)
	runpy.run_path(str(_TARGET), run_name="__main__")
else:
	globals().update(
		{k: v for k, v in vars(_load()).items() if k not in {"__name__", "__file__"}}
	)
