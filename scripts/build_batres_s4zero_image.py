#!/usr/bin/env python3
"""Back-compat: s4=0 only. Prefer build_batres_ceremony_smoke.py."""
import runpy
from pathlib import Path
import sys
sys.argv = [sys.argv[0], "--no-anim-nop", "-o", "workspace/iso-extract/ff7_d1_batres_s4zero.bin"]
runpy.run_path(str(Path(__file__).resolve().parent / "build_batres_ceremony_smoke.py"), run_name="__main__")
