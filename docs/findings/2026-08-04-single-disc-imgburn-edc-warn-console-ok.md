# Finding: ImgBurn EDC miscompare but console play OK (v0.1.1)

**Date:** 2026-08-04
**Status:** operator confirmed

## Report

Clean + single-disc-clean-v0.1.1 burn:

- ImgBurn verify: miscompare LBA 226545 offset 2072 (EDC), labeled BISKDEAD.STR
  (actually BOOGDEMO start; sector identical to pristine in offline build)
- **Console play: fine so far**

## Interpretation

Supports treating that verify failure as **optical write/read noise**, not a corrupt
pack image. Layer does not modify that LBA; offline build matched pristine there.

## Related

- field-audit-v0.1.1-vs-pristine.md
- 2026-08-03-single-disc-imgburn-verify-pass.md (earlier clean verify)
- 2026-08-03-single-disc-console-boot-pass.md
