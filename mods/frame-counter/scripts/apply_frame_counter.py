#!/usr/bin/env python3
"""Apply the frame counter sites to a retail/CSR-family disc 1 image in place (--revert undoes).
Reuses the new-game-plus applier with this mod's site table; run repair_mode2_edc.py afterwards."""
import sys
from pathlib import Path

_MOD = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_MOD.parent / "new-game-plus" / "scripts"))
import apply_new_game_plus as ngp  # noqa: E402

ngp._SITES = _MOD / "patches" / "frame-counter-sites.txt"
if __name__ == "__main__":
	ngp.main()
