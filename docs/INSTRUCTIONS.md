# Task: No-disc-swap — FIELD movie trims (crawl / missing FMV)

## Context

Missing multi-disc movies can: blank FMV, Bugenhagen stare, or **field crawl**.
You are already deleting Set next movie + Play movie where found (incl. final descent BG).

## Auto inventory (this machine)

mods/no-disc-swap/patches/field-movie-inventory-d1.md

**Start with Tier 1** (D1 movie id points at BIN/LZS/NULL/STAFF/etc.):

- LOSLAKE3.DAT — 58=OPENING.BIN (known)
- LAS3_1.DAT — NULL1MIN.DAT
- LAS4_0.DAT — FSHIP2N.BIN
- Several STAFF/FSHIP/OPENING-class hits — confirm in Makou
- CHANGE*/DISK* hits may be UI false friends — verify before delete

Tier 2 OOB ids: use only after Makou Find All confirms Play movie.

## Edit rule

1. Makou Find All: Play movie / Set next movie
2. Delete Set + Play for bad scenes
3. Keep Wait, Execute script, Jump, bits
4. DS smoke the scene
5. When batch done: rebuild layer + push pack

    python3 mods/no-disc-swap/scripts/build_clean_d1_layer.py \
      --work workspace/iso-extract/ff7_d1_noswap_work.bin \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin

## Evidence

    Tier1 maps trimmed (list):
    Final descent: done/pending
    Crawl sites: done/pending
    Layer rebuild: yes/no
    Notes:

Say check.
