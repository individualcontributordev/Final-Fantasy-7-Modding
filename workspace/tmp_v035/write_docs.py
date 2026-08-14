#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

finding = ROOT / "docs/findings/2026-08-13-v034-fail-v035-lost2-music.md"
finding.write_text(
    """# v0.1.34 FAIL / v0.1.35 LOST2 music unmute

**Date:** 2026-08-13
**Status:** v0.1.34 retired; v0.1.35 ships

## Playtest (v0.1.34)

APPLIED included movies 0.1.4 + core 0.1.33 + path 0.1.26 + break 0.1.34.
D1 to D2: landed field #634 LOST2, no music, no break scene.

## LOST2 identity

SD stack LOST2 == CSR Disc 2 (hash 69a15e2493a4490f, 17090 B), not pristine/original and not CSR D1.
CSR D2 has slightly longer party talk than D1 — can feel untrimmed while still being D2.

## Why silent forest

CSR D2 LOST2 init/0 with GM = 0xa455 and bank3/0x84 bit4 OFF:

    IFUB bit4 ON  -> fail -> IFUW GM != a455 -> fail -> RET   # no MUSIC

Any other GM still plays MUSIC then RET. Playtest matches a455 + bit4 clear.

## Why v0.1.34 failed

Patched LOSIN2 BITOFF to BITON at init offset 0x49 (with SETWORD a455 nearby).
That block sits after the first RET in the Main script body. Playtest showed it did not change LOST2 entry flags.

Also: pure CSR COS_BTM2 with GM=a455 never reaches break ASK (exits on GM >= 0x202).
Forcing COS was already a black-screen path (v0.1.6-0.1.8). Multi-disc D1 to D2 ceremony is
largely BLACKBGB (end-of-disc / save / DSKCG) then LOST2 forest — not guaranteed COS ASK.

## v0.1.35 fix (minimal, reachable)

One compressed-literal byte in CSR D2 LOST2:

| Op | Before | After |
|----|--------|-------|
| IFUB bank3/0x84 bit4 ON, fail E | 0x1c -> fail at 0x23 (IFUW/silent) | 0x24 -> fail at 0x2b (AKAO2 + MUSIC 1 + RET) |

- Lives before any RET in init — real load-time path.
- Does not MAPJUMP #526 when bit4 is off (avoids COS force black path).
- Bit4 ON still follows CSR break MAPJUMP #526.
- LOSIN2 stays CSR BITOFF; no 0.1.34.

Sim: a455 + bit4OFF -> AKAO2, MUSIC 1, RET.

## Stack

movies 0.1.4 -> core v0.1.33 (badge 0.1.35) -> path 0.1.26 -> v0.1.35 (auto).
v0.1.34 disabled.

## Follow-up if music OK but break still missing

Define break as BLACKBGB end-of-disc MESSAGE/save vs Cosmo candle. Audit BLACKBGB Ask-strip
only after music path confirmed.
"""
)
print("wrote", finding)

idx = ROOT / "docs/findings/README.md"
if idx.is_file():
    t = idx.read_text()
    line = (
        "| 2026-08-13 | [v034-fail-v035-lost2-music](2026-08-13-v034-fail-v035-lost2-music.md) "
        "| v0.1.34 dead LOSIN2 BITON; v0.1.35 LOST2 MUSIC unmute (IFUB E) |\n"
    )
    if "v034-fail-v035" not in t:
        lines = t.splitlines(True)
        out = []
        done = False
        for l in lines:
            out.append(l)
            if (not done) and l.startswith("| 2026-"):
                out.append(line)
                done = True
        if not done:
            out.append("\n" + line)
        idx.write_text("".join(out))
        print("README updated")
    else:
        print("README already")

cl = ROOT / "mods/single-disc/CHANGELOG.md"
if cl.is_file():
    t = cl.read_text()
    block = """## 0.1.35 — 2026-08-13

- **FAIL retire v0.1.34** (LOSIN2 BITON / COS open — no music, no break in playtest).
- **v0.1.35** auto delta: LOST2 CSR D2 init — when bank3/0x84 bit4 is OFF, fail IFUB into
  **AKAO2 + MUSIC** instead of silent RET (1-byte E 0x1c to 0x24). No COS force.
- Badge / core id still single-disc-on-csr-v0.1.33 with version **0.1.35**.

"""
    if "0.1.35" not in t[:800]:
        lines = t.splitlines(True)
        if lines and lines[0].startswith("#"):
            cl.write_text(lines[0] + "\n" + block + "".join(lines[1:]))
        else:
            cl.write_text(block + t)
        print("changelog ok")
    else:
        print("changelog already")

vf = ROOT / "mods/single-disc/VERSION"
if vf.is_file():
    vf.write_text("0.1.35\n")
    print("VERSION", vf.read_text().strip())

(ROOT / "docs/INSTRUCTIONS.md").write_text(
    """# INSTRUCTIONS — Single-disc D1 to D2 forest music (badge v0.1.35)

## What changed

v0.1.34 is **retired** (playtest: still silent #634, no break).
New auto pack **v0.1.35** retargets LOST2 so GM a455 + bit4 OFF plays **forest music** instead of silent RET.
Does **not** force COS_BTM2 (that black-screened before).

## Build (COPY-PASTE)

1. Hard-refresh builder (badge **v0.1.35** only — not 0.1.34).
2. Base **CSR v0.14.1**, CSR+ off.
3. Enable **Single-disc** only (endings auto OK).
4. APPLIED must include:
   - CSR manip movies v0.1.4
   - Single-disc v0.1.35 (single-disc-on-csr-v0.1.33)
   - (auto) path FMVs v0.1.26
   - (auto) **disc1 to 2 forest music v0.1.35** (single-disc-on-csr-v0.1.35)
   - **Must NOT** list single-disc-on-csr-v0.1.34
5. Download new Disc 1 zip / .bin+.cue.

## Playtest focus

D1 to D2 transition (LOSIN2 party -> BLACKBGB hub -> LOST2 #634):

| Check | PASS | FAIL |
|-------|------|------|
| Land #634 forest | yes | wrong field |
| **Forest music** | audible on entry | still silent |
| Black screen / softlock | no | yes |
| COS_BTM2 force (optional) | not required this pack | if black + wrong field, note it |

Also note whether BLACKBGB still shows **End of Disc** text / save ASK before forest.

## Evidence to paste back

1. Full **APPLIED.txt**
2. One line: music PASS/FAIL, break/end-of-disc PASS/FAIL/skip, any black screen Y/N

## Do not

- Re-enable v0.1.34
- Expect Cosmo candle / COS ASK from 0.1.35 alone (music only this ship)
"""
)
print("INSTRUCTIONS ok")
