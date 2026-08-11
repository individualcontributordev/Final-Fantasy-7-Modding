# Finding: Single-disc Cosmo / Bugenhagen glitch (field 642 WHITE1)

**Date:** 2026-08-11
**Status:** fix shipped in single-disc-on-csr-v0.1.3
**Report:** CSR + CSR+ + Single-disc Disc 1 — start OK; D2 Bugenhagen waterfall + field **642** glitching.

## Map IDs

| ID | Stem | Role |
|----|------|------|
| 637–639 | loslake1–3 | Bugenhagen Cosmo lake / waterfall |
| **642** | **white1** | Cosmo white-room field |
| 643 | white2 | Adjacent |

## Root cause

Single-disc-on-csr v0.1.2 merged many CSR **D2** FIELD `.DAT` scripts onto D1, but
some movie-trim passes left **hybrid** scripts that match **neither** pure CSR D1
nor pure CSR D2:

- `WHITE2.DAT` — size 9401 like D2, **bytes ≠ D2 and ≠ D1**
- `LOSLAKE3.DAT` — same size as D1/D2, **bytes ≠ either**
- `LOSIN2.DAT` — SD had non-D2 bytes

`WHITE1.DAT` was pure D2 (OK) but sits next to broken WHITE2 / lake maps — glitching
in that corridor fits bad script/movie pairing more than CSR+ disc1 packs.

CSR+ COTA correctly replaces `LOSLAKE1` with D2 CSR+ bytes; it does not fix WHITE*.

## Fix (v0.1.3)

Overwrite Cosmo corridor fields from **pure CSR Disc 2**:

WHITE1/2/IN, HEKIGA, BLUE_1/2, LOSLAKE1–3, LOST1–3, LOSIN1–3, LOSINN
(+ matching MIM/BSX when needed; DAT was the hybrid problem).

Shipped as `single-disc-on-csr-v0.1.3` (0.1.2 disabled). Auto-include movies/endings
point at 0.1.3.
