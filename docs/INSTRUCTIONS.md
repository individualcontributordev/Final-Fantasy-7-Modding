# INSTRUCTIONS — Single-disc D1 to D2 forest music (badge v0.1.35)

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
