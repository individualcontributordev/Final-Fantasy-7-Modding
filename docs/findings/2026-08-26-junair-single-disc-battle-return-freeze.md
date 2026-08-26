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

## Caveat — relevance to the battle-return freeze not yet confirmed

This `air0`/slot-3 branch is gated by an `IFSW` flag check (different flag
condition per disc: `0x0b` on D1 vs `0x31` on D2), so it's a **conditional**
branch, not something guaranteed to run every time the field loads or every
time a battle ends. It has not yet been confirmed that:

1. This slot is actually invoked during the battle-return / field-reinit
   sequence (as opposed to some unrelated story trigger), or
2. The `IFSW` condition is actually true at game moment 1016 in the
   single-disc build's flag state.

It remains the single most likely candidate (only genuine script content
delta between the D1 and D2 copies of this field, and the `AKAO(0xF2)`
literal CD-command bytes are a known freeze-prone construct per the linked
finding), but is unconfirmed.

## Next steps

1. RAM-watch the script interpreter PC (or use DuckStation's debugger) at
   the exact freeze moment to confirm execution is inside this `air0`
   entity's script (specifically the `AKAO` instruction) vs. elsewhere
   (e.g. a shared field-init/re-entry script this diff doesn't cover).
2. If confirmed: this `AKAO` instruction's literal bytes
   (`c1 78 00000000 00000000 00000000`) were compiled assuming CSR D2's
   physical layout; identify what CD command `0xC1` actually issues
   (Ghidra: `FUN_800c46d0` dispatch, cmd byte `0xC1`) to understand why it
   hangs on a D1-based single-disc image.
3. Possible fix directions once confirmed: strip/patch this specific
   `air0`/slot-3 block in the single-disc build's JUNAIR merge (similar in
   spirit to the CANON_2 fix in
   `docs/findings/2026-08-12-single-disc-canon2-akao-dskcg-strip.md`, but
   here it's genuinely new D2 content, not merge corruption — needs design
   review before stripping, since it may be intentional post-battle story
   content, e.g. new dialogue/party state (`PRTYE`) added by CSR D2).

## False leads (for future readers)

- Encounter table mismatch: **disproved**, tables identical byte-for-byte.
- SCENE.BIN D1 vs D2 mismatch: **disproved**, files identical byte-for-byte.
- Movie-relocation patch (`ship_movie_relocation_v010.py`): **ruled out** —
  freeze reproduces identically on the core build without that layer
  applied at all.
