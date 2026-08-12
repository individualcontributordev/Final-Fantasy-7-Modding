#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

cl = ROOT / "mods/single-disc/CHANGELOG.md"
ct = cl.read_text()
if "0.1.23" not in ct:
    cl.write_text(
        """## 0.1.23 (FSHIP_12 PARASHOT — Cloud Highwind deck FMV)

- User: CSR D2 movie PARASHOT positions Cloud; CSR+single-disc cut/broken.
- FSHIP_12 (#67) ad/3 on CSR: PMVIE 59 PARASHOT, 50 METEOFIX, 51 METEOSKY then MAPJUMP.
- Single-disc had stripped those Set+Play ops (movie trim).
- Restore CSR FSHIP_12.DAT + inject D2 PARASHOT/METEOFIX/METEOSKY into D1 mids 59/50/51.
- Keeps MD8_52 NRCRL (0.1.22) and MD8_5 NRCRLB (0.1.21). Prefer path fields unchanged.

"""
        + ct
    )
    print("changelog")

seed = ROOT / "mods/single-disc/patches/csr-manip-movie-seed.txt"
t = seed.read_text()
if "PARASHOT" not in t:
    seed.write_text(
        t.rstrip()
        + """

# FSHIP_12 (#67) ad/3: PARASHOT + meteo pair (Cloud Highwind). Shipped v0.1.23.
2 PARASHOT.MOV ->OPENINGE.MOV
2 METEOFIX.MOV ->MTCRL.STR
2 METEOSKY.MOV ->MTNVL.STR
"""
    )
    print("seed")

(ROOT / "mods/single-disc/VERSION").write_text("0.1.23\n")

(ROOT / "docs/findings/2026-08-13-fship12-parashot-cloud-position.md").write_text(
    """# Finding: CSR+single-disc missing PARASHOT on FSHIP_12

**Compare:** CSR Disc 2 multi vs CSR + single-disc.
**User:** the movie is called PARASHOT (positions Cloud).

## Path

| Id | Field | CSR D2 |
|---:|-------|--------|
| 67 | FSHIP_12 | ad/3 PMVIE **59 PARASHOT**, **50 METEOFIX**, **51 METEOSKY** then MAPJUMP |
| 779 | MD8_52 | NRCRL then FSHIP_25 (fixed v0.1.22) |
| 731 | MD8_5 | NRCRLB (fixed v0.1.21) |

## Root cause

Single-disc movie-trim removed FSHIP_12 Set+Play. D1 mid59 was OPENINGE not PARASHOT.
Same script block needs mid50/51 (METEOFIX/METEOSKY) for the full CSR deck FMV sequence.

## Fix (v0.1.23)

- Restore CSR FSHIP_12.DAT.
- Inject D2 PARASHOT -> D1 OPENINGE (mid59); METEOFIX->MTCRL; METEOSKY->MTNVL.
"""
)

fr = ROOT / "docs/findings/README.md"
rt = fr.read_text()
row = (
    "| 2026-08-13 | [fship12-parashot-cloud-position](2026-08-13-fship12-parashot-cloud-position.md) "
    "| SD missing FSHIP_12 PARASHOT (Cloud Highwind deck FMV) |\n"
)
if "fship12-parashot-cloud-position" not in rt:
    lines = rt.splitlines(True)
    out = []
    ins = False
    for i, ln in enumerate(lines):
        out.append(ln)
        if (not ins) and ln.startswith("|---") and i > 0 and "Date" in lines[i - 1]:
            out.append(row)
            ins = True
    fr.write_text("".join(out))

(ROOT / "docs/INSTRUCTIONS.md").write_text(
    """# INSTRUCTIONS — playtest single-disc v0.1.23 (PARASHOT)

## What changed

CSR Disc 2 Highwind deck movie **PARASHOT** (FSHIP_12) was stripped on single-disc.
v0.1.23 restores FSHIP_12 Set+Play and injects D2 PARASHOT (+ METEOFIX/METEOSKY).
MD8_52 NRCRL / MD8_5 NRCRLB / Hojo / break still kept from prior ships.

## Build

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base CSR, Single-disc only (CSR+ off)
3. APPLIED: **single-disc-on-csr-v0.1.23** (+ manip-movies + endings auto)
4. Build Disc 1

## Test

| Path | Expect |
|------|--------|
| Highwind deck / FSHIP_12 | **PARASHOT** plays fully (Cloud positioned) like CSR D2 |
| MD8_52 / MD8_5 | Still correct FMVs |
| Hojo / disc break / waterfall | Still OK |
"""
)
print("docs ok")
