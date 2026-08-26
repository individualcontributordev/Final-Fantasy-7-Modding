# Finding: JUNAIR (field 384) freezes returning from battle on single-disc-on-csr — encounter/SCENE.BIN hypothesis disproven

**Date:** 2026-08-26
**Status:** root cause narrowed, not yet fixed
**Stack:** CSR + Single-disc only (core build, no movie-relocation layer) — reproduces identically with and without movie-relocation, so unrelated to that patch.

## Symptom

At JUNAIR (field id 384, game moment 1016, CSR D2 content), field loads fine.
Triggering a random encounter, finishing the battle, and returning to the
field freezes the game. Confirmed on both `bisect_core_no_relocation.bin`
and `playtest_movie_relocation.bin` (patched). Does **not** freeze on stock
CSR Disc 2 alone.

## Disproven hypothesis (false lead)

Original theory: single-disc merges CSR D2's JUNAIR.DAT wholesale onto a D1
base, but the build only ships D1's `BATTLE/SCENE.BIN`, so JUNAIR's D2
encounter table might reference scene indices invalid on D1.

**Disproved by direct comparison:**
- `FIELD/JUNAIR.DAT` encounter section (48 bytes) is **byte-identical**
  between CSR D1 and CSR D2.
- `BATTLE/SCENE.BIN` is **byte-identical** (270,336 bytes) between CSR D1
  and CSR D2.

So there is no encounter-table/scene-index mismatch for JUNAIR at all — the
D1 and D2 copies of this field have identical battle configuration.

## What actually differs between D1 and D2 JUNAIR.DAT

Full script-slot diff (736 script slots compared): only **one** slot differs,
`('air0', 3)`:

- **D1** (19 bytes): `IFSW(cond=0x0b) → MAPJUMP(60810111f1f6fb410000) → RET`
- **D2** (57 bytes): `IFSW(cond=0x31) → AKAO(f2 00 00 00 c1 78 00 00 00 00 00 00 00 00) → PRTYE(cafefefe) → PRTYE(ca02fefe) → MMBLK(ce02) → BITON(8210e206) → MAPJUMP(609201b0002500010080) → MAPJUMP(60810111f1f6fb410000, same tail as D1) → RET`

`merge_safe_fields.py` classifies JUNAIR as "CSR only edited D2" (D1 copy is
untouched pristine-equivalent for this slot) and takes CSR D2's file
wholesale — this is exactly per its documented behavior, not a bug in the
merge script itself.

Per `docs/findings/2026-08-24-akao-opcode-0xf2-is-canonon-cd-call-site.md`,
opcode `0xF2` (`AKAO`) issues a **raw CD-XA command with parameters
compiled as literal constants in the field's own script bytes** (cmd code,
sector/size fields) — it does **not** go through `MOVIE_ID.BIN`, so the
prior movie-relocation fix cannot affect this at all (consistent with the
freeze being identical with/without that patch).

## `air0`/slot-3 hypothesis: DISPROVEN (2026-08-26 update)

Playtester confirmed this `air0` slot-3 block is gated by a **line trigger**
(walk-into-line script call) that is not being hit in the reproduction —
the freeze happens right after a battle, well before that trigger point in
the field. So this branch cannot be the cause regardless of the `IFSW`
flag state.

This also means **no genuine JUNAIR.DAT content difference explains the
freeze**: a full script-slot diff (736 slots) plus section-by-section diff
confirms `air0`/slot-3 (unreachable here) is the *only* content delta —
`walkmesh`, `background`, `camera`, `inf`, `encounter`, and `model_loader`
sections are all byte-identical D1 vs D2, and all 735 other script slots
match exactly. Text section differs by only 2 bytes total (padding), no
script logic difference.

**Conclusion: the cause is not inside `FIELD/JUNAIR.DAT` at all.** It must
be something else in the battle-return path: engine/global state, a
different shared file (battle module common code, VRAM/module data,
audio/CD-DA track layout affected by the single-disc merge), or something
disc-layout-dependent that isn't visible in this field's own file content.

## Next steps

1. RAM-watch the script interpreter PC / call stack (DuckStation debugger)
   at the exact freeze moment. Since it's not `air0`, check whether PC is
   inside generic battle-end/field-reinit engine code (not the field
   script interpreter at all) vs. some other field entity's script that
   *is* reachable at this point (re-review scripts for `dir`/other
   entities executed on field re-entry, not just the diffed slot).
2. Since JUNAIR.DAT content is now ruled out, broaden the search: compare
   other files touched by battle-return (e.g. shared battle/field common
   modules, CD-DA/audio track table, `MOVIE_ID.BIN` if it's read at
   battle-end for any reason) between stock CSR D2 alone and the
   single-disc merged image, since the freeze is present on single-disc
   but not on stock D2.
3. Consider whether single-disc strips or renumbers CD audio tracks (CD-DA
   redbook tracks) present on D2 but not carried into the merged D1-based
   image — a battle-end music/SFX cue trying to read a track that no
   longer exists in the same position could hang the CD-XA subsystem
   similarly to the (ruled-out) AKAO literal-sector theory, just from a
   different call site than JUNAIR's field script.

## False leads (for future readers)

- Encounter table mismatch: **disproved**, tables identical byte-for-byte.
- SCENE.BIN D1 vs D2 mismatch: **disproved**, files identical byte-for-byte.
- Movie-relocation patch (`ship_movie_relocation_v010.py`): **ruled out** —
  freeze reproduces identically on the core build without that layer
  applied at all.
- `air0`/slot-3 `AKAO(0xF2)` script delta: **disproved** — this block is
  gated by a line trigger not hit before the freeze occurs, and no other
  JUNAIR.DAT content differs between D1 and D2. The freeze source is
  outside this file entirely.
