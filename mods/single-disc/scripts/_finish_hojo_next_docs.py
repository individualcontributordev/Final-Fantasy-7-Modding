#!/usr/bin/env python3
"""INSTRUCTIONS + finding: D1-D2 OK; isolate Hojo next."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    (ROOT / "docs/INSTRUCTIONS.md").write_text(
        """# Task: Isolate disc-2 Hojo glitch (then disc-3 transition)

## Closed (success)

single-disc-on-csr-v0.1.9 — Jenova, end-of-disc-1 trims, disc1-to-disc2
transition, and break scene: working as expected.

## Open report

Disc-2 Hojo fight / post-fight is glitched. After Hojo comes the
disc-3 swap path (BLACKBGD to BLACKBGB to LAS0_1).

## What we know in bytes (v0.1.9)

Path after Hojo fight (CSR D2 / SD same for these ops):

1. CANON_2 (#741) hojyo/31: BATTLE then set GM 0x644 then MAPJUMP BLACKBGD (#105)
2. BLACKBGD dir/31: MAPJUMP BLACKBGB (#103)
3. BLACKBGB: SETBYTE disc=3, MAPJUMP LAS0_1 (#744) (DSKCG stripped on SD)

CANON_2 on SD:

- Script slots match CSR D2 (including hojyo fight/exit)
- Texts match CSR D2
- AKAO block same size but bytes differ (possible audio glitch source)
- Compressed DAT is OTHER vs pure D2 (Ask-strip era / merge residue)

Movies:

- CSR D2 has CANONHT2.MOV / CANONON.MOV as real files
- Single-disc D1 has no those filenames; manip-movies seeds CANONHT2 into a
  D1 slot (CAR_1209) and CANONON into JAIROFAL / LBA alias
- CSR+ Hojo pack removes CANONHT2 play on multi-disc CSR+; plain CSR keeps it

So glitch is likely one of: wrong/missing Hojo FMV stream, AKAO/audio mismatch,
or CSR+ Hojo D1 layer fighting single-disc (if CSR+ was on).

## What you do (isolation)

Always: hard-refresh builder; quit DuckStation fully between builds; no CE;
save-state only a field or two before Hojo / Sister Ray corridor.

### Build H1 — CSR + Single-disc only (CSR+ off)

APPLIED must have single-disc-on-csr-v0.1.9 and movies pack auto.
No csr-plus-scene-* packs.

Play to Hojo fight through post-fight toward disc-3 hub.

### Build H2 — H1 + CSR+ Hojo only

Also enable CSR+ Hojo lab trim (has disc1 layer). Prefer no other CSR+ packs.

## Evidence (paste)

```
APPLIED single-disc id:
APPLIED movies: YES/NO id:
APPLIED CSR+ Hojo: YES/NO
Build: H1 / H2 / other

Pre-Hojo corridor: OK / GLITCH / FREEZE
Hojo fight: OK / GLITCH / FREEZE
Post-Hojo field (CANON_2 after battle): OK / GLITCH / FREEZE
BLACKBGD / BLACKBGB: OK / GLITCH / ASK / FREEZE
Toward LAS0_1 / disc3: OK / GLITCH / FREEZE / OTHER

What glitch looks like (graphics / audio / wrong scene / softlock):
Load method: in-game save / save-state (field or two before)
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.

Commit example: ops: isolate single-disc Hojo glitch after D1-D2 OK
"""
    )
    print("INSTRUCTIONS ok")

    (ROOT / "docs/findings/2026-08-12-single-disc-d1d2-ok-hojo-next.md").write_text(
        """# Finding: D1 to D2 break OK on v0.1.9; Hojo / D3 path next

**Date:** 2026-08-12
**Status:** D1-D2 closed OK; Hojo open
**Stack:** CSR + single-disc-on-csr-v0.1.9

## Confirmed OK (human)

- Jenova fight
- End of disc 1 trims
- Transition to disc 2
- Break scene

## Open

Disc 2 Hojo fight glitched. After Hojo is disc 3 swap / transition.

## Byte notes

Post-Hojo path: CANON_2 to BLACKBGD (#105) to BLACKBGB (#103) to LAS0_1 (#744).

CANON_2 on SD vs CSR D2: all script slots equal, texts equal, AKAO size equal
but AKAO bytes differ; file hash OTHER. No DSKCG/ASK left in key MAPJUMP path
for hojyo/31.

CANONHT2/CANONON not present as MOVIE filenames on D1; seed/alias only via
manip-movies pack. CSR+ Hojo trim has disc1 layer and changes CANON_2 heavily.

## Next

Isolate H1 (SD only + movies) vs H2 (+ CSR+ Hojo). See docs/INSTRUCTIONS.md.
"""
    )
    print("finding ok")

    fr = ROOT / "docs/findings/README.md"
    t = fr.read_text()
    needle = "d1d2-ok-hojo-next"
    line = (
        "| 2026-08-12 | D1-D2 OK on SD 0.1.9; Hojo next | "
        "`2026-08-12-single-disc-d1d2-ok-hojo-next.md` |\n"
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
