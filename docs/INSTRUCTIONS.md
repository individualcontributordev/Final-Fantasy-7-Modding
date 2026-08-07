# Status: CSR manip vs ending overwrites (audit)

## Short answer

**Required CSR manip-movies are OK** on the ending CD image, after a small fix:

| Required manip | Status on ending v7 bin |
|----------------|-------------------------|
| CANONON in JAIROFAL | OK (high LBA, not stomped) |
| CANONON @ LBA 250450 (LOSLAKE1) | OK (re-punched after endings) |
| CANONHT2 in CAR_1209 | OK (outside ending ranges) |
| LASTMAP.BIN in JAIROFLY | OK |
| LAST4_3.BIN in GOLD7_2 | **Was stomped** by ENDING2E → **restored** |

Local bin already has LAST4_3 restored. Rebuild script now does it every time
(step 5/6).

## Collateral (stock D1 FMVs, not manip seeds)

Ending LBA layout overwrites ~20 D1 movie files under those addresses
(plate fall, rocket fail, gold/boog chunks, junon, etc.). Full list:
`docs/findings/2026-08-07-ending-overwrite-csr-manip-audit.md`

RCKTFAIL was already compromised by CANONON@250450 on the normal movies pack.

## Rebuild (optional)

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
# workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Still: mid-ENDING2E can glitch where CANONON sits; size **766340400**.
