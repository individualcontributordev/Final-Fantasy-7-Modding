#!/usr/bin/env python3
"""Docs for manip-movies v0.1.4 LBA 250450 alias restore."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    (ROOT / "docs/INSTRUCTIONS.md").write_text(
        """# Task: Retest Bugen waterfall FMV (not rocket town)

## What was wrong

LOSLAKE1 (Bugenhagen / waterfall FD path) seeks absolute ISO LBA 250450.
On CSR Disc 2 that LBA is CANONON. On stock D1 it is mid-RCKTFAIL (rocket).

manip-movies v0.1.3 fixed Form2 MOVIE_ID (id47 -> JAIROFAL=CANONON bytes) but
dropped the v0.1.1/v0.1.2 Form2 sector alias at LBA 250450. Field code that
seeks 250450 still hit rocket data.

## Fix

single-disc-csr-manip-movies-v0.1.4:
- Keeps Form2 MOVIE_ID eng size/aux (v0.1.3)
- Restores raw CANONON copy at LBA 250450 (RCKTFAIL tail clobber tradeoff)

Auto with Single-disc on CSR when CSR+ off. uiHidden.

## What you do

1. Hard-refresh builder
2. Base: CSR
3. Mods: Single-disc only (CSR+ off)
4. APPLIED must show:
   - single-disc-on-csr-v0.1.20
   - single-disc-csr-manip-movies-v0.1.4
5. Build Disc 1; quit DuckStation; no CE
6. Save-state a field or two before Cosmo / Bugenhagen waterfall FD scene
7. Confirm lake/waterfall FMV (CANONON-style), NOT rocket town

## Evidence (paste)

```
APPLIED single-disc:
APPLIED movies:
CSR+: OFF
Waterfall FMV: OK LAKE / ROCKET / OTHER
Audio: CLEAN / FLICKER / OTHER
Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
"""
    )
    print("INSTRUCTIONS ok")

    (
        ROOT / "docs/findings/2026-08-12-loslake1-lba-250450-alias-regressed.md"
    ).write_text(
        """# Finding: LOSLAKE1 waterfall played rocket town again (LBA 250450)

**Date:** 2026-08-12
**Status:** fixed manip-movies v0.1.4
**Stack:** CSR + single-disc-on-csr-v0.1.20 + movies (CSR+ off)

## Symptom

Bugen / Cosmo waterfall FD manip scene played rocket town FMV again
(same class as pre-v0.1.1/v0.1.2).

## Cause

LOSLAKE1 seeks ISO LBA 250450 (not only MOVIE_ID[47]).

| Disc | LBA 250450 |
|------|------------|
| CSR D2 | CANONON.MOV start (Form2) |
| Stock D1 / SD without alias | mid RCKTFAIL.MOV |

v0.1.3 inject put CANONON bytes in JAIROFAL + correct id47 MOVIE_ID, but did
not write sectors at 250450. Absolute seek still hit rocket.

## Fix

v0.1.4 = inject (Form2 MOVIE_ID) + alias_d2_seek_lba_on_d1.py (raw CANONON at
250450). RCKTFAIL tail clobbered (known tradeoff).

## Verify

sdm LBA250450 sector0 == CSR2 CANONON sector0; id47 eng Form2; JAIROFAL==CANONON.
"""
    )

    fr = ROOT / "docs/findings/README.md"
    t = fr.read_text()
    needle = "loslake1-lba-250450-alias-regressed"
    line = (
        "| 2026-08-12 | LOSLAKE1 LBA 250450 alias regressed in movies 0.1.3 | "
        "`2026-08-12-loslake1-lba-250450-alias-regressed.md` |\n"
    )
    if needle not in t:
        lines = t.splitlines(True)
        out = []
        inserted = False
        for ln in lines:
            out.append(ln)
            if (not inserted) and ln.startswith("| 2026-"):
                out.append(line)
                inserted = True
        if not inserted:
            out.append("\n" + line)
        fr.write_text("".join(out))
        print("findings README updated")

    wl = ROOT / "mods/single-disc/patches/csr-manip-movie-whitelist.md"
    t = wl.read_text()
    if "0.1.4" not in t:
        wl.write_text(
            t.rstrip()
            + """

| 2026-08-12 | Rocket instead of waterfall | v0.1.3 dropped LBA 250450 CANONON Form2 alias; v0.1.4 restores alias + keeps Form2 MOVIE_ID |
"""
        )
        print("whitelist ok")

    seed = ROOT / "mods/single-disc/patches/csr-manip-movie-seed.txt"
    st = seed.read_text()
    if "250450" not in st:
        seed.write_text(
            st.rstrip()
            + """

# After inject: also run alias_d2_seek_lba_on_d1.py so ISO LBA 250450 is
# CANONON Form2 sectors (LOSLAKE1 absolute seek). MOVIE_ID[47] alone is not enough.
"""
        )
        print("seed note ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
