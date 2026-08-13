# Full FIELD script extract: CSR D1 / D2 vs single-disc stack

**Date:** 2026-08-13
**Status:** complete (working tree dumps under workspace/)

## Method

1. List every FIELD/*.DAT on CSR D1 ISO (787 maps).
2. Decode all entity scripts to opcode streams (offsets, IF fail targets, MAPJUMP/MUSIC/etc).
3. Same for CSR D2 and SD stack: movies 0.1.4 + core 0.1.33 + path 0.1.26 + v0.1.35.
4. File-level SHA compare, then script-level op diffs where SD matches neither disc.

Artifacts (local, large JSON — not committed):

- workspace/field-script-compare-2026-08-13/csr-d1-scripts.json
- workspace/field-script-compare-2026-08-13/csr-d2-scripts.json
- workspace/field-script-compare-2026-08-13/sd-scripts.json
- workspace/field-script-compare-2026-08-13/COMPARE.md (about 456 KB)
- workspace/field-script-compare-2026-08-13/summary.json
- Re-run: python3 workspace/tmp_v035/compare_all_field_scripts.py

## Headline counts

| Bucket | Count |
|--------|------:|
| FIELD maps compared | 787 |
| SD byte-identical to D1 (or D1==D2) | 697 |
| SD byte-identical to D2 only | 34 |
| SD matches neither D1 nor D2 | 56 |
| CSR D1 != D2 collisions | 235 |

## D1 to D2 gate fields

### LOSIN2

Not in the 56: SD == CSR D1 (pure). No BITON pack. Prefer d1 is correct.

### LOST2

SD matches neither. Body is CSR D2 + one init IFUB fail E change (v0.1.35: E 0x1c to 0x24). Prefer d2 with intentional 1-byte patch.

### BLACKBGB

SD matches neither. Prefer d1 base with DSKCG removal:

| CSR D1 | SD |
|--------|-----|
| DSKCG count 4 | DSKCG count 0 |
| MAPJUMP #634 then MUSIC id=3 (both disc-2 arms) | same order (MUSIC still after MAPJUMP) |
| ASK save arms | ASK still present |

Multi-disc hub. Single-disc correctly removes disc change. MUSIC after MAPJUMP never runs on the hub for CSR multi either; next field is supposed to start BGM.

### COS_BTM2

SD matches neither pure D1 nor pure D2 (D2-class body with remaining stack deltas). Not the live landing field when the player stays on #634.

### BLUE_2

SD is D2-class path/movie install. CSR D1 dir/0 has SETWORD a455 + MAPJUMP #526; SD removes that arm and keeps MAPJUMP #632 only. Multi-disc a455 writer on D1 is not the same as SD BLUE_2.

## Prefer list vs collisions

Among D1!=D2 collisions, SD NEITHER (patched) includes BLACKBGB, LOST2, CANON_2, COS_BTM2, many FSHIP/path/movie maps — expected for path engine + ask strip. No LOSIN2 prefer mismatch.

## Does this show wrong ops / wrong place?

1. Not random disc-wide corruption: 697/787 match D1; D2-only picks look intentional.
2. D1 to 2 hubs are the known fields: LOSIN2 (pure D1), BLACKBGB (D1 minus DSKCG), LOST2 (D2 + 1 byte) — not a mistaken pristine swap.
3. v0.1.35 only changes LOST2 IFUB fail (confirmed in op dump vs D2). Playtest still silent => not wrong field file; music still not audible via that path alone; BLACKBGB still leaves MUSIC after MAPJUMP as CSR does.
4. BLUE_2 on SD no longer carries CSR D1 a455 to COS — if anything relied on that writer, multi-disc reference is that field.

## Use next

When shipping the next pack, diff only the 56 PATCHED fields (or re-run the compare script) before inventing more COS/LOSIN2 theory patches.
