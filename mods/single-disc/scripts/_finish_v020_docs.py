#!/usr/bin/env python3
"""Docs for single-disc v0.1.20 CANON_2 AKAO restore."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    cl = ROOT / "mods/single-disc/CHANGELOG.md"
    old = cl.read_text()
    rest = old.find("## 0.1.9")
    if rest < 0:
        raise SystemExit("0.1.9 missing")
    top = """# Single-disc changelog

Newest at top.

## 0.1.20 (CANON_2 Hojo field — undo bad DSKCG strip in AKAO)

- Report: CSR + Single-disc only; CANON_2 (#741) fully glitched as soon as the
  Hojo field loads (disc-3 path not reachable).
- MIM/BSX match CSR D2. All script slots and texts match CSR D2.
- Only 14 bytes differ: inside the **AKAO** block, seven times `0e 03` became
  `10 00`. That is the old Ask/DSKCG strip pattern (NOP DSKCG disc 3) applied as
  a raw byte search, not as a real field opcode.
- CSR D2 CANON_2 has **zero** DSKCG/ASK opcodes; those `0e 03` bytes are music
  data. Corrupting them glitches the field on load.
- Restore pure CSR Disc 2 CANON_2.DAT. Prefer: CANON_2.DAT d2 (keep pure D2;
  do not raw-strip 0e0x inside AKAO).
- Keeps 0.1.9 LOSIN2 D1 + LOST2/COS_BTM2 D2 break path.
- Builder: single-disc-on-csr-v0.1.20 enabled; older main packs off.

"""
    cl.write_text(top + old[rest:])
    print("CHANGELOG ok")

    prefer = ROOT / "mods/single-disc/patches/csr-field-disc-prefer.txt"
    t = prefer.read_text()
    if "CANON_2.DAT" not in t:
        needle = "LOSIN2.DAT d1"
        i = t.find(needle)
        j = t.find("\n", i) if i >= 0 else -1
        line = (
            "\nCANON_2.DAT d2      # #741 Hojo: pure CSR D2; never raw-strip "
            "0e03 inside AKAO (v0.1.5 bug)\n"
        )
        if j >= 0:
            prefer.write_text(t[: j + 1] + line + t[j + 1 :])
        else:
            prefer.write_text(t + line)
        print("prefer ok")
    else:
        print("prefer already has CANON_2")

    (ROOT / "docs/findings/2026-08-12-single-disc-canon2-akao-dskcg-strip.md").write_text(
        """# Finding: CANON_2 glitch on load — DSKCG strip hit AKAO

**Date:** 2026-08-12
**Status:** fixed in single-disc-on-csr-v0.1.20
**Stack:** CSR + Single-disc only (CSR+ off); field glitched when CANON_2 loads

## Symptom

Hojo field (#741 CANON_2) fully glitched on load. Disc-3 transition not testable.

## Not the cause

- MIM/BSX: identical to CSR D2
- Script slots / texts: identical to CSR D2
- Movies pack: does not change CANON_2.DAT
- Real DSKCG/ASK opcodes on CSR D2 CANON_2: **none**

## Cause

v0.1.5 era residual Ask strip turned seven AKAO payloads of `0e 03` into `10 00`
(JMPF +0 style / DSKCG nop pattern) without parsing opcodes. Same compressed
size ±; 14 bytes differ, all inside AKAO.

CSR D2 AKAO contains 37x `0e 03`; SD had 30x `0e 03` + 7 corrupted pairs.

## Fix

Restore byte-identical CSR Disc 2 FIELD/CANON_2.DAT on the single-disc image.

## Lesson

Never bulk-replace 0x0E / 0x0E0x patterns in full decompressed FIELD blobs.
Only patch confirmed DSKCG/ASK ops from the script decoder.
"""
    )
    print("finding ok")

    (ROOT / "docs/INSTRUCTIONS.md").write_text(
        """# Task: Retest Hojo field (CANON_2) on single-disc-on-csr v0.1.20

## Closed earlier

v0.1.9: Jenova, end disc 1 trims, disc1-to-disc2, break scene OK.

## What was wrong on Hojo

CANON_2 (#741) glitched as soon as the field loaded (CSR + Single-disc, no CSR+).
v0.1.5 raw DSKCG strip rewrote `0e 03` bytes inside **AKAO music data** (not real
disc-change ops). CSR D2 CANON_2 has zero DSKCG/ASK opcodes.

## Fix

single-disc-on-csr-v0.1.20 restores pure CSR Disc 2 CANON_2.DAT.

## What you do

1. Hard-refresh the builder
2. Base: CSR
3. Mods: Single-disc only (CSR+ off)
4. Confirm APPLIED has single-disc-on-csr-v0.1.20
5. Build Disc 1
6. Quit DuckStation fully; no CE
7. Load save-state a field or two before Hojo (e.g. BLIN66_6 / FSHIP_24), play in
8. Check CANON_2 on load, fight, post-fight toward BLACKBGD / disc3 if possible

Expect: Hojo field looks like multi-disc CSR (not fully glitched on entry).

## Evidence (paste)

```
APPLIED single-disc id:
movies pack auto?: YES/NO
CSR+: OFF
CANON_2 on load: OK / GLITCH / FREEZE
Hojo fight: OK / GLITCH / FREEZE / NOT REACHED
Post-Hojo / BLACKBGD: OK / GLITCH / FREEZE / NOT REACHED
Toward disc3 / LAS0_1: OK / GLITCH / FREEZE / NOT REACHED
Load method: in-game save / save-state (field or two before)
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.

Commit example: ops: retest Hojo CANON_2 after single-disc 0.1.20
"""
    )
    print("INSTRUCTIONS ok")

    fr = ROOT / "docs/findings/README.md"
    t = fr.read_text()
    needle = "canon2-akao-dskcg-strip"
    line = (
        "| 2026-08-12 | CANON_2 AKAO corrupted by DSKCG strip | "
        "`2026-08-12-single-disc-canon2-akao-dskcg-strip.md` |\n"
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
