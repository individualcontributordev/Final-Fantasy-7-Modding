# Task: CSR single-disc — playtest music + break scene (updated packs)

## Already done for you (published)

Updated packs on git main:

| Pack | What changed |
|------|----------------|
| single-disc-on-csr-v0.1.1 | blackbgb: Ask for disc turned into a no-op jump so Play music still runs; lost2 on Disc 1 is now CSR Disc 2 lost2 (5-min break scene) |
| single-disc-csr-manip-movies-v0.1.0 | Same four videos as before (rebuilt on new core) |

Verify: PASS for CSR + both packs.

Local playtest image (gitignored):

    workspace/iso-extract/ff7_d1_csr_single_disc_playtest_work.bin

Same content as builder stack after Pages updates.

---

## What you do now

1. git pull
2. New builder zip: CSR v0.14.1 + Single-disc on CSR + movie seed (no CSR+)
   or open the local playtest .bin above in DuckStation
3. Check:
   - Path that used to ask for a disc: music plays, no insert-disc prompt
   - After Jenova Life / into lost2: break scene (5 min or continue)
4. Say check with notes

---

## Did we copy all CSR Disc 2 and Disc 3 onto Disc 1?

No.

| What | On Disc 1 single-disc? |
|------|-------------------------|
| CSR Disc 1 field/script changes | Yes (CSR base pack) |
| Supernova files from Disc 3 | Yes (core pack) |
| A few multi-disc videos (seed list) | Yes (movie pack) |
| lost2 break scene from CSR Disc 2 | Yes (just added in core) |
| Every CSR change that only exists on Disc 2 or Disc 3 maps | No — many map files differ per disc; we did not merge all of D2/D3 CSR into D1 |

CSR ships three disc images. Single-disc D1 starts from CSR Disc 1, then we add only what single-disc needs (no disc ask, no freezes, Supernova, break scene, seed videos). Other D2/D3-only CSR tweaks still live on those discs for multi-disc play.

If something on late Disc 2/3 CSR feels wrong on single-disc, say which map — we can copy that file the same way as lost2.

---

## Technical notes (optional)

- blackbgb: one Ask for disc 3 at byte 432 replaced with forward jump +0 so the next op (Play music) still runs. File size unchanged.
- lost2: CSR D2 file is 17090 bytes; D1 slot grew from 17007 (same sector count).

---

## Notes for check

    New zip or local bin:
    Music on hub path:
    Break scene on lost2:
    Ask for disc:
    Other problems:
