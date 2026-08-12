#!/usr/bin/env python3
"""Write CHANGELOG / finding / INSTRUCTIONS for single-disc v0.1.8."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    cl = ROOT / "mods/single-disc/CHANGELOG.md"
    old = cl.read_text()
    rest_start = old.find("## 0.1.7")
    if rest_start < 0:
        raise SystemExit("0.1.7 missing")
    top = """# Single-disc changelog

Newest at top.

## 0.1.8 (undo LOST2 to cos_btm2 force — fix black break)

- v0.1.6/0.1.7 forced LOST2 MAPJUMP to cos_btm2 and opened COS_BTM2 IFUW gates.
  That path is NOT how multi-disc CSR runs the break. On normal disc1 to disc2,
  GameMoment is never 0xa455, so LOST2 skips the cos_btm2 jump. Forcing the jump
  lands COS_BTM2 with the wrong moment: IFSW GM >= 0x202 hits RET immediately
  (black screen + music, no break menu).
- Restore pure CSR Disc 2 LOST2 + COS_BTM2 bytes (no force).
- Keep BLACKBGB Ask/DSKCG strips + disc-id SETBYTE and all 0.1.5 field Ask strips.
- Builder: single-disc-on-csr-v0.1.8 enabled; 0.1.7/0.1.6 disabled.

"""
    cl.write_text(top + old[rest_start:])
    print("CHANGELOG ok")

    (ROOT / "docs/findings/2026-08-11-single-disc-lost2-force-caused-black-break.md").write_text(
        """# Finding: Forced LOST2 to cos_btm2 caused black break (v0.1.6/0.1.7)

**Date:** 2026-08-11
**Status:** fixed in single-disc-on-csr-v0.1.8
**Stack:** CSR + Single-disc (no CSR+) — Build C still black after 0.1.7

## Symptom

Disc1 to disc2: black screen, disc-2-ish music, no CSR break menu / scene.

CSR multi-disc (swap D2) break remains OK.

## Wrong theory (0.1.6 / 0.1.7)

Assumed break needs LOST2 IFUW 55 a4 true then MAPJUMP cos_btm2, and that
0xa455 was disc id 2. Forced:

1. LOST2 else-jump on that IFUW so always MAPJUMP cos_btm2
2. COS_BTM2 large IFUW else-jumps to 0 (v0.1.7)

## Correct opcode read

IFUW/IFSW layout (FFRTT): op | B1B2 | A u16 | V u16 | C | E

- Bank byte 0x20 = bank 2 addr 0 = GameMoment, not disc id.
- Disc id is bank 13 (SETBYTE 80 d0 00 02 on BLACKBGB).
- Value 0xa455 is a CSR sentinel GameMoment that is never written by any
  FIELD script on Disc 2 (full DAT scan). So the LOST2 to cos_btm2 MAPJUMP is
  dead on multi-disc too.

## Why force black-screens

On forced landing in COS_BTM2 with normal end-of-D1 GameMoment (>= 0x0202):

- IFSW GM >= 0x0202 goes to SETBYTE then RET (skips break block)
- IFUW GM == 0xa455 break ASK / music is never reached after RET

Music from the early MUSIC f002 / AKAO path still runs = black + music.

Multi-disc CSR instead stays on CSR D2 LOST2 after BLACKBGB (post-swap),
with DSKCG + SETBYTE disc=2. Break choreography lives in that LOST2 / D2
open path, not the forced cos_btm2 init.

## Fix (v0.1.8)

Restore byte-identical CSR Disc 2 FIELD/LOST2.DAT and FIELD/COS_BTM2.DAT
on the single-disc image. Keep BLACKBGB DSKCG stripped + disc SETBYTE and
0.1.5 Ask strips.

## Evidence checks

| Check | 0.1.7 | 0.1.8 |
|-------|-------|-------|
| LOST2 == CSR D2 | no (force) | yes |
| COS_BTM2 == CSR D2 | no (force) | yes |
| LOST2 MAPJUMP IFUW else | 0x00 | 0x0B |
| COS break IFUW else | 0x00 | 0xCF |
| BLACKBGB DSKCG | 0 | 0 |

## Follow-up if break still missing

If playtest still lacks break after 0.1.8, investigate LOST2 non-init
scripts / version entity / movies pack streams — not another cos_btm2 IFUW force.
"""
    )
    print("finding ok")

    (ROOT / "docs/INSTRUCTIONS.md").write_text(
        """# Task: Retest disc1-to-disc2 break on single-disc-on-csr v0.1.8

## What was wrong

v0.1.6/0.1.7 forced LOST2 MAPJUMP to cos_btm2 and opened COS_BTM2 gates.
That is NOT the multi-disc CSR path. Forced land on cos_btm2 with normal
GameMoment hits IFSW GM >= 0x202 then RET = black screen + music, no break.

CSR multi-disc break still OK (swap D2, stay on D2 LOST2).

## Fix

single-disc-on-csr-v0.1.8 restores pure CSR Disc 2 LOST2 + COS_BTM2
(no force). BLACKBGB still has DSKCG stripped and sets disc id 2.

## What you do

1. Hard-refresh the builder
2. Base: CSR
3. Mods: Single-disc only (CSR+ off)
4. Confirm APPLIED has single-disc-on-csr-v0.1.8
5. Build Disc 1
6. Quit DuckStation fully; no CE
7. Load in-game save or save-state a field or two before the transition
8. Run disc1-to-disc2 / break

Expect: same as multi-disc CSR break (menu/scene + music), not black-only

Save-states OK only if taken a field or two before the scene under test.

## Evidence (paste)

```
APPLIED single-disc id:
movies pack auto?: YES/NO
Disc1 to disc2: OK BREAK / BLACK+MUSIC / FREEZE / OTHER
Break scene/menu: YES / NO
Playable after: YES / NO
Load method: in-game save / save-state (field or two before)
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.

Commit example: ops: retest disc1-disc2 break after single-disc 0.1.8
"""
    )
    print("INSTRUCTIONS ok")

    fr = ROOT / "docs/findings/README.md"
    if fr.is_file():
        t = fr.read_text()
        needle = "lost2-force-caused-black"
        line = (
            "| 2026-08-11 | single-disc LOST2 force black break | "
            "`2026-08-11-single-disc-lost2-force-caused-black-break.md` |\n"
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
        else:
            print("findings README already has row")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
