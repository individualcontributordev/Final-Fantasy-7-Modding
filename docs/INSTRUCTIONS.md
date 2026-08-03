# Task: No-disc-swap — continue playtest; publish next layer when ready

## Status

- Operator: D2/D3-range Set next movie + Play movie trims on D1 unblocked playtest; continuing.
- Finding: docs/findings/2026-08-04-noswap-d2d3-movie-trims-unblock.md
- Remaining list (pre-trim audit): mods/no-disc-swap/patches/field-movie-d2d3-after-disc-change.md
- Load D2 save still asks disc 2 unless save disc id is 1 / D1-origin save

## While playing

Note any new: crawl, ask-for-disc, freeze, map name, field id.

## When ready to ship next pack

1. Work bin = Ask trims + all movie Set/Play trims + SNOVA v3
2. build_clean_d1_layer.py (bump VERSION e.g. 0.1.1-dev)
3. verify_builder_config + enable + push
4. Builder rebuild + burn

## Evidence (optional)

    Still blocked anywhere:
    Next pack published:
    Notes:

Say check.
