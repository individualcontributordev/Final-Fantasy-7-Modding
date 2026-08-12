#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

cl = ROOT / "mods/single-disc/CHANGELOG.md"
ct = cl.read_text()
if "0.1.24" not in ct:
    cl.write_text(
        """## 0.1.24 (path FMVs after manip-movies — PARASHOT/NRCRL unique LBAs)

- PARASHOT missing + MD8_5 glitch when manip-movies applied after SD core:
  shared movie LBAs clobbered path injects.
- Builder apply order: manip-movies then single-disc-on-csr.
- Pack bin-diffed vs CSR+movies; path FMVs force-append at unique EOF LBAs
  (PARASHOT, METEOFIX, METEOSKY, NRCRL, NRCRLB).
- JAIROFAL/CANONON alias preserved. FSHIP_12/MD8_52 CSR scripts restored.

"""
        + ct
    )
    print("changelog")

(ROOT / "mods/single-disc/VERSION").write_text("0.1.24\n")

(ROOT / "docs/INSTRUCTIONS.md").write_text(
    """# INSTRUCTIONS — single-disc v0.1.24 (PARASHOT + MD8_5)

## What broke

With CSR + single-disc + auto manip-movies, path FMVs (PARASHOT, NRCRL) were
written then overwritten by the movies pack (shared disc LBAs with JAIROFAL/etc).
Result: PARASHOT missing; MD8_5 mid53 stream/meta glitched.

## Fix v0.1.24

- Apply order: manip-movies first, then single-disc-on-csr.
- Single-disc pack rebuilds path FMVs at unique EOF LBAs after movies.
- FSHIP_12 plays PARASHOT (+ meteo); MD8_5 NRCRLB; MD8_52 NRCRL.

## Build

1. Hard-refresh builder
2. CSR + Single-disc only (CSR+ off)
3. APPLIED must show single-disc-on-csr-v0.1.24 and manip-movies v0.1.4
4. Build Disc 1

## Test

| Path | Expect |
|------|--------|
| FSHIP_12 | Full PARASHOT (Cloud position) |
| MD8_5 #731 | Clean NRCRLB FMV, field not glitched |
| MD8_52 | NRCRL then Highwind |
| Waterfall / Hojo / break | Still OK |
"""
)

(ROOT / "docs/findings/2026-08-13-path-fmv-movies-pack-clobber.md").write_text(
    """# Path FMV clobber by manip-movies pack

## Symptom

PARASHOT does not play; field 731 (MD8_5) glitched on CSR+single-disc with auto movies.

## Cause

Apply order was SD core then manip-movies. Movies pack grew JAIROFAL/CANONON and
rewrote MOVIE_ID/shared LBAs over path injects (NRCRL mid52 shared JAIROFAL LBA;
METEOFIX/METEOSKY clobbered).

## Fix

1. Builder addonApplyRank: movies=10, single-disc-on-csr=20.
2. v0.1.24 layer vs CSR+movies baseline; inject_one(..., force_append=True).
"""
)

fr = ROOT / "docs/findings/README.md"
rt = fr.read_text()
row = (
    "| 2026-08-13 | [path-fmv-movies-pack-clobber](2026-08-13-path-fmv-movies-pack-clobber.md) "
    "| manip-movies clobbered PARASHOT/NRCRL after SD inject |\n"
)
if "path-fmv-movies-pack-clobber" not in rt:
    lines = rt.splitlines(True)
    out = []
    ins = False
    for i, ln in enumerate(lines):
        out.append(ln)
        if (not ins) and ln.startswith("|---") and i > 0 and "Date" in lines[i - 1]:
            out.append(row)
            ins = True
    fr.write_text("".join(out))
print("docs ok")
