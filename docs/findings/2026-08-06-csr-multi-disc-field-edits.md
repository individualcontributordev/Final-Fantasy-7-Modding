# CSR field maps edited on multiple discs

Generated vs csr-v0.14.1 layers on pristine NTSC-U D1/D2/D3.

A field stem is listed if CSR changes that FIELD/*.DAT on **two or more** discs
(vs pristine on that disc). Single-disc D2/D3→D1 merge can clobber CSR D1-only
trims when CSR D2/D3 has a different version of the same stem (see DEL1 #441).

## Summary

| Metric | Count |
|--------|------:|
| CSR-edited DATs D1 / D2 / D3 | 174 / 71 / 4 |
| Stems edited on 2+ discs | 10 |
| … all 3 discs | 0 |
| … D1+D2 only | 10 |
| … D1+D3 only | 0 |
| … D2+D3 only | 0 |
| Multi-disc stems with **identical** CSR bytes on every disc that edits them | 0 |
| Multi-disc stems with **different** CSR bytes per disc (**review / merge candidates**) | 10 |

## Different CSR versions (manual merge / prefer-D1 policy candidates)

These are the important ones: CSR touched the same map on multiple discs but the
resulting files are **not** byte-identical. Picking D2 or D3 wholesale can drop D1 trims.

| Field DAT | Discs CSR-edited | Sizes CSR (D1/D2/D3) | Pristine identical across those discs? |
|-----------|------------------|----------------------|----------------------------------------|
| BLACKBGB.DAT | D1,D2 | 13013 / 13013 / (13008) | yes |
| BUGIN1A.DAT | D1,D2 | 12117 / 12097 / (12092) | yes |
| COS_BTM.DAT | D1,D2 | 23141 / 23143 / (23228) | yes |
| COS_BTM2.DAT | D1,D2 | 17572 / 17558 / (17167) | yes |
| DEL1.DAT | D1,D2 | 21432 / 21456 / (21700) | yes |
| JUNAIR2.DAT | D1,D2 | 16720 / 16720 / (16729) | yes |
| LOST2.DAT | D1,D2 | 17007 / 17090 / (16974) | yes |
| NIVGATE.DAT | D1,D2 | 7378 / 7358 / (7366) | yes |
| RCKTIN2.DAT | D1,D2 | 17713 / 17709 / (17723) | yes |
| RCKTIN7.DAT | D1,D2 | 13186 / 13202 / (13199) | yes |

## Same CSR version on every disc that edits it

Lower risk for single-disc merge: any disc copy is the same CSR result.

| Field DAT | Discs | CSR size |
|-----------|-------|---------:|

## Notes

- Comparison is whole-file hash of FIELD/<stem>.DAT after applying each disc CSR layer.
- Does not classify *why* CSR differed (early/mid/late game); that needs Makou / changelog.
- DEL1.DAT is the known bad case: CSR D1 removes jump to DEL2; CSR D2 keeps a jump.
- FIELD.BIN excluded from this DAT list (engine overlay, handled separately).

## Follow-up

Prefer D1/D2 triage: 2026-08-06-csr-multi-disc-field-prefer.md
