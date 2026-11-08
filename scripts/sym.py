#!/usr/bin/env python3
"""Look up FF7 (US) symbols from the local ff7-decomp checkout (read-only reference).

  python scripts/sym.py overlays                  # overlay -> load address, disc file, offset formula
  python scripts/sym.py NAME [-o field] [-a]      # substring search; -a also lists func_/D_ autonames
  python scripts/sym.py 0x800A1234 [-o field]     # address -> exact / nearest preceding symbol + file offset

Overlays share load addresses, so an address is matched against every overlay unless -o narrows it.
Offsets are into the decompressed (.dec) overlay; main is SCUS_941.63 (PSX-EXE header 0x800).
Needs: git clone https://github.com/Xeeynamo/ff7-decomp external/ff7-decomp
"""
import argparse
import re
import sys
from bisect import bisect_right
from pathlib import Path

CFG = Path(__file__).resolve().parents[1] / "external/ff7-decomp/config"
HDR = 0x800
# overlay: (load address, disc file, symbol files)
OVERLAYS = {
    "main": (0x80010000, "SCUS_941.63", ["symbols.main.us.txt", "sym_extern.us.txt"]),
    "field": (0x800A0000, "FIELD/FIELD.BIN", ["symbols.field.us.txt"]),
    "world": (0x800A0000, "WORLD/WORLD.BIN", ["symbols.world.txt"]),
    "battle": (0x800A0000, "BATTLE/BATTLE.X", ["symbols.battle.txt"]),
    "brom": (0x800A0000, "BATTLE/BROM.X", ["symbols.brom.us.txt"]),
    "dschange": (0x800A0000, "FIELD/DSCHANGE.X", ["symbols.dschange.us.txt"]),
    "ending": (0x800A0000, "FIELD/ENDING.X", ["symbols.ending.us.txt"]),
    "batini": (0x801B0000, "BATTLE/BATINI.X", ["symbols.batini.txt"]),
    "barrier": (0x801B0000, "MAGIC/BARRIER.BIN", ["symbols.magic-barrier.us.txt"]),
    "lv5deth": (0x801B0000, "MAGIC/LV5DETH.BIN", ["symbols.magic-lv5deth.us.txt"]),
    "bginmenu": (0x801D0000, "MENU/BGINMENU.MNU", ["symbols.bginmenu.us.txt"]),
    "cnfgmenu": (0x801D0000, "MENU/CNFGMENU.MNU", ["symbols.cnfgmenu.us.txt"]),
    "savemenu": (0x801D0000, "MENU/SAVEMENU.MNU", ["symbols.savemenu.us.txt"]),
    "itemmenu": (0x801D0000, "MENU/ITEMMENU.MNU", ["symbols.itemmenu.us.txt"]),
}
LINE = re.compile(r"^(\w+)\s*=\s*(0x[0-9a-fA-F]+);")
AUTO = re.compile(r"^_?(func|D|jtbl|L)_[0-9A-Fa-f]{8}$")
NEAR = 0x1000  # nearest-preceding matches farther than this are noise across overlays


def load(ov):
    syms = []
    for f in OVERLAYS[ov][2]:
        for line in (CFG / f).read_text().splitlines():
            m = LINE.match(line)
            if m:
                syms.append((int(m[2], 16), m[1]))
    return sorted(syms)


def file_off(ov, addr):
    base = OVERLAYS[ov][0]
    return addr - base + (HDR if ov == "main" else 0) if addr >= base else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("query", help="'overlays', a name substring, or an address")
    ap.add_argument("-o", "--overlay", choices=OVERLAYS)
    ap.add_argument("-a", "--all", action="store_true", help="include auto-generated names")
    a = ap.parse_args()
    if not CFG.is_dir():
        sys.exit(f"missing {CFG}; see --help")
    ovs = [a.overlay] if a.overlay else list(OVERLAYS)

    if a.query == "overlays":
        for ov, (base, f, _) in OVERLAYS.items():
            print(f"{ov:9} {base:#010x}  {f:20} off = addr - {base:#x}" + (f" + {HDR:#x}" if ov == "main" else ""))
    elif re.fullmatch(r"(0x)?[0-9a-fA-F]{6,8}", a.query):
        t = int(a.query, 16)
        for ov in ovs:
            syms = load(ov)
            i = bisect_right(syms, (t, "￿")) - 1
            if i < 0 or t - syms[i][0] > NEAR:
                continue
            addr, name = syms[i]
            off = file_off(ov, t)
            print(f"{ov:9} {name}" + (f"+{t - addr:#x}" if t != addr else "") + (f"  file+{off:#x}" if off is not None else ""))
    else:
        q = a.query.lower()
        for ov in ovs:
            for addr, name in load(ov):
                if q in name.lower() and (a.all or not AUTO.match(name)):
                    print(f"{ov:9} {addr:#010x} {name}")


if __name__ == "__main__":
    main()
