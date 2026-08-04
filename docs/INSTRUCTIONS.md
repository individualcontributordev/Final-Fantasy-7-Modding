# Task: CSR single-disc — playtest full D2/D3 CSR map merge

## Done (published)

Core pack single-disc-on-csr-v0.1.1 now includes:

1. CSR Disc 1 base (as always)
2. **All CSR Disc 2 field map changes** copied onto Disc 1 (72 maps)
3. **All CSR Disc 3 field map changes** copied onto Disc 1 (5 maps)
4. CSR Disc 1 FIELD.BIN kept (not Disc 2 engine file)
5. blackbgb: no insert-disc prompt; music still runs
6. lost2: CSR Disc 2 break scene
7. Supernova + earlier single-disc freeze fixes where still present
8. Movie seed pack rebuilt on top (same 4 videos)

Not done by applying disc2/disc3 layer files onto D1 (that would corrupt offsets).
Done by copying each changed FIELD file from CSR D2/D3 onto D1.

List: mods/single-disc/patches/csr-d2d3-field-merge-on-d1.md

Verify: PASS

Local bin:

    workspace/iso-extract/ff7_d1_csr_single_disc_playtest_work.bin

---

## What you do

1. git pull
2. New builder zip: CSR + Single-disc on CSR + movie seed (no CSR+)
   or use the local bin above
3. Playtest hard: early game, disc1-to-disc2 moment, break scene, music, late maps
4. Say check with anything wrong (map name)

Note: merging D2/D3 CSR maps can put back some insert-disc or freeze scripts that Clean-style edits had removed on a few maps. Report those maps if you hit them.

---

## Notes for check

    Boot:
    Break scene:
    Music after hub:
    Ask for disc:
    Freeze/crawl (map):
    Other:
