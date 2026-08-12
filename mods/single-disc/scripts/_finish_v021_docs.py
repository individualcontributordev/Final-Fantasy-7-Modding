#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

seed = ROOT / "mods/single-disc/patches/csr-manip-movie-seed.txt"
t = seed.read_text()
if "NRCRLB" not in t:
    seed.write_text(
        t.rstrip()
        + """

# MD8_5 (#731) Diamond Weapon approach after FSHIP_12 leave: PMVIE mid=53.
# D2=NRCRLB.MOV; D1 slot name NIVLSFS.MOV. Shipped in single-disc-on-csr-v0.1.21.
2 NRCRLB.MOV ->NIVLSFS.MOV
"""
    )
    print("seed updated")

cl = ROOT / "mods/single-disc/CHANGELOG.md"
ct = cl.read_text()
if "0.1.21" not in ct:
    cl.write_text(
        """## 0.1.21 (MD8_5 mid53 NRCRLB — Highwind 71 to 67 to 731)

- Path without COTA/Hojo skip: FSHIP_24 (#71) to FSHIP_12 (#67) to MD8_5 (#731).
- MAPJUMP 67 to 731 was already correct; MD8_5 plays PMVIE mid=53.
- On multi-disc D2 mid53 = NRCRLB.MOV; on D1 mid53 = NIVLSFS.MOV (wrong stream).
- Inject D2 NRCRLB Form2 into D1 NIVLSFS slot + MOVIE_ID eng size/aux.
- Does not change LOSIN2 / LOST2 / CANON_2 / BLACKBGB / WHITE2 / FSHIP FIELD vs 0.1.20.

"""
        + ct
    )
    print("changelog ok")

findings = ROOT / "docs/findings/2026-08-12-fship12-md8-5-mid53-nrcrlb.md"
findings.write_text(
    """# Finding: FSHIP_12 (#67) to MD8_5 (#731) stuck on single-disc

**Stack:** csr-v0.14.1 + single-disc-on-csr (<=0.1.20) + manip-movies
**Report:** CSR Highwind scenes without skip: field 71 to 67 to 731; transition from 67 felt broken.

## Maplist

| Id | Stem | Role |
|---:|------|------|
| 71 | fship_24 | Highwind interior (CSR D2) |
| 67 | fship_12 | Deck; ASK leave party; MAPJUMP 731 |
| 731 | md8_5 | Diamond Weapon approach field |

## What is not broken

- FSHIP_24 to FSHIP_12 MAPJUMP exists on CSR D2 FSHIP_24 (SD has those bytes).
- FSHIP_12 ad/31 MAPJUMP to #731 is byte-identical CSR D1 = CSR D2 = SD 0.1.20.
- Script table after FSHIP_12 movie trims still points at valid ad/31 ASK+MAPJUMP.

## Root cause

MD8_5 dir/0 (same on CSR D1/D2/SD):

1. Fade / lock controls
2. PMVIE mid=53 + MOVIE
3. SETWORD GameMoment progress
4. Unlock

Movie id 53 is disc-local:

| Disc | Sorted MOVIE name at id 53 |
|------|----------------------------|
| D2 / CSR multi | NRCRLB.MOV (correct) |
| D1 / single-disc | NIVLSFS.MOV (wrong) |

Wrong Form2 stream can hang before SETWORD — looks like 67 to 731 broken.

## Fix

single-disc-on-csr-v0.1.21: inject pristine D2 NRCRLB.MOV into D1 slot NIVLSFS.MOV
(mid 53) with Form2 MOVIE_ID eng size/aux.

Side effect: BLACKBG4 debug hub mv/1 mid53 also gets NRCRLB — acceptable.

## Not changed

LOSIN2 d1, LOST2 d2, CANON_2 d2, BLACKBGB strip, WHITE2 hybrid, FSHIP FIELD trims.

## Verify

FIELD FSHIP_12/24/MD8_5/CANON_2/LOSIN2/LOST2/BLACKBGB identical vs 0.1.20 after inject;
only MOVIE/NIVLSFS + MOVIE_ID change.
"""
)
print("finding ok")

fr = ROOT / "docs/findings/README.md"
rt = fr.read_text()
row = (
    "| 2026-08-12 | [fship12-md8-5-mid53-nrcrlb](2026-08-12-fship12-md8-5-mid53-nrcrlb.md) "
    "| SD: 71-67-731 hang = MD8_5 PMVIE mid53 wrong D1 movie (NRCRLB) |\n"
)
if "fship12-md8-5-mid53-nrcrlb" not in rt:
    lines = rt.splitlines(True)
    out = []
    ins = False
    for i, ln in enumerate(lines):
        out.append(ln)
        if (not ins) and ln.startswith("|---") and i > 0 and "Date" in lines[i - 1]:
            out.append(row)
            ins = True
    fr.write_text("".join(out))
    print("README ok")

vp = ROOT / "mods/single-disc/VERSION"
if vp.exists():
    vp.write_text("0.1.21\n")
    print("VERSION ok")

(ROOT / "docs/INSTRUCTIONS.md").write_text(
    """# INSTRUCTIONS — playtest single-disc v0.1.21 (MD8_5 / 71-67-731)

## What changed

CSR Highwind path without scene skip: field 71 (FSHIP_24) to 67 (FSHIP_12) to 731 (MD8_5)
could hang after leaving the deck.

Cause: MD8_5 plays movie id 53. On Disc 2 that is NRCRLB; on Disc 1 it was still NIVLSFS.
Wrong FMV blocked progress after the MAPJUMP (jump itself was fine).

Fix: single-disc-on-csr-v0.1.21 injects D2 NRCRLB into D1 mid53.
Prior Hojo/break/waterfall field fixes unchanged.

## COPY-PASTE — rebuild + play

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base: CSR
3. Add-on: Single-disc only (CSR+ scenes off)
4. Confirm APPLIED includes:
   - single-disc-on-csr-v0.1.21 (not 0.1.20)
   - single-disc-csr-manip-movies-v0.1.4 (auto)
5. Build Disc 1 zip and load in DuckStation.

## What to test

| Path | Expect |
|------|--------|
| No-skip Highwind / DW approach | 71 to 67 deck leave to 731 MD8_5 FMV then continue |
| Hojo CANON_2 + FMV audio | Still good (unchanged) |
| Disc 1 to 2 break (LOSIN2/LOST2) | Still good |
| Waterfall / LOSLAKE1 | Still good |

## If 731 still fails

Note whether MD8_5 loads (field art) vs black vs movie hang.
"""
)
print("INSTRUCTIONS ok")
print("done")
