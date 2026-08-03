# Task: No-disc-swap — retest builder after EDC grow fix

## Cause of error

Builder message: source and patched image sizes differ

applyLayer already supports growing the image (SNOVA +570 sectors).
EDC repair required source.length === patched.length and threw.

## Fix (site)

individualcontributordev.github.io builder/edc.js — pushed.
Repair now allows patched longer than source; regenerates EDC on changed
+ newly appended sectors.

## Your steps

1. Hard refresh builder (cache bust): https://individualcontributor.dev/builder/
   Use a private window if the old edc.js is cached.
2. Base: Unmodified / clean
3. Add-on: No-disc-swap Clean D1
4. Disc 1 → Build

Expect: zip download succeeds (no size-differ error).
APPLIED.txt may note EDC sectors repaired.

5. Burn path: image already EDC-repaired by builder; still follow
   docs/07-hardware-burn.md if your burner requires extra steps.
6. Console smoke.

## Evidence

    Builder build: PASS/FAIL
    Notes:
    Console: …

Say check.

## Notes

- Pack remains D1-only; grown size ~748.8 MB vs retail ~747.4 MB
- Do not commit .bin
