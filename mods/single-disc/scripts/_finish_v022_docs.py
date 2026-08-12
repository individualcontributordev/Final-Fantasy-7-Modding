#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

cl = ROOT / "mods/single-disc/CHANGELOG.md"
ct = cl.read_text()
if "0.1.22" not in ct:
    cl.write_text(
        """## 0.1.22 (MD8_52 NRCRL — Cloud position FMV)

- CSR multi-disc MD8_52 (#779) plays PMVIE mid=52 (NRCRL.MOV) then MAPJUMP FSHIP_25 (#72).
- Single-disc had stripped Set+Play (movie trim); jump ran with no FMV — Cloud mis-positioned vs CSR D2.
- Restore CSR MD8_52.DAT (Set+Play) and inject D2 NRCRL into D1 mid52 (MTNVL2 slot, grow).
- Keeps 0.1.21 NRCRLB mid53 (MD8_5). Prefer fields LOSIN2/LOST2/CANON_2/BLACKBGB unchanged.

"""
        + ct
    )
    print("changelog")

seed = ROOT / "mods/single-disc/patches/csr-manip-movie-seed.txt"
t = seed.read_text()
if "NRCRL.MOV ->MTNVL2" not in t and "NRCRL.MOV ->MTNVL2.STR" not in t:
    seed.write_text(
        t.rstrip()
        + """

# MD8_52 (#779): PMVIE mid=52 D2 NRCRL (Cloud position then FSHIP_25). Shipped v0.1.22.
2 NRCRL.MOV ->MTNVL2.STR
"""
    )
    print("seed")

(ROOT / "mods/single-disc/VERSION").write_text("0.1.22\n")

(ROOT / "docs/findings/2026-08-13-md8-52-nrcrl-cloud-position.md").write_text(
    """# Finding: CSR+single-disc MD8_52 Cloud-position FMV missing

**Compare:** CSR Disc 2 multi vs CSR + single-disc Disc 1.
**Symptom:** On CSR a movie plays that leaves Cloud in the correct place; on single-disc the movie is cut/broken or skipped.

## Maps

| Id | Field | Role |
|---:|-------|------|
| 731 | MD8_5 | DW approach; PMVIE mid=53 NRCRLB (fixed v0.1.21) |
| 779 | MD8_52 | Follow-up; PMVIE mid=52 NRCRL then MAPJUMP #72 FSHIP_25 |

## Root cause

1. Field: single-disc movie-trim removed PMVIE+MOVIE from MD8_52 dir3/0 (audit pairs 1 to 0) because D1 mid52 resolved to wrong MTNVL2.STR.
2. Script still MAPJUMP to FSHIP_25 without the FMV that positions the party/Cloud on CSR D2.

## Fix (v0.1.22)

- Restore CSR MD8_52.DAT (identical CSR D1/D2 scripts with Set+Play).
- Inject pristine D2 NRCRL.MOV into D1 movie id 52 (MTNVL2.STR slot; grew ISO).
- MOVIE_ID Form2 eng size/aux from source.

## Not changed

LOSIN2, LOST2, CANON_2, BLACKBGB, WHITE2, MD8_5 NRCRLB mid53.
"""
)

fr = ROOT / "docs/findings/README.md"
rt = fr.read_text()
row = (
    "| 2026-08-13 | [md8-52-nrcrl-cloud-position](2026-08-13-md8-52-nrcrl-cloud-position.md) "
    "| SD vs CSR D2: MD8_52 missing NRCRL FMV (Cloud position) |\n"
)
if "md8-52-nrcrl-cloud-position" not in rt:
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
    """# INSTRUCTIONS — playtest single-disc v0.1.22 (MD8_52 Cloud FMV)

## What changed

Vs CSR Disc 2 multi: after Diamond Weapon approach, MD8_52 should play NRCRL
(positions Cloud) then Highwind FSHIP_25.

Single-disc had removed that Set+Play; jump still happened so the movie felt cut/broken.

v0.1.22: restore MD8_52 movie ops + inject D2 NRCRL at mid52.
MD8_5 NRCRLB (v0.1.21) kept. Hojo/break untouched.

## Build

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base CSR, Single-disc only (CSR+ off)
3. APPLIED must include single-disc-on-csr-v0.1.22 (+ manip-movies + endings auto)
4. Build Disc 1

## Test

| Path | Expect |
|------|--------|
| DW Highwind path (no skip) | MD8_5 FMV, then MD8_52 NRCRL plays fully, Cloud ends correct, to FSHIP_25 |
| CSR D2 multi compare | Same movie/exit as multi-disc CSR |
| Hojo / disc1 to 2 break / waterfall | Still OK |
"""
)
print("docs ok")
