# Task: Retest Bugen waterfall FMV (not rocket town)

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

Commit example: ops: retest disc1-disc2 break after single-disc 0.1.7


warning in console for builder

builder.js:468 showSaveFilePicker failed, using blob download SecurityError: Failed to execute 'showSaveFilePicker' on 'Window': Must be handling a user gesture to show a file picker.
    at saveZipDownload (builder.js:450:32)
    at applySelection (builder.js:1887:23)
