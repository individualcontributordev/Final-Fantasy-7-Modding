# D1 movie ops fid<=631: applied 0.1.0 vs pristine

Question: did we accidentally delete Set next movie / Play movie on early/mid D1 maps?

Compare: pristine D1 vs no-disc-swap-clean-v0.1.0-dev applied.
Filter: field id **<= 631** (up to and including maps before losin2 #632).

Method: LZS script section, PMVIE(0xF8)+MOVIE(0xF9) within 48 bytes.
Classify pristine D1 movie target: stream OK vs nonstream/meta/OOB.

## Summary

| Category | Count |
|----------|------:|
| Field DATs fid<=631 with any byte change | 2 |
| All PMVIE+MOVIE pairs removed | 1 |
| Pair multiset changed (partial) | 0 |
| Pairs unchanged (still present) | 71 |

## All pairs removed (fid<=631)

These had PMVIE+MOVIE on pristine and **none** on applied — your Makou deletes.

| ID | DAT | Stem | Pristine targets | Likely OK to remove? |
|---:|-----|------|------------------|----------------------|
| 143 | ROOTMAP.DAT | rootmap | 24=FSHIP2.BIN [nonstrm] x1 | YES — nonstream/OOB on D1 (crawl/placeholder class) |

## Partial pair changes (fid<=631)

(none)

## Possible mistaken deletes (pure D1 stream targets removed)

**None detected** by this heuristic.

## Mixed removals (review)

(none)

## Safe-class removals (nonstream/OOB only)

Count: 1

- 143 ROOTMAP.DAT: 24=FSHIP2.BIN [nonstrm] x1

## Unchanged maps that still have movie pairs (fid<=631)

Count: 71 — still playing something on D1 (good if intentional leave).

With at least one stream target still present: 37 maps

## Byte-changed DAT list fid<=631 (includes Ask trims, movie trims, etc.)

Count: 2

- 106 BLACKBGE.DAT — pairs-same
- 143 ROOTMAP.DAT — pairs-removed

## Notes

- Heuristic is not perfect: a stream on D1 can still be the WRONG multi-disc clip.
- Removing a pure D1 stream (e.g. ONTRAIN, OPENING movie, Gold Saucer) is higher regret.
- blackbg* hubs often mix bike/story/movie; check blackbgb carefully.
- Re-run after next layer publish.
## Bottom line

On applied 0.1.0-dev, for field id <= 631:

- No mistaken pure-stream movie deletes detected
- Only movie pair fully removed: ROOTMAP.DAT (id 143) — pristine target FSHIP2.BIN (nonstream / safe class)
- Other FIELD byte changes in this id range are not mass early-game FMV removal
- D1-native Set/Play for disc-1 story (ids 0-631) appear left intact aside from rootmap

## All FIELD DAT byte changes fid<=631 on applied 0.1.0

- 95 BLACKBG3.DAT (size delta -2)
- 103 BLACKBGB.DAT (size delta +1)
- 106 BLACKBGE.DAT (size delta -2)
- 143 ROOTMAP.DAT (size delta -3)

