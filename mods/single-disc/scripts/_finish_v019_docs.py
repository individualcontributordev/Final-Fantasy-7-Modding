#!/usr/bin/env python3
"""CHANGELOG / finding / INSTRUCTIONS / prefer list for single-disc v0.1.9."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    cl = ROOT / "mods/single-disc/CHANGELOG.md"
    old = cl.read_text()
    rest = old.find("## 0.1.8")
    if rest < 0:
        raise SystemExit("0.1.8 missing")
    top = """# Single-disc changelog

Newest at top.

## 0.1.9 (LOSIN2 end-of-D1 must stay CSR D1)

- Field #632 LOSIN2 is end of disc 1 (before BLACKBGB disc-2 ask/break hub).
- Blind D2 FIELD merge put CSR Disc 2 LOSIN2 on the one-disc image.
- CSR D1 LOSIN2 init sets GameMoment 0xa455 (break sentinel) then party goes to
  BLACKBGB. CSR D2 LOSIN2 never writes 0xa455 — so LOST2/COS_BTM2 break gates
  never open (black + regular D2 music).
- Restore CSR D1 LOSIN2. Keep CSR D2 LOST2 + COS_BTM2 (0.1.8) and BLACKBGB
  Ask/DSKCG strips.
- Prefer list: LOSIN2.DAT d1 (do not overwrite with D2 on future merges).
- Builder: single-disc-on-csr-v0.1.9 enabled; 0.1.8 and older main packs off.

"""
    cl.write_text(top + old[rest:])
    print("CHANGELOG ok")

    prefer = ROOT / "mods/single-disc/patches/csr-field-disc-prefer.txt"
    t = prefer.read_text()
    if "LOSIN2.DAT" not in t:
        # insert after LOST2 line
        needle = "LOST2.DAT d2"
        i = t.find(needle)
        if i < 0:
            raise SystemExit("LOST2 prefer missing")
        # find end of that line
        j = t.find("\n", i)
        line = (
            "\nLOSIN2.DAT d1      # #632 end-of-D1: CSR D1 sets GM 0xa455 for break; "
            "D2 LOST2/COS gates need it\n"
        )
        prefer.write_text(t[: j + 1] + line + t[j + 1 :])
        print("prefer list ok")
    else:
        # ensure d1
        lines = []
        for ln in t.splitlines(True):
            if ln.strip().startswith("LOSIN2.DAT"):
                lines.append(
                    "LOSIN2.DAT d1      # #632 end-of-D1: CSR D1 sets GM 0xa455 "
                    "for break; D2 LOST2/COS gates need it\n"
                )
            else:
                lines.append(ln)
        prefer.write_text("".join(lines))
        print("prefer list updated")

    (ROOT / "docs/findings/2026-08-11-single-disc-losin2-must-be-csr-d1.md").write_text(
        """# Finding: LOSIN2 (#632) must stay CSR D1 on single-disc

**Date:** 2026-08-11
**Status:** fixed in single-disc-on-csr-v0.1.9
**Report:** field 632 using disc 2; no break; black + regular disc 2 music

## Role of LOSIN2

Makou id 632 = losin2 = end of CSR disc 1 path, immediately before BLACKBGB
(#103) disc-change / break hub.

## Multi-disc CSR chain (working)

1. LOSIN2 (CSR D1) init when GM==0x2a2:
   - SETWORD GameMoment = 0x2a5
   - SETWORD GameMoment = 0xa455   ← break sentinel
2. cloud/3 MAPJUMP BLACKBGB
3. BLACKBGB: SETBYTE disc=2, DSKCG 2, MAPJUMP LOST2
4. LOST2 (CSR D2) / COS_BTM2: IFUW GM==0xa455 opens break choreography

## Single-disc bug

D2 FIELD merge replaced LOSIN2 with CSR Disc 2 bytes. D2 LOSIN2:

- Does not write 0xa455
- Still MAPJUMPs BLACKBGB with music

BLACKBGB (Ask-stripped) still jumps LOST2, but LOST2 and COS_BTM2 gates on
0xa455 stay false → skip break → black + D2-style music.

Confirmed hashes (v0.1.8):

| File | CSR D1 | CSR D2 | SD 0.1.8 |
|------|--------|--------|----------|
| LOSIN2 | A | B | B (wrong) |
| LOST2 | D1 variant | D2 | D2 (wanted for open) |
| COS_BTM2 | … | D2 | D2 |

## Fix

Restore CSR D1 LOSIN2 on the single-disc image. Keep D2 LOST2 + COS_BTM2.
Prefer list: LOSIN2.DAT d1 so future merges do not re-clobber.

## Rule

End-of-D1 maps that arm break/disc-transition state must prefer CSR D1.
Do not blindly install D2 for every field id >= 632.
"""
    )
    print("finding ok")

    (ROOT / "docs/INSTRUCTIONS.md").write_text(
        """# Task: Retest disc1-to-disc2 break on single-disc-on-csr v0.1.9

## What was wrong

Field #632 LOSIN2 is end of disc 1 (before the disc-2 ask / BLACKBGB hub).
Single-disc had installed CSR Disc 2 LOSIN2 there. Only CSR Disc 1 LOSIN2
sets GameMoment 0xa455, which opens the LOST2/COS_BTM2 break scene.

Without that: black screen + regular disc 2 music, no break.

## Fix

single-disc-on-csr-v0.1.9 restores CSR D1 LOSIN2.
Keeps CSR D2 LOST2 + COS_BTM2 and BLACKBGB without DSKCG.

## What you do

1. Hard-refresh the builder
2. Base: CSR
3. Mods: Single-disc only (CSR+ off)
4. Confirm APPLIED has single-disc-on-csr-v0.1.9
5. Build Disc 1
6. Quit DuckStation fully; no CE
7. Load in-game save or save-state a field or two before LOSIN2 / transition
8. Run end of disc 1 through break

Expect:
- LOSIN2 behaves like multi-disc CSR disc 1 end (not D2 forest open)
- Break scene/menu like multi-disc CSR after disc 2 swap
- Not black-only with only disc 2 music

Save-states OK only if taken a field or two before the scene under test.

## Evidence (paste)

```
APPLIED single-disc id:
movies pack auto?: YES/NO
LOSIN2 feel: D1 end / D2 open / OTHER
Disc1 to disc2: OK BREAK / BLACK+MUSIC / FREEZE / OTHER
Break scene/menu: YES / NO
Playable after: YES / NO
Load method: in-game save / save-state (field or two before)
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.

Commit example: ops: retest disc1-disc2 break after single-disc 0.1.9
"""
    )
    print("INSTRUCTIONS ok")

    fr = ROOT / "docs/findings/README.md"
    if fr.is_file():
        t = fr.read_text()
        needle = "losin2-must-be-csr-d1"
        line = (
            "| 2026-08-11 | single-disc LOSIN2 must stay CSR D1 | "
            "`2026-08-11-single-disc-losin2-must-be-csr-d1.md` |\n"
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
