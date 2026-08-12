#!/usr/bin/env python3
"""Docs + manifest polish for manip-movies v0.1.3."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    man = json.loads((ROOT / "builder/manifest.json").read_text())
    for a in man["addons"]:
        if a["id"].startswith("single-disc-csr-manip-movies-") and a[
            "id"
        ] != "single-disc-csr-manip-movies-v0.1.3":
            a["enabled"] = False
        if a["id"] == "single-disc-csr-manip-movies-v0.1.3":
            a["enabled"] = True
            a["hidden"] = True
            a["autoIncludeWhen"] = {
                "addonSelected": "single-disc-on-csr-v0.1.20",
                "bases": ["csr-v0.14.1"],
                "unlessAddonIdPrefix": "csr-plus-scene-",
            }
    (ROOT / "builder/manifest.json").write_text(json.dumps(man, indent=2) + "\n")

    pack_path = ROOT / "builder/single-disc-csr-manip-movies-v0.1.3/pack.json"
    pack = json.loads(pack_path.read_text())
    pack["autoIncludeWhen"] = {
        "addonSelected": "single-disc-on-csr-v0.1.20",
        "bases": ["csr-v0.14.1"],
        "unlessAddonIdPrefix": "csr-plus-scene-",
    }
    pack["hidden"] = True
    pack_path.write_text(json.dumps(pack, indent=2) + "\n")
    print("manifest/pack ok")

    wl = ROOT / "mods/single-disc/patches/csr-manip-movie-whitelist.md"
    t = wl.read_text()
    if "0.1.3" not in t:
        wl.write_text(
            t.rstrip()
            + """

| 2026-08-12 | Dual/flicker audio on manip movies | MOVIE_ID eng_size was ISO bytes + stale aux; CSR D2 uses nsec*2336 Form2 size. Pack v0.1.3 copies source Form2 eng size/aux. Residual zero optional (FF7_ZERO_MOVIE_RESIDUAL=1). |
"""
        )
        print("whitelist ok")

    (ROOT / "docs/INSTRUCTIONS.md").write_text(
        """# Task: Retest manip-movies audio after v0.1.3 (Hojo CANONHT2)

## Closed

- single-disc-on-csr-v0.1.20: CANON_2 Hojo field OK (no full glitch on load)
- D1 to D2 break OK on 0.1.9+

## Open (audio)

Manip-movies had real audio plus a flickering/extra sound. Shrink-inject wrote
correct CANONHT2 bytes into CAR_1209 but left MOVIE_ID engine size as ISO
byte length + old aux, while CSR D2 uses Form2 eng size (nsec*2336) and source
aux. Player could mis-length the stream (dual/flicker audio).

## Fix

single-disc-csr-manip-movies-v0.1.3 — Form2 MOVIE_ID eng size/aux from source
disc. Auto with Single-disc when CSR+ off.

## What you do

1. Hard-refresh builder
2. Base: CSR
3. Mods: Single-disc only (CSR+ off so movies auto-include)
4. APPLIED must show:
   - single-disc-on-csr-v0.1.20
   - single-disc-csr-manip-movies-v0.1.3
5. Build Disc 1
6. Quit DuckStation fully; no CE
7. Save-state a field or two before Hojo; enter CANON_2 / play Hojo FMV path
8. Listen: one clean track, no flicker/double audio

Also spot-check any other seeded FMV you notice if easy.

## Evidence (paste)

```
APPLIED single-disc id:
APPLIED movies id:
CSR+: OFF
Hojo field load: OK / GLITCH
Hojo FMV/audio: CLEAN / FLICKER+DOUBLE / OTHER
Other FMVs notes:
Load method: in-game save / save-state (field or two before)
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
"""
    )
    print("INSTRUCTIONS ok")

    (
        ROOT / "docs/findings/2026-08-12-manip-movies-dual-audio-movie-id.md"
    ).write_text(
        """# Finding: manip-movies dual/flicker audio — wrong MOVIE_ID eng size

**Date:** 2026-08-12
**Status:** fix shipped single-disc-csr-manip-movies-v0.1.3
**Report:** After CANON_2 OK, manip-movies sound broken: real audio + flickering extra

## Cause

Seed inject put CSR D2 CANONHT2 bytes into D1 CAR_1209.STR (payload match).
MOVIE_ID row kept:

- eng_size = ISO byte size (5240832)
- aux from old D1 CAR row

CSR D2 CANONHT2 row uses:

- eng_size = nsec * 2336 (5977824) Form2 engine length
- source aux (b/c)

Mismatch lets the player run wrong length/metadata vs residual old CAR XA in
the abandoned tail after shrink. Result: dual/flicker audio.

## Fix

inject_movies_by_disc_id.py: always patch MOVIE_ID from source Form2 meta;
if eng_size smaller than form2 estimate, force nsec*2336. Optional residual
zero via FF7_ZERO_MOVIE_RESIDUAL=1 (huge layer).

Pack: single-disc-csr-manip-movies-v0.1.3
"""
    )

    fr = ROOT / "docs/findings/README.md"
    t = fr.read_text()
    needle = "dual-audio-movie-id"
    line = (
        "| 2026-08-12 | manip-movies dual audio MOVIE_ID Form2 size | "
        "`2026-08-12-manip-movies-dual-audio-movie-id.md` |\n"
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
